#!/usr/bin/env python3
"""
AgentQMS Discovery Tool
Discovers and catalogs all artifacts, tools, and resources in the AgentQMS system.
"""

import os
import sys
import json
from pathlib import Path
from typing import Dict, List, Any
import yaml


class AgentQMSDiscovery:
    """Discovers and catalogs AgentQMS components."""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.getcwd())
        self.agentqms_path = self.base_path / "AgentQMS"

    def discover_all(self) -> Dict[str, Any]:
        """Discover all components in the AgentQMS system."""
        return {
            "artifacts": self.discover_artifacts(),
            "tools": self.discover_tools(),
            "templates": self.discover_templates(),
            "handbook": self.discover_handbook(),
            "system_status": self.get_system_status()
        }

    def discover_artifacts(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover all artifacts organized by type."""
        artifacts_path = self.agentqms_path / "agent_interface" / "docs" / "artifacts"
        artifacts = {}

        if not artifacts_path.exists():
            return artifacts

        for artifact_dir in artifacts_path.iterdir():
            if artifact_dir.is_dir() and not artifact_dir.name.startswith('_'):
                artifact_type = artifact_dir.name.replace('-', '_')
                artifacts[artifact_type] = []

                for artifact_file in artifact_dir.glob("*.md"):
                    try:
                        metadata = self._extract_metadata(artifact_file)
                        artifacts[artifact_type].append({
                            "filename": artifact_file.name,
                            "path": str(artifact_file.relative_to(self.base_path)),
                            "metadata": metadata
                        })
                    except Exception as e:
                        print(f"Warning: Could not process {artifact_file}: {e}")

        return artifacts

    def discover_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """Discover all tools in the system."""
        tools = {
            "interface_tools": [],
            "automation_tools": []
        }

        # Interface tools
        interface_tools_path = self.agentqms_path / "agent_interface" / "tools"
        if interface_tools_path.exists():
            for tool_file in interface_tools_path.rglob("*.py"):
                tools["interface_tools"].append({
                    "name": tool_file.stem,
                    "path": str(tool_file.relative_to(self.base_path)),
                    "type": "interface"
                })

        # Automation tools
        automation_tools_path = self.agentqms_path / "agent_tools"
        if automation_tools_path.exists():
            for tool_file in automation_tools_path.rglob("*.py"):
                tools["automation_tools"].append({
                    "name": tool_file.stem,
                    "path": str(tool_file.relative_to(self.base_path)),
                    "type": "automation"
                })

        return tools

    def discover_templates(self) -> List[Dict[str, Any]]:
        """Discover all artifact templates."""
        templates_path = self.agentqms_path / "agent_interface" / "docs" / "artifacts" / "templates"
        templates = []

        if not templates_path.exists():
            return templates

        for template_file in templates_path.glob("*.md"):
            try:
                metadata = self._extract_metadata(template_file)
                templates.append({
                    "filename": template_file.name,
                    "path": str(template_file.relative_to(self.base_path)),
                    "metadata": metadata
                })
            except Exception as e:
                print(f"Warning: Could not process template {template_file}: {e}")

        return templates

    def discover_handbook(self) -> Dict[str, Any]:
        """Discover AI handbook structure."""
        handbook_path = self.agentqms_path / "docs" / "ai_handbook"
        handbook = {}

        if not handbook_path.exists():
            return handbook

        for section_dir in handbook_path.iterdir():
            if section_dir.is_dir():
                section_name = section_dir.name
                handbook[section_name] = []

                for doc_file in section_dir.rglob("*.md"):
                    handbook[section_name].append({
                        "filename": doc_file.name,
                        "path": str(doc_file.relative_to(self.base_path))
                    })

        return handbook

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        return {
            "agentqms_path": str(self.agentqms_path),
            "agentqms_exists": self.agentqms_path.exists(),
            "handbook_exists": (self.agentqms_path / "docs" / "ai_handbook").exists(),
            "tools_exist": (self.agentqms_path / "agent_tools").exists(),
            "interface_exists": (self.agentqms_path / "agent_interface").exists()
        }

    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown file."""
        metadata = {}
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if content.startswith('---'):
                end_pos = content.find('---', 3)
                if end_pos != -1:
                    frontmatter = content[3:end_pos].strip()
                    metadata = yaml.safe_load(frontmatter) or {}
        except Exception:
            pass

        return metadata


def main():
    import argparse

    parser = argparse.ArgumentParser(description='AgentQMS Discovery Tool')
    parser.add_argument('--output', choices=['json', 'text'], default='text',
                       help='Output format')
    parser.add_argument('--type', choices=['artifacts', 'tools', 'templates', 'handbook', 'all'],
                       default='all', help='Type of components to discover')

    args = parser.parse_args()

    discovery = AgentQMSDiscovery()

    if args.type == 'all':
        result = discovery.discover_all()
    elif args.type == 'artifacts':
        result = discovery.discover_artifacts()
    elif args.type == 'tools':
        result = discovery.discover_tools()
    elif args.type == 'templates':
        result = discovery.discover_templates()
    elif args.type == 'handbook':
        result = discovery.discover_handbook()

    if args.output == 'json':
        print(json.dumps(result, indent=2, default=str))
    else:
        print("AgentQMS Discovery Results")
        print("=" * 50)

        if args.type == 'all':
            print(f"System Status: {result['system_status']}")
            print(f"\nArtifacts Found: {sum(len(v) for v in result['artifacts'].values())}")
            print(f"Tools Found: {sum(len(v) for v in result['tools'].values())}")
            print(f"Templates Found: {len(result['templates'])}")
            print(f"Handbook Sections: {len(result['handbook'])}")
        else:
            print(json.dumps(result, indent=2, default=str))


if __name__ == '__main__':
    main()