#!/usr/bin/env python3
"""
AgentQMS Documentation Index Generator
Automatically generates and updates index files for documentation artifacts.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


class IndexGenerator:
    """Generates index files for AgentQMS documentation."""

    def __init__(self, base_path: str | None = None):
        self.base_path = Path(base_path or Path.cwd())

    def generate_all_indexes(self, validate: bool = False) -> Any:
        """Generate all index files."""
        results = {}

        # Generate artifact indexes
        results["artifacts"] = self._generate_artifact_indexes()

        # Generate handbook index
        results["handbook"] = self._generate_handbook_index()

        # Generate template index
        results["templates"] = self._generate_template_index()

        if validate:
            results["validation"] = self._validate_indexes()

        return results

    def _generate_artifact_indexes(self) -> dict[str, Any]:
        """Generate indexes for artifacts."""
        artifacts_path = self.base_path / "AgentQMS" / "agent_interface" / "docs" / "artifacts"
        results: dict[str, Any] = {}

        if not artifacts_path.exists():
            return results

        for artifact_dir in artifacts_path.iterdir():
            if artifact_dir.is_dir() and not artifact_dir.name.startswith("_"):
                index_path = artifact_dir / "INDEX.md"
                artifacts = self._collect_artifacts(artifact_dir)

                if artifacts:
                    self._write_index_file(index_path, artifacts, artifact_dir.name)
                    results[artifact_dir.name] = len(artifacts)

        return results

    def _generate_handbook_index(self) -> int:
        """Generate handbook index."""
        handbook_path = self.base_path / "AgentQMS" / "docs" / "ai_handbook"

        if not handbook_path.exists():
            return 0

        index_path = handbook_path / "INDEX.md"
        sections = {}

        for section_dir in handbook_path.iterdir():
            if section_dir.is_dir():
                docs = list(section_dir.rglob("*.md"))
                sections[section_dir.name] = [
                    {
                        "title": self._extract_title(doc),
                        "path": str(doc.relative_to(handbook_path))
                    }
                    for doc in docs
                ]

        if sections:
            self._write_handbook_index(index_path, sections)

        return sum(len(docs) for docs in sections.values())

    def _generate_template_index(self) -> int:
        """Generate template index."""
        templates_path = self.base_path / "AgentQMS" / "agent_interface" / "docs" / "artifacts" / "templates"

        if not templates_path.exists():
            return 0

        index_path = templates_path / "INDEX.md"
        templates = []

        for template_file in templates_path.glob("*.md"):
            metadata = self._extract_metadata(template_file)
            templates.append({
                "filename": template_file.name,
                "title": metadata.get("title", template_file.stem),
                "type": metadata.get("type", "template"),
                "description": metadata.get("description", "")
            })

        if templates:
            self._write_template_index(index_path, templates)

        return len(templates)

    def _collect_artifacts(self, artifact_dir: Path) -> list[dict[str, Any]]:
        """Collect artifacts from a directory."""
        artifacts = []

        for artifact_file in artifact_dir.glob("*.md"):
            if artifact_file.name == "INDEX.md":
                continue

            metadata = self._extract_metadata(artifact_file)
            artifacts.append({
                "filename": artifact_file.name,
                "title": metadata.get("title", artifact_file.stem),
                "status": metadata.get("status", "unknown"),
                "date": metadata.get("date", "unknown"),
                "version": metadata.get("version", "unknown")
            })

        # Sort by date (newest first)
        artifacts.sort(key=lambda x: x["date"], reverse=True)
        return artifacts

    def _write_index_file(self, index_path: Path, artifacts: list[dict[str, Any]], category: str):
        """Write an index file for artifacts."""
        content = f"# {category.replace('_', ' ').title()} Index\n\n"
        content += f"Auto-generated index of {category} artifacts.\n\n"
        content += f"**Total Artifacts**: {len(artifacts)}\n\n"

        if artifacts:
            content += "| Title | Status | Date | Version |\n"
            content += "|-------|--------|------|--------|\n"

            for artifact in artifacts:
                title_link = f"[{artifact['title']}]({artifact['filename']})"
                content += f"| {title_link} | {artifact['status']} | {artifact['date']} | {artifact['version']} |\n"

        content += "\n---\n*Generated by AgentQMS Index Generator*"

        index_path.parent.mkdir(parents=True, exist_ok=True)
        with index_path.open("w", encoding="utf-8") as f:
            f.write(content)

    def _write_handbook_index(self, index_path: Path, sections: dict[str, list[dict[str, Any]]]):
        """Write handbook index."""
        content = "# AI Handbook Index\n\n"
        content += "Comprehensive index of AgentQMS AI Handbook documentation.\n\n"

        for section_name, docs in sections.items():
            section_title = section_name.replace("_", " ").title()
            content += f"## {section_title}\n\n"

            for doc in docs:
                content += f"- [{doc['title']}]({doc['path']})\n"

            content += "\n"

        content += "---\n*Generated by AgentQMS Index Generator*"

        with index_path.open("w", encoding="utf-8") as f:
            f.write(content)

    def _write_template_index(self, index_path: Path, templates: list[dict[str, Any]]):
        """Write template index."""
        content = "# Artifact Templates Index\n\n"
        content += "Available templates for creating new artifacts.\n\n"
        content += f"**Total Templates**: {len(templates)}\n\n"

        for template in templates:
            content += f"### {template['title']}\n"
            content += f"- **File**: `{template['filename']}`\n"
            content += f"- **Type**: {template['type']}\n"
            if template["description"]:
                content += f"- **Description**: {template['description']}\n"
            content += "\n"

        content += "---\n*Generated by AgentQMS Index Generator*"

        with index_path.open("w", encoding="utf-8") as f:
            f.write(content)

    def _extract_metadata(self, file_path: Path) -> dict[str, Any]:
        """Extract metadata from file."""
        metadata: dict[str, Any] = {}
        try:
            with file_path.open(encoding="utf-8") as f:
                content = f.read()

            if content.startswith("---"):
                end_pos = content.find("---", 3)
                if end_pos != -1:
                    frontmatter = content[3:end_pos].strip()
                    metadata = yaml.safe_load(frontmatter) or {}
        except Exception:
            pass

        return metadata

    def _extract_title(self, file_path: Path) -> str:
        """Extract title from file."""
        try:
            with file_path.open(encoding="utf-8") as f:
                for line_content in f:
                    stripped_line = line_content.strip()
                    if stripped_line.startswith("# "):
                        return stripped_line[2:]
        except Exception:
            pass

        return file_path.stem

    def _validate_indexes(self) -> dict[str, Any]:
        """Validate generated indexes."""
        # Basic validation - check if files exist and are readable
        validation_results: dict[str, Any] = {
            "valid_indexes": 0,
            "invalid_indexes": 0,
            "errors": []
        }

        index_files = [
            "AgentQMS/agent_interface/docs/artifacts/assessments/INDEX.md",
            "AgentQMS/agent_interface/docs/artifacts/components/INDEX.md",
            "AgentQMS/agent_interface/docs/artifacts/implementation_plans/INDEX.md",
            "AgentQMS/agent_interface/docs/artifacts/templates/INDEX.md",
            "AgentQMS/agent_interface/docs/artifacts/user-guides/INDEX.md",
            "AgentQMS/docs/ai_handbook/INDEX.md"
        ]

        for index_file in index_files:
            index_path = self.base_path / index_file
            if index_path.exists():
                try:
                    with index_path.open("r", encoding="utf-8") as f:
                        content = f.read()
                    if len(content.strip()) > 0:
                        validation_results["valid_indexes"] += 1
                    else:
                        validation_results["invalid_indexes"] += 1
                        validation_results["errors"].append(f"Empty index: {index_file}")
                except Exception as e:
                    validation_results["invalid_indexes"] += 1
                    validation_results["errors"].append(f"Error reading {index_file}: {e}")
            else:
                validation_results["invalid_indexes"] += 1
                validation_results["errors"].append(f"Missing index: {index_file}")

        return validation_results


def main():
    parser = argparse.ArgumentParser(description="AgentQMS Index Generator")
    parser.add_argument("--validate", action="store_true", help="Validate generated indexes")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    generator = IndexGenerator()

    try:
        results = generator.generate_all_indexes(validate=args.validate)

        if args.output == "json":
            print(json.dumps(results, indent=2, default=str))
        else:
            print("AgentQMS Index Generation Results")
            print("=" * 50)

            if "artifacts" in results:
                print(f"Artifact indexes generated: {len(results['artifacts'])} categories")
                for category, count in results["artifacts"].items():
                    print(f"  - {category}: {count} artifacts")

            if "handbook" in results:
                print(f"Handbook documents indexed: {results['handbook']}")

            if "templates" in results:
                print(f"Templates indexed: {results['templates']}")

            if "validation" in results:
                validation = results["validation"]
                print(f"Index validation: {validation['valid_indexes']} valid, {validation['invalid_indexes']} invalid")
                if validation["errors"]:
                    print("Errors:")
                    for error in validation["errors"]:
                        print(f"  - {error}")

            print("\n✅ Index generation completed!")

    except Exception as e:
        print(f"❌ Error during index generation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
