#!/usr/bin/env python3
"""
AgentQMS Documentation Quality Assurance Tool
Comprehensive QA checks for documentation artifacts.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import Any


class DocumentationQA:
    """Quality assurance for AgentQMS documentation."""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path or Path.cwd())
        self.issues: dict[str, list[str]] = {}

    def run_full_qa(self) -> dict[str, Any]:
        """Run comprehensive QA checks."""
        results = {
            "total_files": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "issues": {},
            "summary": {}
        }

        # Find all documentation files
        doc_files = self._find_doc_files()

        for doc_file in doc_files:
            results["total_files"] += 1
            file_issues = self._check_file(doc_file)

            if file_issues:
                results["failed_checks"] += 1
                results["issues"][str(doc_file.relative_to(self.base_path))] = file_issues
            else:
                results["passed_checks"] += 1

        results["summary"] = self._generate_summary(results)
        return results

    def _find_doc_files(self) -> list[Path]:
        """Find all documentation files."""
        doc_files = []

        # Common documentation extensions
        extensions = ["*.md", "*.txt", "*.rst", "*.adoc"]

        for ext in extensions:
            doc_files.extend(self.base_path.rglob(ext))

        # Filter out files in unwanted directories
        filtered_files = []
        for doc_file in doc_files:
            if not self._should_skip_file(doc_file):
                filtered_files.append(doc_file)

        return filtered_files

    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        parts = file_path.parts
        return any(part.startswith(".") or part in ["node_modules", "__pycache__", ".git"] for part in parts)

    def _check_file(self, file_path: Path) -> list[str]:
        """Check a single documentation file."""
        issues = []

        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            # Check for required frontmatter
            if not self._has_frontmatter(content):
                issues.append("Missing YAML frontmatter")

            # Check frontmatter completeness
            frontmatter_issues = self._check_frontmatter(content)
            issues.extend(frontmatter_issues)

            # Check content quality
            content_issues = self._check_content_quality(content)
            issues.extend(content_issues)

            # Check formatting
            format_issues = self._check_formatting(content)
            issues.extend(format_issues)

        except Exception as e:
            issues.append(f"Error reading file: {e}")

        return issues

    def _has_frontmatter(self, content: str) -> bool:
        """Check if content has YAML frontmatter."""
        lines = content.split("\n")
        if len(lines) < 3:
            return False

        return lines[0].strip() == "---" and "---" in lines[1:]

    def _check_frontmatter(self, content: str) -> list[str]:
        """Check frontmatter completeness."""
        issues = []

        if not self._has_frontmatter(content):
            return issues

        # Extract frontmatter
        lines = content.split("\n")
        end_idx = -1
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == "---":
                end_idx = i
                break

        if end_idx == -1:
            return ["Invalid frontmatter format"]

        frontmatter_text = "\n".join(lines[1:end_idx])

        try:
            import yaml
            metadata = yaml.safe_load(frontmatter_text) or {}
        except Exception:
            return ["Invalid YAML in frontmatter"]

        # Required fields for AgentQMS artifacts
        required_fields = ["title", "type", "status"]
        for field in required_fields:
            if field not in metadata:
                issues.append(f"Missing required frontmatter field: {field}")

        # Check status values
        if "status" in metadata:
            valid_statuses = ["draft", "review", "approved", "published", "archived"]
            if metadata["status"] not in valid_statuses:
                issues.append(f"Invalid status value: {metadata['status']}")

        # Check type values
        if "type" in metadata:
            valid_types = [
                "implementation_plan", "assessment", "component",
                "user_guide", "template", "reference", "protocol"
            ]
            if metadata["type"] not in valid_types:
                issues.append(f"Invalid type value: {metadata['type']}")

        return issues

    def _check_content_quality(self, content: str) -> list[str]:
        """Check content quality."""
        issues = []

        # Check minimum length
        if len(content.strip()) < 100:
            issues.append("Content too short (minimum 100 characters)")

        # Check for TODO comments
        if "TODO" in content.upper():
            issues.append("Contains TODO comments")

        # Check for placeholder text
        placeholders = ["lorem ipsum", "placeholder", "tbd", "coming soon"]
        content_lower = content.lower()
        for placeholder in placeholders:
            if placeholder in content_lower:
                issues.append(f"Contains placeholder text: '{placeholder}'")

        # Check for broken links (basic check)
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        matches = re.findall(link_pattern, content)
        for _, url in matches:
            if url.startswith(("http://", "https://")):
                # Basic URL validation
                if not self._is_valid_url(url):
                    issues.append(f"Potentially invalid URL: {url}")

        return issues

    def _check_formatting(self, content: str) -> list[str]:
        """Check formatting issues."""
        issues = []

        lines = content.split("\n")

        # Check for trailing whitespace
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line:
                issues.append(f"Trailing whitespace on line {i}")

        # Check for multiple consecutive blank lines
        consecutive_blanks = 0
        for line in lines:
            if line.strip() == "":
                consecutive_blanks += 1
                if consecutive_blanks > 2:
                    issues.append("Multiple consecutive blank lines")
                    break
            else:
                consecutive_blanks = 0

        # Check markdown formatting
        if content.strip():
            # Should start with title
            if not lines[0].strip().startswith("# "):
                issues.append("Document should start with a level 1 heading")

        return issues

    def _is_valid_url(self, url: str) -> bool:
        """Basic URL validation."""
        # Simple regex for URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return url_pattern.match(url) is not None

    def _generate_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        """Generate QA summary."""
        total = results["total_files"]
        passed = results["passed_checks"]
        failed = results["failed_checks"]

        summary = {
            "total_files_checked": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": f"{(passed / total * 100):.1f}%" if total > 0 else "0%",
            "most_common_issues": self._get_common_issues(results["issues"])
        }

        return summary

    def _get_common_issues(self, issues: dict[str, list[str]]) -> list[dict[str, Any]]:
        """Get most common issues."""
        issue_counts = {}

        for file_issues in issues.values():
            for issue in file_issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Sort by frequency
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)

        return [
            {"issue": issue, "count": count}
            for issue, count in sorted_issues[:5]  # Top 5 issues
        ]


def main():
    parser = argparse.ArgumentParser(description="AgentQMS Documentation QA Tool")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    qa = DocumentationQA()

    try:
        results = qa.run_full_qa()

        if args.output == "json":
            import json
            print(json.dumps(results, indent=2))
        else:
            print("AgentQMS Documentation QA Results")
            print("=" * 50)
            print(f"Total files checked: {results['summary']['total_files_checked']}")
            print(f"Passed: {results['summary']['passed']}")
            print(f"Failed: {results['summary']['failed']}")
            print(f"Pass rate: {results['summary']['pass_rate']}")

            if results["issues"]:
                print("\nIssues found:")
                for file_path, file_issues in results["issues"].items():
                    print(f"\n{file_path}:")
                    for issue in file_issues:
                        print(f"  - {issue}")

                print("\nMost common issues:")
                for issue_info in results["summary"]["most_common_issues"]:
                    print(f"  - {issue_info['issue']}: {issue_info['count']} files")
            else:
                print("\n✅ All documentation passed QA checks!")

    except Exception as e:
        print(f"❌ Error during QA: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()