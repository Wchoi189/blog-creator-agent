#!/usr/bin/env python3
"""
AgentQMS Link Validator
Validates internal and external links in documentation artifacts.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    requests = None


class LinkValidator:
    """Validates links in AgentQMS documentation."""

    HTTP_SUCCESS_MAX = 400

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path or Path.cwd())
        self.broken_links: dict[str, list[str]] = {}
        self.checked_links: set[str] = set()
        self.external_timeout = 10

    def validate_all_links(self, check_external: bool = False) -> dict[str, Any]:
        """Validate all links in documentation."""
        results: dict[str, Any] = {
            "total_files": 0,
            "files_with_links": 0,
            "total_links": 0,
            "broken_internal_links": 0,
            "broken_external_links": 0,
            "broken_links": {},
            "errors": []
        }

        # Find all markdown files
        md_files = list(self.base_path.rglob("*.md"))

        for md_file in md_files:
            if self._should_skip_file(md_file):
                continue

            results["total_files"] += 1
            links = self._extract_links(md_file)

            if links:
                results["files_with_links"] += 1
                results["total_links"] += len(links)

                broken_in_file = self._validate_links_in_file(md_file, links, check_external)
                if broken_in_file:
                    results["broken_links"][str(md_file.relative_to(self.base_path))] = broken_in_file
                    results["broken_internal_links"] += len([link for link in broken_in_file if not link.startswith("http")])
                    results["broken_external_links"] += len([link for link in broken_in_file if link.startswith("http")])

        return results

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        # Skip files in hidden directories or specific directories
        parts = file_path.parts
        return any(part.startswith(".") or part in ["node_modules", "__pycache__", ".git"] for part in parts)

    def _extract_links(self, file_path: Path) -> list[str]:
        """Extract all links from a markdown file."""
        links = []

        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Find markdown links: [text](url)
            link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
            matches = re.findall(link_pattern, content)

            for _, url in matches:
                # Remove fragment identifiers
                clean_url = url.split("#")[0]
                if clean_url and clean_url not in links:
                    links.append(clean_url)

            # Find reference-style links
            ref_pattern = r"^\s*\[([^\]]+)\]:\s*(.+)$"
            for line in content.split("\n"):
                match = re.match(ref_pattern, line, re.MULTILINE)
                if match:
                    url = match.group(2).strip()
                    clean_url = url.split("#")[0]
                    if clean_url and clean_url not in links:
                        links.append(clean_url)

        except Exception as e:
            self.broken_links[str(file_path)] = [f"Error reading file: {e}"]

        return links

    def _validate_links_in_file(self, file_path: Path, links: list[str], check_external: bool) -> list[str]:
        """Validate links in a specific file."""
        broken = []

        for link in links:
            if link in self.checked_links:
                continue

            self.checked_links.add(link)

            if link.startswith(("http://", "https://")):
                if check_external and not self._validate_external_link(link):
                    broken.append(link)
            elif not self._validate_internal_link(file_path, link):
                broken.append(link)

        return broken

    def _validate_internal_link(self, file_path: Path, link: str) -> bool:
        """Validate an internal link."""
        # Handle relative paths
        if not link.startswith("/"):
            # Relative to the current file's directory
            target_path = (file_path.parent / link).resolve()
        else:
            # Absolute path from workspace root
            target_path = (self.base_path / link.lstrip("/")).resolve()

        # Try different extensions if none specified
        if not target_path.exists():
            if "." not in target_path.name:
                # Try adding .md extension
                if (target_path.parent / f"{target_path.name}.md").exists():
                    return True
                # Try adding .html extension
                if (target_path.parent / f"{target_path.name}.html").exists():
                    return True
            return False

        return target_path.exists()

    def _validate_external_link(self, url: str) -> bool:
        """Validate an external link."""
        try:
            response = requests.head(url, timeout=self.external_timeout, allow_redirects=True)
            return response.status_code < self.HTTP_SUCCESS_MAX
        except Exception:
            # Try GET request if HEAD fails
            try:
                response = requests.get(url, timeout=self.external_timeout, stream=True)
                return response.status_code < self.HTTP_SUCCESS_MAX
            except Exception:
                return False


def main():
    parser = argparse.ArgumentParser(description="AgentQMS Link Validator")
    parser.add_argument("--external", action="store_true", help="Check external links (slower)")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")
    parser.add_argument("--timeout", type=int, default=10, help="Timeout for external links")

    args = parser.parse_args()

    validator = LinkValidator()
    validator.external_timeout = args.timeout

    try:
        results = validator.validate_all_links(check_external=args.external)

        if args.output == "json":
            print(__import__("json").dumps(results, indent=2))
        else:
            print("AgentQMS Link Validation Results")
            print("=" * 50)
            print(f"Total files scanned: {results['total_files']}")
            print(f"Files with links: {results['files_with_links']}")
            print(f"Total links found: {results['total_links']}")
            print(f"Broken internal links: {results['broken_internal_links']}")
            print(f"Broken external links: {results['broken_external_links']}")

            if results["broken_links"]:
                print("\nBroken links by file:")
                for file_path, broken in results["broken_links"].items():
                    print(f"\n{file_path}:")
                    for link in broken:
                        print(f"  - {link}")
            else:
                print("\n✅ All links are valid!")

            if results["errors"]:
                print("\nErrors encountered:")
                for error in results["errors"]:
                    print(f"  - {error}")

    except Exception as e:
        print(f"❌ Error during link validation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
