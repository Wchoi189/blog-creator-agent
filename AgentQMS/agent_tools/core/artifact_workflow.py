#!/usr/bin/env python3
"""
AgentQMS Core Tools - Artifact Workflow Management
Provides functionality for creating, managing, and tracking artifacts throughout their lifecycle.
"""

import os
import sys
import argparse
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import json


class ArtifactWorkflow:
    """Manages the lifecycle of artifacts in the AgentQMS system."""

    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path or os.getcwd())
        self.templates_path = self.base_path / "AgentQMS" / "agent_interface" / "docs" / "artifacts" / "templates"
        self.artifacts_path = self.base_path / "docs"

    def create_artifact(self, artifact_type: str, name: str, title: str, **kwargs) -> str:
        """Create a new artifact from template."""
        template_file = self._find_template(artifact_type)
        if not template_file:
            raise ValueError(f"No template found for artifact type: {artifact_type}")

        # Generate frontmatter
        frontmatter = self._generate_frontmatter(artifact_type, title, **kwargs)

        # Read template content
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # Create artifact content
        content = f"---\n{frontmatter}---\n\n{template_content}"

        # Generate filename
        filename = self._generate_filename(artifact_type, name)
        filepath = self.artifacts_path / artifact_type.replace('_', '-') / filename

        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return str(filepath)

    def _find_template(self, artifact_type: str) -> Optional[Path]:
        """Find the appropriate template for the artifact type."""
        template_patterns = {
            'implementation_plan': '*blueprint*template*kpi*driven*',
            'assessment': '*assessment*',
            'component': '*component*',
            'user_guide': '*guide*'
        }

        pattern = template_patterns.get(artifact_type, f'*{artifact_type}*')
        templates = list(self.templates_path.glob(f'**/{pattern}.md'))

        return templates[0] if templates else None

    def _generate_frontmatter(self, artifact_type: str, title: str, **kwargs) -> str:
        """Generate YAML frontmatter for the artifact."""
        frontmatter = {
            'type': artifact_type,
            'category': kwargs.get('category', 'development'),
            'status': 'draft',
            'version': '1.0',
            'tags': kwargs.get('tags', [artifact_type.replace('_', '-')]),
            'title': title,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M (%Z)')
        }

        return yaml.dump(frontmatter, default_flow_style=False, allow_unicode=True).strip()

    def _generate_filename(self, artifact_type: str, name: str) -> str:
        """Generate a semantic filename for the artifact."""
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M')
        clean_name = name.lower().replace(' ', '_').replace('-', '_')
        return f"{timestamp}_{artifact_type}_{clean_name}.md"


def main():
    parser = argparse.ArgumentParser(description='AgentQMS Artifact Workflow Manager')
    parser.add_argument('action', choices=['create'], help='Action to perform')
    parser.add_argument('--type', required=True, help='Artifact type')
    parser.add_argument('--name', required=True, help='Artifact name')
    parser.add_argument('--title', required=True, help='Artifact title')
    parser.add_argument('--category', default='development', help='Artifact category')
    parser.add_argument('--tags', nargs='*', help='Artifact tags')

    args = parser.parse_args()

    workflow = ArtifactWorkflow()

    if args.action == 'create':
        try:
            filepath = workflow.create_artifact(
                args.type,
                args.name,
                args.title,
                category=args.category,
                tags=args.tags
            )
            print(f"✅ Artifact created: {filepath}")
        except Exception as e:
            print(f"❌ Error creating artifact: {e}")
            sys.exit(1)


if __name__ == '__main__':
    main()