# ============================================================================
# Terraform Bootstrap Makefile
# ----------------------------------------------------------------------------
# Purpose: Manage creation of remote state backend (S3 + DynamoDB) locally,
# then migrate Terraform to use the remote backend.
# ----------------------------------------------------------------------------
# Usage (from repo root or this directory):
#   cd iac/bootstrap
#   make help
# ============================================================================

AWS_PROFILE ?= genai-immersion-houston
AWS_REGION  ?= us-west-2
BACKEND_CONFIG ?= backend.hcl
BACKEND_FILE ?= backend.tf
BUCKET ?= conflicto-tfstate
LOCK_TABLE ?= conflicto-terraform-locks
TF ?= terraform

# ----------------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------------
CHECK_TERRAFORM = if ! command -v $(TF) >/dev/null 2>&1; then \
		echo "❌ Terraform not installed. Install from https://developer.hashicorp.com/terraform/downloads"; \
		exit 1; \
	fi

# ----------------------------------------------------------------------------
# Phony targets
# ----------------------------------------------------------------------------
.PHONY: help init-local plan-local apply-local enable-backend plan apply validate-state state-ls lock-check destroy-bootstrap clean show backend-file-status

help:
	@echo "\nTerraform Bootstrap Makefile"
	@echo "================================"
	@echo "Variables (override with make VAR=value):"
	@echo "  AWS_PROFILE=$(AWS_PROFILE)"
	@echo "  AWS_REGION=$(AWS_REGION)"
	@echo "  BUCKET=$(BUCKET)"
	@echo "  LOCK_TABLE=$(LOCK_TABLE)"
	@echo "\nBootstrap Workflow:" \
		"\n  1) make init-local       # Local init (no backend yet)" \
		"\n  2) make plan-local       # Create local plan" \
		"\n  3) make apply-local      # Apply local plan (creates bucket+table)" \
		"\n  4) make enable-backend   # Create backend.tf & migrate state" \
		"\n  5) make plan             # Remote plan (now using S3 backend)" \
		"\n  6) make apply            # Apply using remote backend" \
		"\n  7) make validate-state   # Sanity checks" \
		"\nOptional:" \
		"\n  make destroy-bootstrap   # Tear down (only if not in use)" \
		"\n  make clean               # Remove local cache & state copies" \
		"\n  make backend-file-status # Shows whether backend.tf is present" \
		"\n"

# ----------------------------------------------------------------------------
# Local (pre-backend) phase
# ----------------------------------------------------------------------------
init-local:
	@$(CHECK_TERRAFORM)
	@if [ -f $(BACKEND_FILE) ]; then \
		echo "⚠️  $(BACKEND_FILE) exists. Remove it before local-only init if you want to recreate resources."; \
	else \
		echo "🚀 Initializing Terraform (LOCAL backend)..."; \
		$(TF) init; \
	fi

plan-local: init-local
	@echo "📝 Planning (LOCAL backend)..."
	$(TF) plan -out local.plan

apply-local:
	@echo "⚙️  Applying (LOCAL backend)..."
	@if [ ! -f local.plan ]; then \
		echo "⚠️  local.plan not found. Running plan first..."; \
		$(TF) plan -out local.plan; \
	fi
	$(TF) apply local.plan
	@echo "✅ Local apply complete. Next: make enable-backend"

# ----------------------------------------------------------------------------
# Backend migration phase
# ----------------------------------------------------------------------------
backend-file-status:
	@if [ -f $(BACKEND_FILE) ]; then \
		echo "✅ $(BACKEND_FILE) present (remote backend ready)."; \
	else \
		echo "❌ $(BACKEND_FILE) missing (still local backend)."; \
	fi

# Creates backend.tf if missing
$(BACKEND_FILE):
	@if [ -f $(BACKEND_FILE) ]; then \
		echo "ℹ️  $(BACKEND_FILE) already exists"; \
	else \
		echo "📝 Creating $(BACKEND_FILE) with S3 backend stub..."; \
		echo 'terraform {\n  backend "s3" {}\n}' > $(BACKEND_FILE); \
	fi

enable-backend: $(BACKEND_FILE)
	@$(CHECK_TERRAFORM)
	@if [ ! -f "$(BACKEND_CONFIG)" ]; then \
		echo "❌ $(BACKEND_CONFIG) not found. Create it first (see README)."; \
		exit 1; \
	fi
	@echo "🔄 Migrating state to S3 backend (bucket=$(BUCKET) table=$(LOCK_TABLE))..."
	# Force non-interactive by explicitly providing backend config values
	$(TF) init -migrate-state \
		-backend-config=bucket=$(BUCKET) \
		-backend-config=region=$(AWS_REGION) \
		-backend-config=profile=$(AWS_PROFILE) \
		-backend-config=dynamodb_table=$(LOCK_TABLE) \
		-backend-config=key=bootstrap/terraform.tfstate \
		-backend-config=encrypt=true \
		-backend-config=use_lockfile=true
	@echo "✅ Backend migration complete. You are now using remote state."

# ----------------------------------------------------------------------------
# Remote phase (after backend migration)
# ----------------------------------------------------------------------------
plan:
	@$(CHECK_TERRAFORM)
	@echo "📝 Planning (REMOTE backend)..."
	$(TF) plan -out remote.plan

apply:
	@echo "⚙️  Applying (REMOTE backend)..."
	@if [ ! -f remote.plan ]; then \
		echo "⚠️  remote.plan not found. Running plan first..."; \
		$(TF) plan -out remote.plan; \
	fi
	$(TF) apply remote.plan

validate-state:
	@echo "🔍 Validating remote state resources..."
	@echo "🪣 Checking bucket: $(BUCKET)"
	@aws s3 ls --profile $(AWS_PROFILE) | grep $(BUCKET) || { echo "❌ Bucket $(BUCKET) not found"; exit 1; }
	@echo "📄 Checking state object (may appear after first remote apply)..."
	@aws s3 ls s3://$(BUCKET)/ --profile $(AWS_PROFILE) | grep terraform.tfstate || echo "⚠️  terraform.tfstate not yet present (expected if no remote apply yet)"
	@echo "🔐 Checking DynamoDB lock table: $(LOCK_TABLE)"
	@aws dynamodb describe-table --table-name $(LOCK_TABLE) --profile $(AWS_PROFILE) >/dev/null && echo "✅ Lock table OK"
	@echo "✅ Validation done"

lock-check:
	@echo "🔍 Current lock entries (should usually be empty):"
	@aws dynamodb scan --table-name $(LOCK_TABLE) --profile $(AWS_PROFILE) --query 'Items' | grep LockID || echo "(none)"

# ----------------------------------------------------------------------------
# Destructive / Cleanup
# ----------------------------------------------------------------------------
# Only run destroy BEFORE other stacks depend on this backend.
# After migration and usage, destroying these resources will orphan or break state.
destroy-bootstrap:
	@read -p "⚠️  This will DESTROY the state bucket & lock table. Type 'destroy' to continue: " ans; \
	if [ "$$ans" != "destroy" ]; then echo "Aborted"; exit 1; fi
	$(TF) destroy
	@echo "✅ Destroy complete (ensure no dependent stacks existed)."

clean:
	@echo "🧹 Cleaning local Terraform artifacts..."
	rm -rf .terraform/ .terraform.lock.hcl *.plan terraform.tfstate* 2>/dev/null || true
	@echo "✅ Cleaned local state & cache"
