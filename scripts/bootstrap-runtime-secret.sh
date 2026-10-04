#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <namespace>" >&2
  exit 1
fi

NAMESPACE="$1"

: "${DATABASE_NAME:?DATABASE_NAME must be set}"
: "${DATABASE_USER:?DATABASE_USER must be set}"
: "${DATABASE_PASSWORD:?DATABASE_PASSWORD must be set}"

kubectl create secret generic helpdesk-runtime \
  --namespace "$NAMESPACE" \
  --from-literal=DATABASE_NAME="$DATABASE_NAME" \
  --from-literal=DATABASE_USER="$DATABASE_USER" \
  --from-literal=DATABASE_PASSWORD="$DATABASE_PASSWORD" \
  --dry-run=client \
  -o yaml \
| kubectl apply -f -
