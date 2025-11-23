# AI Agent Usage Guide: AST Integration System

**Document Type:** User Guide
**Creation Date:** 2025-11-06
**Last Updated:** 2025-11-06
**Version:** 1.0
**Author:** AI Agent
**Status:** Active

## Overview

This guide provides AI agents with comprehensive instructions for using the AST (Abstract Syntax Tree) Integration System in the Korean Grammar Correction project. The AST system enables automated code analysis, quality monitoring, test generation, and documentation extraction.

## System Architecture

The AST Integration System consists of:

- **Core Service** (`streamlit_app/services/ast_service/`): 4-module analysis engine
- **CLI Tool** (`scripts/ast_analysis_cli.py`): Command-line interface for analysis
- **Agent Wrapper** (`agent_interface/tools/ast_analysis.py`): AI agent interface
- **CI/CD Integration** (`.github/workflows/ast-analysis.yml`): Automated quality checks
- **Streamlit Components** (`streamlit_app/components/ast_visualizer.py`): Interactive visualizations

## Quick Start for AI Agents

### 1. Basic Code Analysis

```bash
# Analyze entire codebase
make ast-analyze

# Analyze specific file or directory
make ast-analyze TARGET=streamlit_app/services/ast_service/
```

### 2. Quality Assessment

```bash
# Check code quality across project
make ast-check-quality

# Check specific module quality
make ast-check-quality TARGET=streamlit_app/models/
```

### 3. Test Generation

```bash
# Generate test scaffolds for a module
make ast-generate-tests TARGET=streamlit_app/services/ast_service/analyzer.py
```

### 4. Documentation Extraction

```bash
# Extract documentation from code
make ast-extract-docs TARGET=streamlit_app/services/ast_service/
```

## Detailed Usage Patterns

### Code Analysis Capabilities

The AST system provides 31 analysis functions across 6 specialized classes:

#### ASTAnalyzer Class
- **File Analysis**: Parse Python files and extract structural information
- **Directory Analysis**: Recursively analyze entire codebases
- **Import Analysis**: Track dependencies and module relationships
- **Function/Method Analysis**: Extract signatures, parameters, and complexity

#### ComplexityVisitor Class
- **Cyclomatic Complexity**: Calculate code complexity metrics
- **Cognitive Complexity**: Assess code readability
- **Maintainability Index**: Evaluate code maintainability

#### CodeValidators Class
- **PEP 8 Compliance**: Check style guide adherence
- **Type Hint Validation**: Verify type annotations
- **Import Organization**: Validate import statement structure
- **Function Size Limits**: Enforce modularity constraints

#### CodeGenerators Class
- **Unit Test Scaffolds**: Generate pytest test templates
- **Mock Object Creation**: Generate test doubles
- **Fixture Generation**: Create pytest fixtures

#### DocumentationExtractor Class
- **Docstring Analysis**: Extract and validate docstrings
- **Function Documentation**: Generate API documentation
- **Module Documentation**: Create module-level docs

#### QualityReporter Class
- **Comprehensive Reports**: Generate detailed quality assessments
- **Violation Tracking**: Monitor code quality issues
- **Improvement Suggestions**: Provide actionable recommendations

### Integration with Development Workflow

#### Pre-commit Integration
The AST system integrates with pre-commit hooks for automatic quality checks:

```yaml
# .pre-commit-config.yaml (automatically configured)
repos:
  - repo: local
    hooks:
      - id: ast-quality-check
        name: AST Quality Check
        entry: python scripts/ast_analysis_cli.py check-quality
        language: system
        files: \.py$
        pass_filenames: false
```

#### CI/CD Pipeline Integration
GitHub Actions automatically run AST analysis on:
- Pull requests
- Pushes to main branch
- Manual workflow triggers

**Workflow Features:**
- Multi-stage analysis (linting → type checking → AST analysis)
- PR comments with analysis results
- Quality gate enforcement
- Performance benchmarking

### Streamlit Visualization Components

AI agents can leverage interactive visualizations:

#### ASTVisualizer Component
- **Code Structure Trees**: Interactive AST visualization
- **Complexity Heatmaps**: Visual complexity analysis
- **Quality Dashboards**: Real-time quality metrics
- **Dependency Graphs**: Module relationship visualization

#### Integration with Schema Engine
```python
# Component registration in schema engine
ast_visualizer_config = {
    "type": "ast_visualizer",
    "properties": {
        "target_path": "streamlit_app/services/",
        "analysis_type": "full",
        "visualization_mode": "interactive"
    }
}
```

## Best Practices for AI Agents

### 1. Analysis Strategy

#### Targeted Analysis
```bash
# Analyze specific problematic areas first
make ast-analyze TARGET=streamlit_app/components/

# Check quality before making changes
make ast-check-quality TARGET=streamlit_app/services/ast_service/
```

#### Incremental Analysis
```bash
# Generate tests for new modules
make ast-generate-tests TARGET=new_module.py

# Extract docs after implementation
make ast-extract-docs TARGET=completed_module.py
```

### 2. Quality Monitoring

#### Proactive Quality Checks
- Run `make ast-check-quality` before committing changes
- Use `make ast-analyze` to understand code structure before modifications
- Generate test scaffolds early in development

