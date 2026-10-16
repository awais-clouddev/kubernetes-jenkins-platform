#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <namespace> <kubeconfig> <context>" >&2
  exit 1
fi

: "${DATABASE_NAME:?DATABASE_NAME must be set}"
: "${DATABASE_USER:?DATABASE_USER must be set}"
: "${DATABASE_PASSWORD:?DATABASE_PASSWORD must be set}"
export DATABASE_NAME DATABASE_USER DATABASE_PASSWORD

python3 - "$1" "$2" "$3" <<'PY'
import json
import os
import subprocess
import sys

namespace, kubeconfig, context = sys.argv[1:]
if namespace not in {"helpdesk-staging", "helpdesk-production"}:
    raise SystemExit("Unsupported application namespace")

secret = {
    "apiVersion": "v1",
    "kind": "Secret",
    "metadata": {"name": "helpdesk-runtime", "namespace": namespace},
    "type": "Opaque",
    "stringData": {
        key: os.environ[key]
        for key in ("DATABASE_NAME", "DATABASE_USER", "DATABASE_PASSWORD")
    },
}
subprocess.run([
    "kubectl", "--kubeconfig", kubeconfig, "--context", context,
    "create", "-f", "-",
], input=json.dumps(secret), text=True, check=True)
PY
