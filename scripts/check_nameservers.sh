#!/usr/bin/env bash
set -euo pipefail

domain=${1:-}
expected_ns_file=${2:-}

if [[ -z "$domain" || -z "$expected_ns_file" ]]; then
  echo "Usage: $0 <domain> <expected_ns_file>" >&2
  exit 1
fi

if ! command -v dig >/dev/null 2>&1; then
  echo "dig command not found; install 'bind' or 'dnsutils' package" >&2
  exit 2
fi

if [[ ! -f "$expected_ns_file" ]]; then
  echo "Expected nameserver file not found: $expected_ns_file" >&2
  exit 3
fi

mapfile -t expected < <(grep -v '^#' "$expected_ns_file" | awk 'NF{print tolower($0)}' | sort)
if [[ ${#expected[@]} -eq 0 ]]; then
  echo "No expected nameservers found in file." >&2
  exit 4
fi

actual=( $(dig +short NS "$domain" | tr '[:upper:]' '[:lower:]' | sed 's/\.$//' | sort) )

if [[ ${#actual[@]} -eq 0 ]]; then
  echo "No NS records returned for $domain" >&2
  exit 5
fi

echo "Expected:" >&2
printf '  %s\n' "${expected[@]}" >&2

echo "Actual:" >&2
printf '  %s\n' "${actual[@]}" >&2

diff_output=$(comm -3 <(printf '%s\n' "${expected[@]}") <(printf '%s\n' "${actual[@]}")) || true

if [[ -n "$diff_output" ]]; then
  echo "Mismatch detected (left=expected only, right=actual only):" >&2
  echo "$diff_output" >&2
  exit 6
fi

echo "Nameserver delegation matches expected set." >&2