#### Issue Resolution
```bash
# Identify quality issues
make ast-check-quality

# Address specific violations
# - Fix import organization
# - Add type hints
# - Break down large functions
# - Add comprehensive docstrings
```

### 3. Test Generation Workflow

#### Automated Test Creation
```bash
# Generate test scaffold
make ast-generate-tests TARGET=streamlit_app/services/my_service.py

# Customize generated tests
# - Add specific test cases
# - Configure fixtures
# - Add edge case coverage
```

#### Test Quality Validation
- Ensure generated tests follow pytest conventions
- Validate test coverage meets project standards
- Integrate with existing test suite

### 4. Documentation Automation

#### Documentation Extraction
```bash
# Extract API documentation
make ast-extract-docs TARGET=streamlit_app/services/

# Generate module documentation
# - Function signatures
# - Parameter descriptions
# - Return value documentation
# - Usage examples
```

## Troubleshooting Guide

### Common Issues

#### Import Path Errors
**Problem:** Relative import issues in complex module hierarchies
**Solution:** Use absolute imports or properly configure PYTHONPATH

#### Module Size Violations
**Problem:** Functions or classes exceed size limits
**Solution:** Break down into smaller, focused components

#### Complexity Warnings
**Problem:** High cyclomatic complexity scores
**Solution:** Extract helper functions and simplify logic

#### Type Hint Missing
**Problem:** Missing type annotations
**Solution:** Add comprehensive type hints for all parameters and return values

### Performance Optimization

#### Analysis Speed
- Target analysis completes in <30 seconds for typical codebases
- Use targeted analysis for large codebases
- Cache results for repeated analyses

#### Memory Usage
- AST parsing is memory-efficient for Python codebases
- Large codebases may require incremental analysis
- Monitor memory usage for very large projects

## Integration Examples

### Development Workflow Integration

```bash
# Complete development cycle
make ast-analyze                    # Understand codebase
make ast-check-quality             # Validate quality
# Make code changes
make ast-generate-tests            # Generate tests
make ast-extract-docs              # Extract documentation
make ast-check-quality             # Final quality check
```

### CI/CD Integration Monitoring

```bash
# Monitor CI/CD pipeline
# - Check GitHub Actions workflow status
# - Review PR comments for analysis results
# - Address any quality gate failures
```

### Streamlit Component Usage

```python
# Using AST visualizer in Streamlit apps
from streamlit_app.components.ast_visualizer import ASTVisualizer

visualizer = ASTVisualizer()
visualizer.render_analysis_dashboard(
    target_path="streamlit_app/",
    analysis_depth="full"
)
```

## Advanced Features

### Custom Analysis Rules

The AST system supports extensible analysis rules:

#### Adding Custom Validators
```python
# Extend CodeValidators class
class CustomCodeValidators:
    def validate_custom_rules(self, node):
        # Implement custom validation logic
        pass
```

#### Custom Generators
```python
# Extend CodeGenerators class
class CustomCodeGenerators:
    def generate_custom_scaffolds(self, analysis_results):
        # Implement custom generation logic
        pass
```

### Integration with External Tools

#### IDE Integration
- VS Code extensions can leverage AST analysis
- Real-time quality feedback during development
- Automated refactoring suggestions

#### Documentation Systems
- Integration with Sphinx for API documentation
- Markdown generation for README files
- Automated changelog generation

## Metrics and Reporting

### Quality Metrics

The system tracks comprehensive quality metrics:

#### Code Quality Score
- Complexity analysis (0-100 scale)
- Maintainability index
- Test coverage estimation
- Documentation completeness

#### Analysis Performance
- Analysis speed (<30s target)
- Memory usage efficiency
- Accuracy rate (>90%)
- False positive/negative rates

### Reporting Formats

#### Console Output
- Real-time analysis results
- Color-coded severity levels
- Actionable recommendations

#### JSON Reports
- Structured data for automation
- Integration with CI/CD systems
- Historical trend analysis

#### HTML Visualizations
- Interactive dashboards
- Graphical complexity analysis
- Dependency relationship graphs

## Future Enhancements

### Planned Features

#### Machine Learning Integration
- Predictive quality analysis
- Automated refactoring suggestions
- Code pattern recognition

#### Multi-language Support
- Extension to other programming languages
- Cross-language dependency analysis
- Unified quality metrics

#### Advanced Visualizations
- 3D code structure visualization
- Real-time analysis dashboards
- Collaborative review tools

## Support and Resources

### Documentation Resources
- `docs/artifacts/2025-11-06_blueprint_ast-integration-implementation.md`: Implementation blueprint
- `docs/ai_handbook/`: AI agent development guidelines
- `streamlit_app/services/ast_service/`: Source code documentation

### Tool Integration
- Agent Makefile commands: `make ast-*`
- CLI tool: `python scripts/ast_analysis_cli.py`
- Streamlit components: Available in schema engine

### Getting Help
- Check existing artifacts in `agent/docs/artifacts/`
- Review implementation blueprint for detailed specifications
- Use `make discover` to explore available agent tools

---

**Document Maintenance:**
- Update this guide when new AST features are added
- Review annually for accuracy and completeness
- Maintain alignment with implementation blueprint specifications
