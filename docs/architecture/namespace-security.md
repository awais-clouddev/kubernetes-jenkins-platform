# Namespace Pod Security Posture

| Namespace | Target posture |
|---|---|
| helpdesk-staging | Restricted |
| helpdesk-production | Restricted |
| ci-deploy-agents | Restricted |
| ci-build-agents | Restricted where compatible; validate later |
| jenkins | Test compatibility before enforcement |
| observability | Test compatibility before enforcement |
| envoy-gateway-system | Vendor-required posture |
| buildkit-system | Explicit documented security exception |
