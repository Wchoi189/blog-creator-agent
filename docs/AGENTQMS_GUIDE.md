# AgentQMS Framework Guide

## Overview

AgentQMS (Quality Management System) is a comprehensive framework for managing AI agent development, artifact creation, and quality assurance in the Blog Creator Agent migration project.

## Core Components

### 1. Agent Interface (`AgentQMS/agent_interface/`)
The command-line interface for AgentQMS operations.

**Key Directories**:
- `docs/artifacts/` - Quality-controlled documentation artifacts
- `tools/` - Automation scripts and utilities
- `workflows/` - Standardized processes and scripts

### 2. Agent Tools (`AgentQMS/agent_tools/`)
Automation tools for development workflow.

**Categories**:
- `compliance/` - Quality validation and compliance checking
- `core/` - Core framework functionality
- `documentation/` - Documentation generation and management

### 3. AI Handbook (`AgentQMS/docs/ai_handbook/`)
Comprehensive protocols and guidelines for AI agents.

**Structure**:
- `01_introduction/` - Framework overview
- `02_protocols/` - Development and operational protocols
- `03_references/` - Technical references and guides

## Getting Started

### Installation
```bash
# Ensure Python 3.8+ is available
python --version

# Install dependencies (if needed)
pip install -r requirements.txt
```

### Basic Usage
```bash
cd AgentQMS/agent_interface

# Discover available tools
make discover

# Check system status
make status

# Validate all artifacts
make validate
```

## Artifact Management

### Creating Artifacts
```bash
# Create implementation plan
make create-plan

# Create technical assessment
make create-assessment

# Create design document
make create-design
```

### Artifact Types
- **Implementation Plans**: Detailed development roadmaps
- **Assessments**: Technical analysis and evaluations
- **Components**: Reusable code and configuration
- **User Guides**: Documentation for end users
- **Templates**: Standardized document templates

### Validation Process
```bash
# Validate specific file
make validate-file FILE=path/to/artifact.md

# Validate all artifacts
make validate

# Check compliance
make compliance
```

## Development Workflow

### 1. Planning Phase
```bash
# Create implementation plan
make create-plan

# Validate plan structure
make validate-file FILE=docs/plans/new_plan.md
```

### 2. Development Phase
```bash
# Regular validation during development
make validate

# Check compliance status
make compliance
```

### 3. Review Phase
```bash
# Final validation before commit
make validate

# Generate compliance report
make compliance
```

## Quality Standards

### Frontmatter Requirements
All artifacts must include YAML frontmatter:

```yaml
---
type: "implementation_plan"
category: "development"
status: "active"
version: "1.0"
tags: ['migration', 'frontend', 'nextjs']
title: "Part 2: Frontend Development"
date: "2025-11-23 20:15 (KST)"
---
```

### Naming Conventions
- **Files**: `semantic_name.md` (no timestamps)
- **Directories**: `snake_case`
- **Types**: Predefined artifact types only

### Content Standards
- **Structure**: Consistent heading hierarchy
- **Formatting**: Markdown with proper syntax
- **References**: Internal links use relative paths
- **Completeness**: All sections must be filled

## Automation Tools

### Discovery Tools
```bash
# List all available tools
python AgentQMS/agent_tools/core/discover.py

# Find artifacts by type
python AgentQMS/agent_tools/core/discover.py --type implementation_plan
```

### Quality Tools
```bash
# Validate artifact compliance
python AgentQMS/agent_tools/compliance/validate_artifacts.py --file path/to/file.md

# Auto-fix formatting issues
python AgentQMS/agent_tools/compliance/auto_fix.py --file path/to/file.md
```

### Documentation Tools
```bash
# Generate index files
python AgentQMS/agent_tools/documentation/auto_generate_index.py

# Validate links
python AgentQMS/agent_tools/documentation/validate_links.py
```

## Protocols and Guidelines

### Development Protocols
Located in `AgentQMS/docs/ai_handbook/02_protocols/development/`

**Key Protocols**:
- **Coding Standards**: Language-specific best practices
- **Testing Requirements**: Test coverage and methodology
- **Documentation Standards**: Artifact creation guidelines
- **Review Process**: Code and artifact review procedures

