#!/usr/bin/env bash
set -euo pipefail

# Simple validation script for the network stack.
# Requirements: aws cli, jq, terraform, correct AWS_PROFILE or credentials exported.
# Usage: from repo root (or anywhere): scripts/validate_network.sh

STACK_DIR="iac/stacks/network"
AWS_PROFILE_ARG=${AWS_PROFILE:+--profile $AWS_PROFILE}
AWS_REGION=${AWS_REGION:-us-west-2}

if ! command -v jq >/dev/null; then
  echo "ERROR: jq not installed" >&2; exit 1
fi
if ! command -v terraform >/dev/null; then
  echo "ERROR: terraform not installed" >&2; exit 1
fi

if [ ! -d "$STACK_DIR" ]; then
  echo "ERROR: Cannot find $STACK_DIR" >&2; exit 1
fi

# Grab outputs
VPC_ID=$(terraform -chdir=$STACK_DIR output -raw vpc_id 2>/dev/null || true)
if [ -z "$VPC_ID" ]; then
  echo "ERROR: Could not read vpc_id output. Did you run terraform apply?" >&2; exit 1
fi

PUBLIC_IDS=$(terraform -chdir=$STACK_DIR output -json public_subnet_ids | jq -r '.[]')
APP_IDS=$(terraform -chdir=$STACK_DIR output -json app_subnet_ids | jq -r '.[]')
DATA_IDS=$(terraform -chdir=$STACK_DIR output -json data_subnet_ids | jq -r '.[]')
ENDPOINT_IDS=$(terraform -chdir=$STACK_DIR output -json endpoint_subnet_ids | jq -r '.[]')

count_list () { echo "$1" | wc -w | tr -d ' '; }

PUB_COUNT=$(count_list "$PUBLIC_IDS")
APP_COUNT=$(count_list "$APP_IDS")
DATA_COUNT=$(count_list "$DATA_IDS")
ENDPT_COUNT=$(count_list "$ENDPOINT_IDS")

EXPECTED_TIER_COUNT=$PUB_COUNT  # expecting symmetrical across tiers

PASS=true

check_equal () {
  local label=$1; local actual=$2; local expected=$3
  if [ "$actual" != "$expected" ]; then
    echo "FAIL: $label count $actual != expected $expected"; PASS=false
  else
    echo "PASS: $label count = $actual"
  fi
}

echo "--- Subnet Counts ---"
check_equal "app" $APP_COUNT $EXPECTED_TIER_COUNT
check_equal "data" $DATA_COUNT $EXPECTED_TIER_COUNT
check_equal "endpoint" $ENDPT_COUNT $EXPECTED_TIER_COUNT

# NAT Gateways (expect 1 if single NAT strategy)
NAT_JSON=$(aws ec2 describe-nat-gateways --filter Name=vpc-id,Values=$VPC_ID --region $AWS_REGION $AWS_PROFILE_ARG)
NAT_COUNT=$(echo "$NAT_JSON" | jq '.NatGateways | length')
if [ "$NAT_COUNT" -eq 1 ]; then
  echo "PASS: NAT gateway count = 1"
else
  echo "WARN: Expected 1 NAT gateway, found $NAT_COUNT"
  PASS=false
fi

# Internet Gateway present
IGW_COUNT=$(aws ec2 describe-internet-gateways --filter Name=attachment.vpc-id,Values=$VPC_ID --region $AWS_REGION $AWS_PROFILE_ARG | jq '.InternetGateways | length')
if [ "$IGW_COUNT" -ge 1 ]; then
  echo "PASS: Internet Gateway attached"
else
  echo "FAIL: No Internet Gateway attached"; PASS=false
fi

# Route tables
RT_JSON=$(aws ec2 describe-route-tables --filters Name=vpc-id,Values=$VPC_ID --region $AWS_REGION $AWS_PROFILE_ARG)
PUBLIC_RT_IDS=$(echo "$RT_JSON" | jq -r '.RouteTables[] | select(.Routes[]? | select(.GatewayId? | startswith("igw-"))) | .RouteTableId')
if [ -n "$PUBLIC_RT_IDS" ]; then
  echo "PASS: Found public route table with IGW route"
else
  echo "FAIL: No public route table with 0.0.0.0/0 -> IGW route"; PASS=false
fi

# Private route table default route via NAT
if [ "$NAT_COUNT" -eq 1 ]; then
  PRIV_RT_IDS=$(echo "$RT_JSON" | jq -r '.RouteTables[] | select(.Routes[]? | select(.NatGatewayId?)) | .RouteTableId')
  if [ -n "$PRIV_RT_IDS" ]; then
    echo "PASS: Private route table has 0.0.0.0/0 -> NAT"
  else
    echo "FAIL: Missing private route table with NAT default route"; PASS=false
  fi
fi

# Summaries
if $PASS; then
  echo "\nOVERALL: PASS"
  exit 0
else
  echo "\nOVERALL: FAIL"
  exit 1
fi
