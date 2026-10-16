#!/usr/bin/env python3
import argparse
import json
import uuid
from urllib.parse import urlencode
from urllib.request import Request, urlopen

parser = argparse.ArgumentParser()
parser.add_argument("--url", required=True)
parser.add_argument("--host", default="staging.helpdesk.local")
args = parser.parse_args()

def request(path, method="GET", payload=None):
    req = Request(
        args.url.rstrip("/") + path,
        data=None if payload is None else json.dumps(payload).encode(),
        method=method,
        headers={"Host": args.host, "Content-Type": "application/json"},
    )
    with urlopen(req, timeout=15) as response:
        body = response.read().decode()
        return json.loads(body) if path.startswith("/api/") else body

assert "<html" in request("/").lower(), "Frontend HTML missing"
for path in ("/app.js", "/style.css"):
    assert request(path).strip(), f"Empty frontend asset: {path}"
print("PASS: frontend HTML and assets")

health = request("/api/health")
assert health["database"] == health["redis"] == "connected", health
print("PASS: dependency health")

marker = "Smoke-" + uuid.uuid4().hex[:12]
ticket = request("/api/tickets", "POST", {
    "employee_name": marker,
    "issue": "Automated staging functional test",
    "priority": "High",
})
ticket_id = ticket["id"]

for priority in ("high", "High"):
    result = request("/api/tickets?" + urlencode({
        "search": marker, "priority": priority,
    }))
    assert any(t["id"] == ticket_id for t in result["tickets"])
print("PASS: create, read and filter casing")

updated = request(
    f"/api/tickets/{ticket_id}/status",
    "PATCH", {"status": "Resolved"},
)
assert updated["status"] == "Resolved"
result = request("/api/tickets?" + urlencode({
    "search": marker, "status": "resolved",
}))
assert any(
    t["id"] == ticket_id and t["status"] == "Resolved"
    for t in result["tickets"]
)
print("PASS: status update and verification")
print("STAGING_FUNCTIONAL_TEST=PASS")
