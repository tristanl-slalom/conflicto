#!/usr/bin/env bash
set -euo pipefail

PROFILE="${1:-genai-immersion-houston}"
REGION="${AWS_REGION:-us-east-1}"

if ! command -v aws >/dev/null; then
  echo "aws CLI not installed" >&2; exit 1
fi

echo "[INFO] Performing AWS SSO login for profile: $PROFILE (region: $REGION)" >&2
aws sso login --profile "$PROFILE"

echo "[INFO] Verifying caller identity..." >&2
aws sts get-caller-identity --profile "$PROFILE" --output json

echo "[INFO] SSO login complete." >&2
