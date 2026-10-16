# Audit Verification — 16 October 2026

## Passed

- Four-node kind-jenkins-audit cluster started with Kubernetes v1.37.0.
- NetworkPolicy test: HTTP allowed, denied by policy, restored after removal.
- Revised API and frontend images built locally and loaded into kind.
- Staging: two API and two frontend replicas Ready; PostgreSQL and Redis Ready.
- PostgreSQL and Redis startup, readiness and liveness probes passed.
- Gateway served frontend HTML/assets and healthy dependency checks.
- Ticket creation, reading, filter casing and status updates passed.
- The reusable smoke test passed in a Restricted deploy-agent test Pod
  using the pinned Jenkins deploy-tools image.
- Deploy-agent direct PostgreSQL access timed out while gateway access worked.
- Discovered Kubernetes Service and endpoint API connections succeeded.
- A staging dump restored into a separate temporary database; three tickets
  were readable. Temporary database and dump were removed.

## Image identities

API:
sha256:5530e1b4856016240ecce64ab451927465f1aeb3c60111ff04dca3056308ec46

Frontend:
sha256:31e22b8eb0918bcf26c3ac375c9695ae0a9c029a7515cb2b7a73e4217f8f6182

These are local audit builds, not a newly verified registry release.

## Verification limits

The revised full Jenkins pipeline has not run. Its functional gate was
exercised independently in the equivalent deploy-tools test environment.
Fresh audit BuildKit certificates were generated and verified. BuildKit
became Ready and its local worker query succeeded. Jenkins completed plugin
initialization and its Pod became Ready.

Jenkins browser access/login and the revised full pipeline remain unverified.
Monitoring installation and complete setup-guide reproduction are deferred.

Production delivery, current alert firing/resolution, browser behavior,
live dependency-outage recovery and off-host disaster recovery were not
tested during this audit. HPA was disabled for the initial audit deployment.

The setup guide documents the intended sequence. Its certificate and
private-registry provisioning sections require operator preparation.
Historical evidence remains historical; documented lab limits are not
implemented production controls.
