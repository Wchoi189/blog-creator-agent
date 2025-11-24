# Agent-Exclusive Makefile
# This Makefile is ONLY for AI agents - humans should not use these commands
# For human development, use the main project Makefile

.PHONY: help discover tools status clean validate compliance docs feedback quality audit

export PYTHONPATH := $(abspath ../..):$(PYTHONPATH)

# Default target - show help
help: ## Show agent help message
	@echo "🤖 Agent Tools Makefile (AGENT-ONLY)"
	@echo "====================================="
	@echo ""
	@echo "⚠️  WARNING: This Makefile is for AI agents only!"
	@echo "   Humans should use the main project Makefile."
	@echo ""
	@echo "📋 Available Agent Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "💡 Quick Start for Agents:"
	@echo "  make discover    - List all available tools"
	@echo "  make status      - Check system status"
	@echo "  make validate    - Validate all artifacts"
	@echo "  make compliance   - Check compliance status"
	@echo ""

# Discovery and Help
discover: ## Discover all available agent tools
	python ../toolkit/core/discover.py

tools: discover ## Alias for discover

status: ## Check overall system status
	@echo "🔍 Checking Agent Tools Status..."
	@echo ""
	@echo "📁 Tool Organization:"
	@ls -la ../toolkit/ | grep "^d" | awk '{print \"  \" $$9}'
	@echo ""
	@echo "🛠️ Agent Wrapper Scripts:"
	@ls -la ../*.sh 2>/dev/null | awk '{print "  " $$9}' || echo "  No wrapper scripts found"
	@echo ""
	@echo "📊 Recent Activity:"
	@find ../docs/artifacts -name "*.md" -mtime -1 2>/dev/null | head -5 | awk '{print "  " $$0}' || echo "  No recent artifacts"

# Artifact Management
create-plan: ## Create implementation plan (usage: make create-plan NAME=my-plan TITLE="My Plan")
	python ../toolkit/core/artifact_workflow.py create --type implementation_plan --name $(NAME) --title "$(TITLE)"

create-assessment: ## Create assessment (usage: make create-assessment NAME=my-assessment TITLE="My Assessment")
	python ../toolkit/core/artifact_workflow.py create --type assessment --name $(NAME) --title "$(TITLE)"

create-design: ## Create design document (usage: make create-design NAME=my-design TITLE="My Design")
	python ../toolkit/core/artifact_workflow.py create --type design --name $(NAME) --title "$(TITLE)"

create-research: ## Create research document (usage: make create-research NAME=my-research TITLE="My Research")
	python ../toolkit/core/artifact_workflow.py create --type research --name $(NAME) --title "$(TITLE)"

create-template: ## Create template (usage: make create-template NAME=my-template TITLE="My Template")
	python ../toolkit/core/artifact_workflow.py create --type template --name $(NAME) --title "$(TITLE)"

create-bug-report: ## Create bug report (usage: make create-bug-report NAME=my-bug TITLE="My Bug Report")
	python ../toolkit/core/artifact_workflow.py create --type bug_report --name $(NAME) --title "$(TITLE)"

# Validation and Compliance
validate: ## Validate all artifacts
	python ../toolkit/compliance/validate_artifacts.py --all

validate-file: ## Validate specific file (usage: make validate-file FILE=path/to/file.md)
	python ../toolkit/compliance/validate_artifacts.py --file $(FILE)

validate-naming: ## Check naming conventions only
	python ../toolkit/compliance/validate_artifacts.py --check-naming

boundary: ## Validate framework/project boundaries
	python ../toolkit/compliance/validate_boundaries.py

compliance: ## Check compliance status
	python ../toolkit/compliance/monitor_artifacts.py --check

compliance-fix: ## Fix compliance issues automatically (DEPRECATED)
	@echo "⚠️  compliance-fix is deprecated. No automated fixer is available." && exit 0

compliance-dashboard: ## Open enhanced compliance dashboard (DEPRECATED)
	@echo "⚠️  compliance-dashboard is deprecated. Use 'make compliance' for checks." && exit 0

# Documentation Management
docs-generate: ## Generate documentation index
	python ../toolkit/documentation/auto_generate_index.py --validate

docs-regenerate: ## Regenerate all documentation
	python ../toolkit/documentation/regenerate_docs.py

docs-update-indexes: ## Update artifact indexes
	python ../toolkit/documentation/update_artifact_indexes.py --all

docs-validate-links: ## Validate documentation links
	python ../toolkit/documentation/validate_links.py

docs-validate-manifest: ## Validate documentation manifest
	python ../toolkit/documentation/validate_manifest.py

docs-validate-metadata: ## Validate documentation metadata
	python ../toolkit/documentation/validate_metadata.py

# Context Bundles
context: ## Generate context bundle for task (usage: make context TASK="task description")
	@if [ -z "$(TASK)" ]; then \
		echo "ERROR: TASK parameter required. Usage: make context TASK=\"task description\""; \
		exit 1; \
	fi
	python ../toolkit/utilities/get_context.py --task "$(TASK)"

context-development: ## Get development context bundle
	python ../toolkit/utilities/get_context.py --type development

context-docs: ## Get documentation context bundle
	python ../toolkit/utilities/get_context.py --type documentation

context-debug: ## Get debugging context bundle
	python ../toolkit/utilities/get_context.py --type debugging

context-plan: ## Get planning context bundle
	python ../toolkit/utilities/get_context.py --type planning

context-list: ## List all available context bundles
	python ../toolkit/utilities/get_context.py --list-context-bundles

# Audit Framework Tools
audit-init: ## Initialize audit (usage: make audit-init FRAMEWORK="Framework Name" DATE="2025-11-09" SCOPE="Scope description")
	python ../toolkit/audit/audit_generator.py init \
		--framework-name "$(FRAMEWORK)" \
		--audit-date "$(DATE)" \
		--audit-scope "$(SCOPE)" \
		--output-dir "docs/audit"

audit-validate: ## Validate audit documents
	python ../toolkit/audit/audit_validator.py validate --audit-dir "docs/audit"

audit-checklist-generate: ## Generate checklist for phase (usage: make audit-checklist-generate PHASE="discovery")
	python ../toolkit/audit/checklist_tool.py generate \
		--phase "$(PHASE)" \
		--output "docs/audit/checklist_$(PHASE).md"

audit-checklist-report: ## Generate audit progress report
	python ../toolkit/audit/checklist_tool.py report --audit-dir "docs/audit"

docs-validate-templates: ## Validate documentation templates
	python ../toolkit/documentation/validate_templates.py

docs-validate-ui-schema: ## Validate UI schema documentation
	python ../toolkit/documentation/validate_ui_schema.py

docs-validate-ai: ## Validate AI documentation (DEPRECATED)
	@echo "⚠️  docs-validate-ai is deprecated. Use other docs-validate-* commands." && exit 0

# Feedback and Quality
feedback-report: ## Generate feedback report
	python ../toolkit/utilities/agent_feedback.py --report

feedback-issue: ## Report documentation issue (usage: make feedback-issue ISSUE="description" FILE="path")
	python ../toolkit/utilities/agent_feedback.py --issue "$(ISSUE)" --file "$(FILE)" --description "Agent reported issue"

feedback-suggest: ## Suggest improvement (usage: make feedback-suggest AREA="area" CURRENT="current" CHANGE="suggested" RATIONALE="reason")
	python ../toolkit/utilities/agent_feedback.py --suggest --area "$(AREA)" --current "$(CURRENT)" --change "$(CHANGE)" --rationale "$(RATIONALE)"

quality-check: ## Check documentation quality
	python ../toolkit/compliance/documentation_quality_monitor.py --report

quality-check-output: ## Check documentation quality and save to file
	python ../toolkit/compliance/documentation_quality_monitor.py --report --output logs/quality/quality_report_$(shell date +%Y%m%d_%H%M).md

ast-analyze: ## Run AST analysis on codebase (usage: make ast-analyze [TARGET=path/to/code])
	@if [ -n "$(TARGET)" ]; then \
		python ./cli_tools/ast_analysis.py analyze "$(TARGET)"; \
	else \
		python ./cli_tools/ast_analysis.py analyze; \
	fi

ast-generate-tests: ## Generate test scaffolds using AST analysis (usage: make ast-generate-tests TARGET=path/to/module.py)
	@if [ -z "$(TARGET)" ]; then \
		echo "ERROR: TARGET parameter required. Usage: make ast-generate-tests TARGET=path/to/module.py"; \
		exit 1; \
	fi
	python ./cli_tools/ast_analysis.py generate-tests "$(TARGET)"

ast-extract-docs: ## Extract documentation from code using AST (usage: make ast-extract-docs TARGET=path/to/module.py)
	@if [ -z "$(TARGET)" ]; then \
		echo "ERROR: TARGET parameter required. Usage: make ast-extract-docs TARGET=path/to/module.py"; \
		exit 1; \
	fi
	python ./cli_tools/ast_analysis.py extract-docs "$(TARGET)"

ast-check-quality: ## Check code quality using AST analysis (usage: make ast-check-quality [TARGET=path/to/code])
	@if [ -n "$(TARGET)" ]; then \
		python ./cli_tools/ast_analysis.py check-quality "$(TARGET)"; \
	else \
		python ./cli_tools/ast_analysis.py check-quality; \
	fi

# Context and Utilities
context-list: ## List available context bundles
	python ../toolkit/utilities/get_context.py --list-bundles

context-bundle: ## Get specific context bundle (usage: make context-bundle BUNDLE=bundle-name)
	python ../toolkit/utilities/get_context.py --bundle $(BUNDLE)

# Workflow Commands
workflow-create: ## Complete workflow: create artifact, validate, update indexes
	@echo "🚀 Starting complete artifact workflow..."
	@echo "📝 Creating artifact..."
	@echo "⚠️  Please specify TYPE, NAME, and TITLE:"
	@echo "   make workflow-create TYPE=implementation_plan NAME=my-plan TITLE=\"My Plan\""
	@if [ -z "$(TYPE)" ] || [ -z "$(NAME)" ] || [ -z "$(TITLE)" ]; then \
		echo "❌ Missing required parameters"; \
		exit 1; \
	fi
	python ../toolkit/core/artifact_workflow.py create --type $(TYPE) --name $(NAME) --title "$(TITLE)"
	@echo "✅ Artifact created"
	@echo "🔍 Validating artifact..."
	python ../toolkit/compliance/validate_artifacts.py --all
	@echo "📊 Updating indexes..."
	python ../toolkit/documentation/update_artifact_indexes.py --all
	@echo "🎉 Workflow completed successfully!"

workflow-validate: ## Complete validation workflow: validate, fix, monitor
	@echo "🔍 Starting validation workflow..."
	@echo "📋 Validating all artifacts..."
	python ../toolkit/compliance/validate_artifacts.py --all
	@echo "📊 Checking compliance status..."
	python ../toolkit/compliance/monitor_artifacts.py --check
	@echo "💡 Note: Automated compliance fixes are available via maintenance scripts"
	@echo "🎉 Validation workflow completed!"

workflow-docs: ## Complete documentation workflow: generate, validate, update
	@echo "📚 Starting documentation workflow..."
	@echo "🔄 Generating documentation index..."
	python ../toolkit/documentation/auto_generate_index.py --validate
	@echo "🔗 Validating documentation links..."
	python ../toolkit/documentation/validate_links.py
	@echo "📊 Updating artifact indexes..."
	python ../toolkit/documentation/update_artifact_indexes.py --all
	@echo "🎉 Documentation workflow completed!"

# Tracking (CLI-first)
track-init: ## Initialize tracking SQLite DB
	python ../toolkit/utilities/tracking/cli.py init

plan-new: ## Create plan (usage: make plan-new TITLE="..." OWNER="me" [KEY=slug])
	python ../toolkit/utilities/tracking/cli.py plan new --title "$(TITLE)" $(if $(OWNER),--owner "$(OWNER)",) $(if $(KEY),--key "$(KEY)",)

exp-new: ## Create experiment (usage: make exp-new TITLE="..." OBJECTIVE="..." OWNER="me" [KEY=slug])
	python ../toolkit/utilities/tracking/cli.py exp new --title "$(TITLE)" $(if $(OBJECTIVE),--objective "$(OBJECTIVE)",) $(if $(OWNER),--owner "$(OWNER)",) $(if $(KEY),--key "$(KEY)",)

exp-export: ## Export experiment runs to CSV (usage: make exp-export OUT=data/ops/experiment_runs.csv)
	@if [ -z "$(OUT)" ]; then \
		echo "ERROR: OUT parameter required. Example: make exp-export OUT=data/ops/experiment_runs.csv"; \
		exit 1; \
	fi
	python ../toolkit/utilities/tracking/cli.py exp export-runs --out "$(OUT)"

# Maintenance Commands
clean: ## Clean up temporary files and caches
	@echo "🧹 Cleaning up temporary files..."
	find .. -name "*.pyc" -delete
	find .. -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find .. -name "*.log" -delete
	@echo "✅ Cleanup completed"

clean-feedback: ## Clean up old feedback files
	@echo "🧹 Cleaning up old feedback files..."
	find logs/feedback -name "*.json" -mtime +30 -delete 2>/dev/null || true
	@echo "✅ Feedback cleanup completed"

# Development Commands
dev-setup: ## Setup development environment
	@echo "🛠️ Setting up development environment..."
	python -m pip install --upgrade pip
	pip install -r ../streamlit_app/requirements.txt
	@echo "✅ Development environment ready"

dev-test: ## Test all agent tools
	@echo "🧪 Testing agent tools..."
	python ../toolkit/core/discover.py
	python ../toolkit/core/artifact_workflow.py --help
	python ../toolkit/compliance/validate_artifacts.py --help
	python ../toolkit/documentation/auto_generate_index.py --help
	python ../toolkit/utilities/agent_feedback.py --help
	@echo "✅ All tools tested successfully"

# Information Commands
info-tools: ## Show detailed tool information
	@echo "🛠️ Agent Tools Information"
	@echo "========================="
	@echo ""
	@echo "📁 Core Tools:"
	@ls ../toolkit/core/*.py 2>/dev/null | sed 's/^/  /'
	@echo ""
	@echo "📁 Compliance Tools:"
	@ls ../toolkit/compliance/*.py 2>/dev/null | sed 's/^/  /'
	@echo ""
	@echo "📁 Documentation Tools:"
	@ls ../toolkit/documentation/*.py 2>/dev/null | sed 's/^/  /'
	@echo ""
	@echo "📁 Utility Tools:"
	@ls ../toolkit/utilities/*.py 2>/dev/null | sed 's/^/  /'

info-stats: ## Show project statistics
	@echo "📊 Project Statistics"
	@echo "====================="
	@echo ""
	@echo "📄 Total Artifacts:"
	@find ../docs/artifacts -name "*.md" 2>/dev/null | wc -l | sed 's/^/  /'
	@echo ""
	@echo "📁 Artifact Types:"
	@find ../docs/artifacts -name "*.md" 2>/dev/null | sed 's/.*\///' | sed 's/^[0-9-]*_[0-9-]*_//' | sed 's/_.*$$//' | sort | uniq -c | sort -nr | sed 's/^/  /' || echo "  No artifacts found"
	@echo ""
	@echo "📅 Recent Activity (last 7 days):"
	@find ../docs/artifacts -name "*.md" -mtime -7 2>/dev/null | wc -l | sed 's/^/  /'

# Quick Commands (most commonly used)
quick-help: help ## Quick help (alias for help)
quick-discover: discover ## Quick discover (alias for discover)
quick-validate: validate ## Quick validate (alias for validate)
quick-compliance: compliance ## Quick compliance check (alias for compliance)
quick-status: status ## Quick status check (alias for status)

# Catalog and Index Generation
tool-catalog: ## Generate tool catalog and scripts index
	python ../toolkit/utilities/generate_tool_catalog.py

# Export Framework
export: ## Export framework to project-agnostic package (usage: make export OUTPUT=export_package/)
	@if [ -z "$(OUTPUT)" ]; then \
		echo "ERROR: OUTPUT parameter required. Usage: make export OUTPUT=export_package/"; \
		exit 1; \
	fi
	python ../toolkit/utilities/export_framework.py --output "$(OUTPUT)" --project-root ..

export-dry-run: ## Dry run export (see what would be exported) (usage: make export-dry-run OUTPUT=export_package/)
	@if [ -z "$(OUTPUT)" ]; then \
		echo "ERROR: OUTPUT parameter required. Usage: make export-dry-run OUTPUT=export_package/"; \
		exit 1; \
	fi
	python ../toolkit/utilities/export_framework.py --output "$(OUTPUT)" --project-root .. --dry-run

export-validate: ## Export framework with validation (usage: make export-validate OUTPUT=export_package/)
	@if [ -z "$(OUTPUT)" ]; then \
		echo "ERROR: OUTPUT parameter required. Usage: make export-validate OUTPUT=export_package/"; \
		exit 1; \
	fi
	python ../toolkit.util

# Versioning and Deprecation
version-bump: ## Bump project version (usage: make version-bump VERSION=0.8.0 NOTES="..." DATE=YYYY-MM-DDTHH:MM:SSZ)
	@if [ -z "$(VERSION)" ]; then echo "ERROR: VERSION required"; exit 1; fi
	@DATE_VAL=$(if [ -n "$(DATE)" ]; then echo "$(DATE)"; else date -u +%Y-%m-%dT%H:%M:%SZ; fi); \
	echo "version: $(VERSION)" > ../project_version.yaml; \
	echo "release_date: $$DATE_VAL" >> ../project_version.yaml; \
	echo "notes: $(NOTES)" >> ../project_version.yaml; \
	echo "breaking_changes: []" >> ../project_version.yaml; \
	echo "Wrote ../project_version.yaml"

docs-deprecate: ## Deprecate docs based on project_version.yaml (add --dry-run with DRY_RUN=1)
	python ../toolkit/documentation/deprecate_docs.py $(if $(DRY_RUN),--dry-run,)
	python ../toolkit/documentation/update_artifact_indexes.py --all
	python ../toolkit/compliance/validate_artifacts.py --all

changelog-draft: ## Generate changelog draft from tracking DB and git log
	python ../toolkit/documentation/generate_changelog_draft.py

changelog-preview: ## Preview changelog draft without writing file
	python ../toolkit/documentation/generate_changelog_draft.py --preview

# All-in-one Commands
all-check: validate compliance quality-check ## Run all checks: validate, compliance, quality
all-docs: docs-generate docs-validate-links docs-update-indexes ## Run all documentation tasks
all-feedback: feedback-report quality-check ## Run all feedback and quality checks

# Emergency Commands
emergency-fix: compliance-fix docs-update-indexes ## Emergency: fix all issues and update indexes
emergency-reset: clean clean-feedback ## Emergency: reset and clean everything

# Show version and system info
version: ## Show system version information
	@echo "🤖 Agent Tools Makefile (AGENT-ONLY)"
	@echo "Version: 1.0"
	@echo "Date: $(shell date)"
	@echo "Python: $(shell python --version 2>/dev/null || echo 'Not available')"
	@echo "Make: $(shell make --version | head -1)"
	@echo "OS: $(shell uname -s 2>/dev/null || echo 'Unknown')"
	@echo ""
	@echo "⚠️  This Makefile is for AI agents only!"
	@echo "   Humans should use the main project Makefile."
