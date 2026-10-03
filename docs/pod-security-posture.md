# Project 6 Pod Security Posture

## Application namespaces
Staging and Production enforce Kubernetes Pod Security Restricted v1.37.

## Deployment agents
ci-deploy-agents enforces Restricted v1.37.

## Build agents
ci-build-agents uses Restricted v1.37. A restricted-compliant CI test Pod
was used to validate compatibility.

## Jenkins
Jenkins compatibility is tested separately from application namespaces.
Its namespace is not blindly forced to Restricted because vendor/chart
container requirements must be preserved.

## Observability
The observability namespace uses Restricted audit/warn posture before the
monitoring stack installation. Actual monitoring workloads will be validated
again during the observability phase.

## Envoy Gateway
Envoy Gateway uses a vendor-required privileged enforcement posture while
Restricted remains enabled for audit and warning visibility.

## BuildKit
BuildKit intentionally uses privileged enforcement because its build daemon
requires an exception from the Restricted application posture. Restricted
audit/warn remains enabled.
