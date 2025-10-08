SHELL := /bin/bash

init:
	terraform init -backend-config=backend.hcl

plan:
	terraform plan

apply:
	terraform apply -auto-approve

outputs:
	terraform output -json | jq

.PHONY: init plan apply outputs
