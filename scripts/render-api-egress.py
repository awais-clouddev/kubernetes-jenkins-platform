#!/usr/bin/env python3
import argparse
import ipaddress
import json
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("--kubeconfig", required=True)
parser.add_argument("--context", required=True)
args = parser.parse_args()
base = ["kubectl", "--kubeconfig", args.kubeconfig, "--context", args.context]

def get(*arguments):
    return json.loads(subprocess.check_output(
        base + ["get", *arguments, "-o", "json"], text=True
    ))

service = get("service", "kubernetes", "-n", "default")
slices = get("endpointslices", "-n", "default",
             "-l", "kubernetes.io/service-name=kubernetes")

targets = {
    (address, port["port"])
    for address in service["spec"].get("clusterIPs", [])
    for port in service["spec"]["ports"]
    if port.get("protocol", "TCP") == "TCP"
}
endpoints = {
    (address, port["port"])
    for item in slices["items"]
    for endpoint in item.get("endpoints", [])
    if endpoint.get("conditions", {}).get("ready") is True
    for address in endpoint["addresses"]
    for port in item.get("ports", [])
    if port.get("protocol", "TCP") == "TCP" and port.get("port")
}
if not targets or not endpoints:
    raise SystemExit("Missing Service addresses or ready API endpoints")

egress = []
for address, port in sorted(targets | endpoints):
    ip = ipaddress.ip_address(address)
    egress.append({
        "to": [{"ipBlock": {"cidr": f"{ip}/{ip.max_prefixlen}"}}],
        "ports": [{"protocol": "TCP", "port": port}],
    })

print(json.dumps({
    "apiVersion": "networking.k8s.io/v1",
    "kind": "NetworkPolicy",
    "metadata": {
        "name": "allow-deploy-agent-to-kubernetes-api",
        "namespace": "ci-deploy-agents",
    },
    "spec": {
        "podSelector": {},
        "policyTypes": ["Egress"],
        "egress": egress,
    },
}, indent=2))
