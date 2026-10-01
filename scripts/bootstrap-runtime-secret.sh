#!/usr/bin/env bash

NAMESPACE="$1"

kubectl create secret generic helpdesk-runtime \
  --namespace "$NAMESPACE" \
  --from-literal=DATABASE_NAME="$DATABASE_NAME" \
  --from-literal=DATABASE_USER="$DATABASE_USER" \
  --from-literal=DATABASE_PASSWORD="$DATABASE_PASSWORD" \
  --dry-run=client \
  -o yaml \
| kubectl apply -f -
