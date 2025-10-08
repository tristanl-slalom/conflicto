SHELL := /bin/bash

init:
	terraform init -backend-config=backend.hcl

plan:
	terraform plan

apply:
	terraform apply -auto-approve

outputs:
	terraform output -json | jq

refresh:
	terraform refresh

.PHONY: init plan apply outputs refresh
