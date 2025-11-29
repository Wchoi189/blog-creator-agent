#!/usr/bin/env python3
"""
Artifact Validation Script for AI Agents

This script validates that artifacts follow the established naming conventions
and organizational structure defined in the project.

Supports extension via plugin system - see .agentqms/plugins/validators.yaml

Usage:
    python validate_artifacts.py --check-naming
    python validate_artifacts.py --file path/to/artifact.md
    python validate_artifacts.py --directory artifacts/
    python validate_artifacts.py --all
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from AgentQMS.agent_tools.utils.runtime import ensure_project_root_on_sys_path

ensure_project_root_on_sys_path()

from AgentQMS.agent_tools.compliance.validate_boundaries import BoundaryValidator

# Try to import context bundle functions for validation
try:
    from AgentQMS.agent_tools.core.context_bundle import (
        is_fresh,
        list_available_bundles,
        load_bundle_definition,
        validate_bundle_files,
    )

    CONTEXT_BUNDLES_AVAILABLE = True
except ImportError:
    CONTEXT_BUNDLES_AVAILABLE = False

# Try to import plugin registry for extensibility
try:
    from AgentQMS.agent_tools.core.plugins import get_plugin_registry

    PLUGINS_AVAILABLE = True
except ImportError:
    PLUGINS_AVAILABLE = False


def _assert_boundaries() -> None:
    violations = BoundaryValidator().validate()
    errors = [v for v in violations if v.severity == "error"]
    if errors:
        formatted = "\n".join(f"- {v.path}: {v.message}" for v in errors)
        raise RuntimeError(
            "Boundary validation failed. Resolve the following issues before running validators:\n"
            f"{formatted}"
        )


_assert_boundaries()


DATE_FORMAT = "%Y-%m-%d %H:%M (KST)"


class ArtifactValidator:
    """Validates artifacts against project naming conventions and structure.
    
    Supports extension via plugin system. Additional prefixes, types, categories,
    and statuses can be registered in .agentqms/plugins/validators.yaml
    """

    # Built-in defaults (always available)
    _BUILTIN_ARTIFACT_TYPES: Dict[str, str] = {
        "implementation_plan_": "docs/artifacts/implementation_plans/",
        "assessment-": "docs/artifacts/assessments/",
        "audit-": "docs/artifacts/audits/",
        "design-": "docs/artifacts/design_documents/",
        "research-": "docs/artifacts/research/",
        "template-": "docs/artifacts/templates/",
        "BUG_": "docs/artifacts/bug_reports/",
        "SESSION_": "docs/artifacts/completed_plans/completion_summaries/session_notes/",
    }

    _BUILTIN_TYPES: List[str] = [
        "implementation_plan",
        "assessment",
        "design",
        "research",
        "template",
        "bug_report",
        "session_note",
        "completion_summary",
    ]

    _BUILTIN_CATEGORIES: List[str] = [
        "development",
        "architecture",
        "evaluation",
        "compliance",
        "code_quality",
        "reference",
        "planning",
        "research",
        "troubleshooting",
    ]

    _BUILTIN_STATUSES: List[str] = [
        "active",
        "draft",
        "completed",
        "archived",
        "deprecated",
    ]

    def __init__(self, artifacts_root: str | Path | None = None):
        # Default to the configured artifacts directory if none is provided
        if artifacts_root is None:
            from AgentQMS.agent_tools.utils.paths import get_artifacts_dir

            self.artifacts_root = get_artifacts_dir()
        else:
            artifacts_root_path = Path(artifacts_root)
            if artifacts_root_path.is_absolute():
                self.artifacts_root = artifacts_root_path
            else:
                from AgentQMS.agent_tools.utils.paths import get_project_root
                self.artifacts_root = get_project_root() / artifacts_root_path

        self.violations = []

        # Start with builtin values
        self.valid_artifact_types = dict(self._BUILTIN_ARTIFACT_TYPES)
        self.valid_types = list(self._BUILTIN_TYPES)
        self.valid_categories = list(self._BUILTIN_CATEGORIES)
        self.valid_statuses = list(self._BUILTIN_STATUSES)

        # Extend with plugin-registered values
        self._load_plugin_extensions()

        # Required frontmatter fields
        self.required_frontmatter = [
            "title",
            "date",
            "type",
            "category",
            "status",
            "version",
        ]

    def _load_plugin_extensions(self) -> None:
        """Load additional validation rules from plugin registry."""
        if not PLUGINS_AVAILABLE:
            return

        try:
            registry = get_plugin_registry()
            validators = registry.get_validators()

            if not validators:
                return

            # Merge artifact types (plugin values override/extend builtin)
            if "prefixes" in validators:
                self.valid_artifact_types.update(validators["prefixes"])

            # Merge types (unique values)
            if "types" in validators:
                for t in validators["types"]:
                    if t not in self.valid_types:
                        self.valid_types.append(t)

            # Merge categories (unique values)
            if "categories" in validators:
                for c in validators["categories"]:
                    if c not in self.valid_categories:
                        self.valid_categories.append(c)

            # Merge statuses (unique values)
            if "statuses" in validators:
                for s in validators["statuses"]:
                    if s not in self.valid_statuses:
                        self.valid_statuses.append(s)

            # Also load prefixes from artifact type plugins
            artifact_types = registry.get_artifact_types()
            for name, type_def in artifact_types.items():
                validation = type_def.get("validation", {})
                prefix = validation.get("filename_prefix")
                directory = type_def.get("metadata", {}).get("directory")

                if prefix and directory:
                    self.valid_artifact_types[prefix] = directory

                # Add artifact type name to valid types
                if name not in self.valid_types:
                    self.valid_types.append(name)

        except Exception:
            # Plugin loading is non-critical - continue with builtins
            pass

    def validate_timestamp_format(
        self, filename: str
    ) -> tuple[bool, str, re.Match | None]:
        """Validate timestamp format in filename."""
        timestamp_pattern = r"^\d{4}-\d{2}-\d{2}_\d{4}_"
        match = re.match(timestamp_pattern, filename)
        valid = bool(match)
        msg = (
            "Valid timestamp format"
            if valid
            else "Missing or invalid timestamp format (expected: YYYY-MM-DD_HHMM_)"
        )
        match_result = match if valid else None
        return valid, msg, match_result

    def validate_naming_convention(self, file_path: Path) -> tuple[bool, str]:
        """Validate artifact naming convention."""
        filename = file_path.name

        # Check timestamp format
        valid, msg, match = self.validate_timestamp_format(filename)
        if not valid:
            return valid, msg

        after_timestamp = filename[match.end() :]

        # Check for valid artifact type after timestamp
        has_valid_artifact_type = any(
            after_timestamp.startswith(artifact_type) for artifact_type in self.valid_artifact_types
        )
        if not has_valid_artifact_type:
            valid_types_str = ", ".join(self.valid_artifact_types.keys())
            return (
                False,
                f"Missing valid artifact type. Valid artifact types: {valid_types_str}",
            )

        # Check for kebab-case in descriptive part
        # Extract the part after the artifact type
        for artifact_type in self.valid_artifact_types:
            if after_timestamp.startswith(artifact_type):
                descriptive_part = after_timestamp[len(artifact_type) : -3]  # Remove .md

                # Check for ALL CAPS or uppercase words (artifacts must be lowercase)
                if descriptive_part.isupper() or any(
                    word.isupper() and len(word) > 1
                    for word in descriptive_part.replace("-", "_").split("_")
                ):
                    return (
                        False,
                        "Artifact filenames must be lowercase. No ALL CAPS allowed. Use kebab-case (lowercase with hyphens)",
                    )

                if (
                    "_" in descriptive_part
                    and not descriptive_part.replace("-", "").replace("_", "").isalnum()
                ):
                    return (
                        False,
                        "Descriptive name should use kebab-case (hyphens, not underscores)",
                    )
                break

        return True, "Valid naming convention"

    def validate_directory_placement(self, file_path: Path) -> tuple[bool, str]:
        """Validate that file is in the correct directory."""
        filename = file_path.name
        relative_path = file_path.relative_to(self.artifacts_root)
        current_dir = str(relative_path.parent)

        # Check if file has a valid artifact type
        expected_dir = None
        for artifact_type, directory in self.valid_artifact_types.items():
            if filename.startswith(artifact_type):
                expected_dir = directory.rstrip("/")
                break

        if expected_dir and current_dir != expected_dir:
            return (
                False,
                f"File should be in '{expected_dir}/' directory, currently in '{current_dir}/'",
            )

        return True, "Correct directory placement"

    def validate_frontmatter(self, file_path: Path) -> tuple[bool, str]:
        """Validate frontmatter structure and content."""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            return False, f"Error reading file: {e}"

        # Check for frontmatter
        if not content.startswith("---"):
            return False, "Missing frontmatter (file should start with '---')"

        # Extract frontmatter
        frontmatter_end = content.find("---", 3)
        if frontmatter_end == -1:
            return False, "Malformed frontmatter (missing closing '---')"

        frontmatter_content = content[3:frontmatter_end]

        # Parse frontmatter (simple YAML-like parsing)
        frontmatter = {}
        for line in frontmatter_content.split("\n"):
            line = line.strip()
            if ":" in line and not line.startswith("#"):
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                frontmatter[key] = value

        # Check required fields
        missing_fields = []
        for field in self.required_frontmatter:
            if field not in frontmatter:
                missing_fields.append(field)

        if missing_fields:
            return (
                False,
                f"Missing required frontmatter fields: {', '.join(missing_fields)}",
            )

        # Validate field values
        validation_errors = []

        date_value = frontmatter.get("date", "").strip()
        if date_value:
            try:
                datetime.strptime(date_value, DATE_FORMAT)
            except ValueError:
                validation_errors.append(
                    "Date must use 'YYYY-MM-DD HH:MM (KST)' format (24-hour clock)."
                )

        if "type" in frontmatter and frontmatter["type"] not in self.valid_types:
            validation_errors.append(
                f"Invalid type '{frontmatter['type']}'. Valid types: {', '.join(self.valid_types)}"
            )

        if (
            "category" in frontmatter
            and frontmatter["category"] not in self.valid_categories
        ):
            validation_errors.append(
                f"Invalid category '{frontmatter['category']}'. Valid categories: {', '.join(self.valid_categories)}"
            )

        if "status" in frontmatter and frontmatter["status"] not in self.valid_statuses:
            validation_errors.append(
                f"Invalid status '{frontmatter['status']}'. Valid statuses: {', '.join(self.valid_statuses)}"
            )

        if validation_errors:
            return False, "; ".join(validation_errors)

        return True, "Valid frontmatter"

    def validate_single_file(self, file_path: Path) -> dict:
        """Validate a single artifact file."""
        # Resolve relative paths to absolute
        if not file_path.is_absolute():
            file_path = file_path.resolve()
            
        result = {"file": str(file_path), "valid": True, "errors": []}

        # Skip INDEX.md files
        if file_path.name == "INDEX.md":
            return result

        # Validate naming convention
        naming_valid, naming_msg = self.validate_naming_convention(file_path)
        if not naming_valid:
            result["valid"] = False
            result["errors"] += [f"Naming: {naming_msg}"]

        # Validate directory placement
        dir_valid, dir_msg = self.validate_directory_placement(file_path)
        if not dir_valid:
            result["valid"] = False
            result["errors"] += [f"Directory: {dir_msg}"]

        # Validate frontmatter
        frontmatter_valid, frontmatter_msg = self.validate_frontmatter(file_path)
        if not frontmatter_valid:
            result["valid"] = False
            result["errors"] += [f"Frontmatter: {frontmatter_msg}"]

        return result

    def validate_directory(self, directory: Path) -> list[dict]:
        """Validate all markdown files in a directory."""
        results = []

        if not directory.exists():
            return [
                {
                    "file": str(directory),
                    "valid": False,
                    "errors": ["Directory does not exist"],
                }
            ]

        for file_path in directory.rglob("*.md"):
            if file_path.is_file():
                result = self.validate_single_file(file_path)
                results.append(result)

        return results

    def validate_all(self) -> list[dict]:
        """Validate all artifacts in the artifacts directory."""
        results = []

        # Validate all artifacts in subdirectories
        for subdirectory in self.artifacts_root.iterdir():
            if subdirectory.is_dir() and not subdirectory.name.startswith("_"):
                results.extend(self.validate_directory(subdirectory))

        # Add bundle validation results if available
        if CONTEXT_BUNDLES_AVAILABLE:
            bundle_results = self.validate_bundles()
            results.extend(bundle_results)

        return results

    def validate_bundles(self) -> list[dict]:
        """
        Validate context bundle definitions.

        Checks:
        - All bundle definition files exist and are valid YAML
        - All files referenced in bundles exist
        - All bundle files are fresh (modified within last 30 days)

        Returns:
            List of validation result dictionaries
        """
        if not CONTEXT_BUNDLES_AVAILABLE:
            return []

        results = []

        try:
            # Get project root using utility function
            from AgentQMS.agent_tools.utils.paths import get_project_root
            project_root = get_project_root()

            available_bundles = list_available_bundles()

            for bundle_name in available_bundles:
                # Determine bundle file path (framework or plugin)
                framework_bundle_path = project_root / "AgentQMS" / "knowledge" / "context_bundles" / f"{bundle_name}.yaml"
                plugin_bundle_path = project_root / ".agentqms" / "plugins" / "context_bundles" / f"{bundle_name}.yaml"

                if framework_bundle_path.exists():
                    bundle_file_display = f"AgentQMS/knowledge/context_bundles/{bundle_name}.yaml"
                elif plugin_bundle_path.exists():
                    bundle_file_display = f".agentqms/plugins/context_bundles/{bundle_name}.yaml"
                else:
                    bundle_file_display = f"context_bundles/{bundle_name}.yaml"

                bundle_result = {
                    "file": bundle_file_display,
                    "valid": True,
                    "errors": [],
                    "warnings": [],
                }

                try:
                    # Load bundle definition
                    bundle_def = load_bundle_definition(bundle_name)

                    # Validate bundle files
                    validate_bundle_files(bundle_def)

                    # Check for missing files
                    tiers = bundle_def.get("tiers", {})

                    for tier_key, tier in tiers.items():
                        tier_files = tier.get("files", [])
                        for file_spec in tier_files:
                            if isinstance(file_spec, str):
                                file_path_str = file_spec
                                is_optional = False
                            elif isinstance(file_spec, dict):
                                file_path_str = file_spec.get("path", "")
                                is_optional = file_spec.get("optional", False)
                            else:
                                continue

                            # Skip glob patterns (handled by validate_bundle_files)
                            if "*" in file_path_str or "**" in file_path_str:
                                continue

                            # Check if file exists
                            file_path = project_root / file_path_str
                            if not file_path.exists():
                                if is_optional:
                                    # Optional files don't fail validation
                                    bundle_result["warnings"].append(
                                        f"Optional file missing in {bundle_name} bundle: {file_path_str}"
                                    )
                                else:
                                    bundle_result["valid"] = False
                                    bundle_result["errors"].append(
                                        f"Missing file in {bundle_name} bundle: {file_path_str}"
                                    )
                            elif not is_fresh(file_path, days=30):
                                bundle_result["warnings"].append(
                                    f"Stale file in {bundle_name} bundle: {file_path_str} "
                                    "(not modified in last 30 days)"
                                )

                except FileNotFoundError:
                    bundle_result["valid"] = False
                    bundle_result["errors"].append(
                        f"Bundle definition file not found: {bundle_name}.yaml"
                    )
                except Exception as e:
                    bundle_result["valid"] = False
                    bundle_result["errors"].append(
                        f"Error validating bundle {bundle_name}: {e!s}"
                    )

                results.append(bundle_result)

        except Exception as e:
            # Add error result if bundle system fails
            results.append(
                {
                    "file": "context_bundles/",
                    "valid": False,
                    "errors": [f"Error validating bundles: {e!s}"],
                    "warnings": [],
                }
            )

        return results

    def generate_report(self, results: list[dict]) -> str:
        """Generate a validation report."""
        total_files = len(results)
        valid_files = sum(1 for r in results if r["valid"])
        invalid_files = total_files - valid_files

        report = []
        report.append("=" * 60)
        report.append("ARTIFACT VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Total files: {total_files}")
        report.append(f"Valid files: {valid_files}")
        report.append(f"Invalid files: {invalid_files}")
        report.append(
            f"Compliance rate: {(valid_files / total_files * 100):.1f}%"
            if total_files > 0
            else "N/A"
        )
        report.append("")

        if invalid_files > 0:
            report.append("VIOLATIONS FOUND:")
            report.append("-" * 40)
            for result in results:
                if not result["valid"]:
                    report.append(f"\n❌ {result['file']}")
                    for error in result["errors"]:
                        report.append(f"   • {error}")

        if valid_files > 0:
            report.append("\n✅ VALID FILES:")
            report.append("-" * 40)
            for result in results:
                if result["valid"]:
                    report.append(f"✓ {result['file']}")

        return "\n".join(report)

    def fix_suggestions(self, results: list[dict]) -> str:
        """Generate fix suggestions for invalid files."""
        suggestions = []
        suggestions.append("FIX SUGGESTIONS:")
        suggestions.append("=" * 40)

        for result in results:
            if not result["valid"]:
                suggestions.append(f"\n📁 {result['file']}")
                for error in result["errors"]:
                    if "Naming:" in error:
                        suggestions.append("   🔧 Rename file to follow convention:")
                        suggestions.append(
                            "      Format: YYYY-MM-DD_HHMM_[PREFIX]_descriptive-name.md"
                        )
                    elif "Directory:" in error:
                        suggestions.append("   🔧 Move file to correct directory")
                    elif "Frontmatter:" in error:
                        suggestions.append("   🔧 Add or fix frontmatter:")
                        suggestions.append(
                            "      Required fields: title, date, type, category, status, version"
                        )

        return "\n".join(suggestions)


def main():
    """Main entry point for the validation script."""
    parser = argparse.ArgumentParser(
        description="Validate artifact naming conventions and structure"
    )
    parser.add_argument("--file", help="Validate a specific file")
    parser.add_argument("--directory", help="Validate all files in a directory")
    parser.add_argument("--all", action="store_true", help="Validate all artifacts")
    parser.add_argument(
        "--check-naming", action="store_true", help="Check naming conventions only"
    )
    parser.add_argument(
        "--artifacts-root",
        default=None,
        help="Root directory for artifacts",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Validate only staged artifact files (for pre-commit/CI hooks)",
    )
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument(
        "--json", action="store_true", help="Output results in JSON format"
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Files to validate (positional arguments, for pre-commit hooks)",
    )

    args = parser.parse_args()

    validator = ArtifactValidator(args.artifacts_root)

    if args.files:
        # Handle positional arguments (from pre-commit hooks passing explicit files)
        results = []
        for file_path_str in args.files:
            file_path = Path(file_path_str)
            if file_path.is_file():
                results.append(validator.validate_single_file(file_path))
            elif file_path.is_dir():
                results.extend(validator.validate_directory(file_path))
    elif args.staged:
        # Validate only staged files under the artifacts root (git required)
        import subprocess

        rel_artifacts_root = Path(args.artifacts_root)
        results = []

        try:
            completed = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                check=False,
                capture_output=True,
                text=True,
            )
            for line in (completed.stdout or "").splitlines():
                path = Path(line.strip())
                if not path.suffix.lower() == ".md":
                    continue
                # Only validate files within the artifacts tree
                try:
                    path.relative_to(rel_artifacts_root)
                except ValueError:
                    continue
                if path.exists():
                    results.append(validator.validate_single_file(path))
        except Exception as exc:  # pragma: no cover - defensive fallback
            print(f"⚠️  Failed to determine staged files; falling back to --all: {exc}")
            results = validator.validate_all()
    elif args.file:
        file_path = Path(args.file)
        results = [validator.validate_single_file(file_path)]
    elif args.directory:
        dir_path = Path(args.directory)
        results = validator.validate_directory(dir_path)
    elif args.all:
        results = validator.validate_all()
    else:
        # Default: validate all
        results = validator.validate_all()

    if args.json:
        output = json.dumps(results, indent=2)
    else:
        output = validator.generate_report(results)
        if any(not r["valid"] for r in results):
            output += "\n\n" + validator.fix_suggestions(results)

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    # Exit with error code if violations found
    if any(not r["valid"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
