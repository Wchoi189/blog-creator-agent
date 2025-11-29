#!/usr/bin/env python3
"""
Safe autofix pipeline: apply validator suggestions with limits.
Consumes validation JSON, performs git mv, updates indexes and links.
"""
import sys
import argparse
import json
import subprocess
import re
from pathlib import Path
from typing import List, Dict, Any

def run_git_command(cmd: List[str], dry_run: bool = False) -> bool:
    """Execute git command, optionally in dry-run mode."""
    if dry_run:
        print(f"  [dry-run] git {' '.join(cmd)}")
        return True
    try:
        result = subprocess.run(["git"] + cmd, check=True, capture_output=True, text=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"  ❌ git command failed: {e.stderr}")
        return False

def extract_suggestions_from_violations(violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Parse validation violations and extract actionable rename/move suggestions."""
    suggestions = []
    
    for item in violations:
        if item.get("valid"):
            continue
        
        file_path = Path(item["file"])
        errors = item.get("errors", [])
        
        for error in errors:
            # Parse naming violations for renames
            if "Missing or invalid timestamp" in error or "Missing valid artifact type" in error:
                # Suggest rename based on pattern
                suggestion = {
                    "type": "rename",
                    "source": str(file_path),
                    "target": None,  # To be computed based on rules
                    "reason": error
                }
                suggestions.append(suggestion)
            
            # Parse directory violations for moves
            elif "Directory:" in error:
                match = re.search(r"should be in '([^']+)' directory", error)
                if match:
                    target_dir = match.group(1)
                    suggestion = {
                        "type": "move",
                        "source": str(file_path),
                        "target_dir": target_dir,
                        "reason": error
                    }
                    suggestions.append(suggestion)
    
    return suggestions

def apply_fixes(suggestions: List[Dict[str, Any]], limit: int, dry_run: bool, project_root: Path) -> int:
    """Apply fixes with limit."""
    applied = 0
    
    for i, suggestion in enumerate(suggestions[:limit]):
        if suggestion["type"] == "move":
            source = Path(suggestion["source"])
            target_dir = project_root / "docs" / "artifacts" / suggestion["target_dir"]
            target = target_dir / source.name
            
            print(f"\n{i+1}. Move: {source.name}")
            print(f"   From: {source.parent}")
            print(f"   To:   {target_dir}")
            
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
            
            if run_git_command(["mv", str(source), str(target)], dry_run):
                applied += 1
        
        elif suggestion["type"] == "rename":
            # For now, just report (actual rename logic requires pattern detection)
            print(f"\n{i+1}. Rename needed: {suggestion['source']}")
            print(f"   Reason: {suggestion['reason']}")
    
    return applied

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Safe autofix pipeline for artifacts")
    parser.add_argument("--limit", type=int, default=10, help="Max fixes to apply")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, no changes")
    parser.add_argument("--commit", action="store_true", help="Auto-commit changes")
    parser.add_argument("--validation-json", help="Path to validation JSON output")
    
    args = parser.parse_args()
    
    from AgentQMS.agent_tools.utils.paths import get_project_root
    project_root = get_project_root()
    
    # Run validation to get current state
    if args.validation_json and Path(args.validation_json).exists():
        with open(args.validation_json) as f:
            violations = json.load(f)
    else:
        print("🔍 Running validation...")
        from AgentQMS.agent_tools.compliance.validate_artifacts import ArtifactValidator
        validator = ArtifactValidator()
        violations = validator.validate_all()
    
    # Extract actionable suggestions
    suggestions = extract_suggestions_from_violations(violations)
    
    if not suggestions:
        print("✅ No fixes needed")
        return 0
    
    print(f"\n📋 Found {len(suggestions)} potential fixes")
    print(f"   Applying up to {args.limit} fixes {'(DRY RUN)' if args.dry_run else ''}")
    
    # Apply fixes
    applied = apply_fixes(suggestions, args.limit, args.dry_run, project_root)
    
    print(f"\n✨ Applied {applied} fixes")
    
    if not args.dry_run and args.commit and applied > 0:
        print("\n📝 Committing changes...")
        run_git_command(["add", "-A"], False)
        run_git_command(["commit", "-m", f"AgentQMS: autofix {applied} artifacts"], False)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
