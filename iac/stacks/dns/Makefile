SHELL := /bin/bash

init:
	terraform init -backend-config=backend.hcl

import-zone:
	@if [ -z "$$ZONE_ID" ]; then echo "Usage: make import-zone ZONE_ID=Z123..."; exit 1; fi; \
	terraform import aws_route53_zone.root $$ZONE_ID

plan:
	terraform plan

apply:
	terraform apply -auto-approve

# Step 1: create only the certificate (needed because validation options are unknown until after creation)
apply-cert-only:
	terraform apply -auto-approve -target=aws_acm_certificate.app

# Step 2: after cert exists, run full apply to create validation records & finalize
apply-complete:
	terraform apply -auto-approve

outputs:
	terraform output -json | jq

refresh:
	terraform refresh

.PHONY: init import-zone plan apply outputs refresh
.PHONY: apply-cert-only apply-complete
