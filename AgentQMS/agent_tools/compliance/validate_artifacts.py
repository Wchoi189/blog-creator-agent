#!/usr/bin/env python3
"""
AgentQMS Artifact Validation Tool
Validates artifacts for compliance with AgentQMS standards and protocols.
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import yaml


class ArtifactValidator:
    """Validates AgentQMS artifacts for compliance."""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.getcwd())
        self.errors = []
        self.warnings = []

    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """Validate all artifacts in the system."""
        artifacts_path = self.base_path / "docs"

        if not artifacts_path.exists():
            self.errors.append("docs/ directory not found")
            return False, self.errors, self.warnings

        for artifact_dir in artifacts_path.iterdir():
            if artifact_dir.is_dir():
                self._validate_directory(artifact_dir)

        return len(self.errors) == 0, self.errors, self.warnings

    def validate_file(self, file_path: str) -> Tuple[bool, List[str], List[str]]:
        """Validate a specific artifact file."""
        path = Path(file_path)
        if not path.exists():
            self.errors.append(f"File not found: {file_path}")
            return False, self.errors, self.warnings

        self._validate_artifact_file(path)
        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_directory(self, dir_path: Path):
        """Validate all artifacts in a directory."""
        for file_path in dir_path.glob("*.md"):
            self._validate_artifact_file(file_path)

    def _validate_artifact_file(self, file_path: Path):
        """Validate a single artifact file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check frontmatter
            self._validate_frontmatter(file_path, content)

            # Check content structure
            self._validate_content_structure(file_path, content)

            # Check naming conventions
            self._validate_naming(file_path)

        except Exception as e:
            self.errors.append(f"Error reading {file_path}: {e}")

    def _validate_frontmatter(self, file_path: Path, content: str):
        """Validate YAML frontmatter."""
        if not content.startswith('---'):
            self.errors.append(f"{file_path}: Missing YAML frontmatter")
            return

        end_pos = content.find('---', 3)
        if end_pos == -1:
            self.errors.append(f"{file_path}: Invalid frontmatter format")
            return

        frontmatter_text = content[3:end_pos].strip()
        try:
            metadata = yaml.safe_load(frontmatter_text) or {}
        except yaml.YAMLError as e:
            self.errors.append(f"{file_path}: Invalid YAML in frontmatter: {e}")
            return

        # Required fields
        required_fields = ['type', 'category', 'status', 'version', 'title', 'date']
        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"{file_path}: Missing required field '{field}' in frontmatter")

        # Validate field values
        if 'type' in metadata:
            valid_types = ['implementation_plan', 'assessment', 'component', 'user_guide', 'template']
            if metadata['type'] not in valid_types:
                self.errors.append(f"{file_path}: Invalid type '{metadata['type']}'. Must be one of: {valid_types}")

        if 'status' in metadata:
            valid_statuses = ['draft', 'active', 'deprecated', 'archived']
            if metadata['status'] not in valid_statuses:
                self.errors.append(f"{file_path}: Invalid status '{metadata['status']}'. Must be one of: {valid_statuses}")

    def _validate_content_structure(self, file_path: Path, content: str):
        """Validate content structure and formatting."""
        lines = content.split('\n')

        # Check for proper heading hierarchy
        headings = []
        for line in lines:
            if line.startswith('#'):
                level = len(line.split()[0])
                headings.append(level)

        # Headings should be in proper order (no skipping levels)
        for i in range(1, len(headings)):
            if headings[i] > headings[i-1] + 1:
                self.warnings.append(f"{file_path}: Heading level skips (#{headings[i-1]} to #{headings[i]})")

        # Check for code blocks (should be properly closed)
        in_code_block = False
        for i, line in enumerate(lines):
            if line.startswith('```'):
                in_code_block = not in_code_block
            elif in_code_block and line.startswith('#'):
                self.warnings.append(f"{file_path}:{i+1}: Heading inside code block")

        if in_code_block:
            self.errors.append(f"{file_path}: Unclosed code block")

    def _validate_naming(self, file_path: Path):
        """Validate file and content naming conventions."""
        filename = file_path.name

        # Check for semantic naming (not just timestamps)
        if re.match(r'^\d{4}-\d{2}-\d{2}_\d{4}_', filename):
            # Timestamp-based naming is allowed but not preferred
            pass
        elif not re.match(r'^[a-z0-9_-]+\.md$', filename):
            self.warnings.append(f"{file_path}: Filename should use lowercase with hyphens/underscores")

        # Check file extension
        if not filename.endswith('.md'):
            self.errors.append(f"{file_path}: File must have .md extension")


def main():
    parser = argparse.ArgumentParser(description='AgentQMS Artifact Validator')
    parser.add_argument('--all', action='store_true', help='Validate all artifacts')
    parser.add_argument('--file', help='Validate specific file')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    validator = ArtifactValidator()

    if args.file:
        success, errors, warnings = validator.validate_file(args.file)
    elif args.all:
        success, errors, warnings = validator.validate_all()
    else:
        parser.print_help()
        sys.exit(1)

    # Output results
    if errors:
        print("❌ Validation Errors:")
        for error in errors:
            print(f"  {error}")

    if warnings:
        print("\n⚠️  Validation Warnings:")
        for warning in warnings:
            print(f"  {warning}")

    if success:
        print("\n✅ All validations passed!")
        sys.exit(0)
    else:
        print(f"\n❌ Validation failed: {len(errors)} errors, {len(warnings)} warnings")
        sys.exit(1)


if __name__ == '__main__':
    main()