### Operational Protocols
Located in `AgentQMS/docs/ai_handbook/02_protocols/operational/`

**Key Protocols**:
- **Artifact Management**: Creation, validation, and maintenance
- **Quality Assurance**: Testing and validation procedures
- **Change Management**: Modification and update processes
- **Compliance Monitoring**: Ongoing quality monitoring

## Integration with Project

### Project Structure
```
blog-creator-agent/
├── AgentQMS/              # Quality management framework
├── docs/
│   ├── plans/            # Implementation plans (AgentQMS-managed)
│   └── assessments/      # Technical assessments (AgentQMS-managed)
├── src/                  # Source code
└── tests/                # Test suites
```

### Workflow Integration
1. **Planning**: Use AgentQMS to create structured implementation plans
2. **Development**: Follow AgentQMS coding and documentation standards
3. **Validation**: Regular AgentQMS compliance checks
4. **Review**: AgentQMS validation before commits

## Troubleshooting

### Common Issues

#### Validation Failures
```bash
# Check validation errors
make validate-file FILE=path/to/file.md

# View detailed error report
python AgentQMS/agent_tools/compliance/validate_artifacts.py --file path/to/file.md --verbose
```

#### Tool Not Found
```bash
# Update tool permissions
chmod +x AgentQMS/agent_interface/tools/*

# Check Python path
python -c "import sys; print(sys.path)"
```

#### Permission Issues
```bash
# Fix file permissions
chmod -R 755 AgentQMS/

# Check ownership
ls -la AgentQMS/
```

### Getting Help

#### Documentation Resources
- **AI Handbook**: `AgentQMS/docs/ai_handbook/`
- **Tool Documentation**: `AgentQMS/agent_interface/README.md`
- **Protocol Guides**: `AgentQMS/docs/ai_handbook/02_protocols/`

#### Support Channels
- **Framework Issues**: Check AgentQMS issue tracker
- **Project Issues**: Use project communication channels
- **Technical Questions**: Consult team documentation

## Best Practices

### For AI Agents
1. **Always validate** artifacts before committing
2. **Follow protocols** from the AI Handbook
3. **Use automation tools** for repetitive tasks
4. **Document decisions** and rationale
5. **Regular compliance checks** during development

### For Human Developers
1. **Review AgentQMS validations** before merging
2. **Follow established patterns** in the handbook
3. **Use framework tools** for artifact creation
4. **Contribute improvements** to the framework
5. **Stay updated** with protocol changes

## Framework Evolution

### Version Control
- **Semantic Versioning**: Major.Minor.Patch
- **Backward Compatibility**: Maintained across minor versions
- **Migration Guides**: Provided for major version changes

### Contributing to AgentQMS
1. **Follow contribution guidelines** in the handbook
2. **Test changes thoroughly** before submission
3. **Document new features** comprehensively
4. **Maintain backward compatibility** when possible

### Future Enhancements
- **AI Integration**: Enhanced AI agent capabilities
- **Extended Tooling**: Additional automation features
- **Protocol Expansion**: New domains and use cases
- **Performance Optimization**: Faster validation and processing

---

## Quick Reference

### Essential Commands
```bash
# Core operations
make discover              # List available tools
make status               # Check system status
make validate             # Validate all artifacts
make compliance           # Check compliance status

# Artifact creation
make create-plan          # Create implementation plan
make create-assessment    # Create technical assessment

# Quality assurance
make validate-file FILE=path/to/file.md
python AgentQMS/agent_tools/compliance/validate_artifacts.py --all
```

### Key Locations
- **Framework Root**: `AgentQMS/`
- **AI Handbook**: `AgentQMS/docs/ai_handbook/`
- **Tools**: `AgentQMS/agent_tools/`
- **Artifacts**: `docs/` (plans, assessments, etc.)

### Contact Information
- **Framework Documentation**: `AgentQMS/docs/ai_handbook/`
- **Tool Help**: `make help` or `python tool_name.py --help`
- **Protocol Questions**: Check relevant handbook sections

---

**Framework Version**: 1.0
**Last Updated**: November 2025
**Documentation**: AgentQMS AI Handbook