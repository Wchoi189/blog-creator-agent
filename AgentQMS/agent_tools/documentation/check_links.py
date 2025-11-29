#!/usr/bin/env python3
"""
Check Markdown links: verify artifact references are valid.
Scans docs/** for [text](path) links and validates targets exist.
"""
import sys
import re
from pathlib import Path
from typing import List, Tuple

def extract_markdown_links(file_path: Path) -> List[Tuple[int, str, str]]:
    """Extract [text](url) links from markdown file. Returns (line_num, text, url)."""
    links = []
    try:
        content = file_path.read_text(encoding="utf-8")
        for i, line in enumerate(content.split("\n"), 1):
            for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
                text, url = match.groups()
                links.append((i, text, url))
    except Exception:
        pass
    return links

def resolve_link(source_file: Path, link_url: str) -> Path | None:
    """Resolve relative markdown link to absolute path."""
    # Skip external URLs, anchors, mailto
    if any(link_url.startswith(p) for p in ["http://", "https://", "#", "mailto:"]):
        return None
    
    # Handle fragment-only anchors
    if link_url.startswith("#"):
        return None
    
    # Remove fragment if present
    if "#" in link_url:
        link_url = link_url.split("#")[0]
    
    if not link_url:
        return None
    
    # Resolve relative to source file's directory
    target = (source_file.parent / link_url).resolve()
    return target

def main():
    """Main entry point."""
    from AgentQMS.agent_tools.utils.paths import get_project_root
    
    project_root = get_project_root()
    docs_dir = project_root / "docs"
    
    if not docs_dir.exists():
        print("❌ docs/ directory not found")
        return 1
    
    print(f"🔍 Checking links in {docs_dir}")
    
    broken_links = []
    checked_files = 0
    total_links = 0
    
    for md_file in docs_dir.rglob("*.md"):
        if ".git" in str(md_file):
            continue
        
        checked_files += 1
        links = extract_markdown_links(md_file)
        
        for line_num, text, url in links:
            total_links += 1
            target = resolve_link(md_file, url)
            
            if target is None:
                # External or anchor link, skip
                continue
            
            if not target.exists():
                rel_source = md_file.relative_to(project_root)
                broken_links.append({
                    "file": str(rel_source),
                    "line": line_num,
                    "text": text,
                    "url": url,
                    "resolved": str(target.relative_to(project_root)) if project_root in target.parents else str(target)
                })
    
    print(f"\n📊 Checked {checked_files} files, {total_links} links")
    
    if broken_links:
        print(f"\n❌ Found {len(broken_links)} broken links:\n")
        for link in broken_links:
            print(f"  {link['file']}:{link['line']}")
            print(f"    [{link['text']}]({link['url']})")
            print(f"    ⚠️  Target not found: {link['resolved']}\n")
        return 1
    else:
        print("\n✅ All links valid")
        return 0

if __name__ == "__main__":
    sys.exit(main())
