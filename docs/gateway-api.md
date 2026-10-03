# Gateway API Architecture

## Gateway Traffic Flow

Staging frontend:

Client
→ Envoy Gateway
→ Gateway `helpdesk-gateway`
→ HTTPRoute `helpdesk-staging-frontend`
→ Service `helpdesk-frontend:80`
→ Frontend Pods

Staging API:

Client
→ Envoy Gateway
→ Gateway `helpdesk-gateway`
→ HTTPRoute `helpdesk-staging-api`
→ `/api` prefix rewrite
→ Service `helpdesk-api:8000`
→ API Pods

The shared Gateway is located in `envoy-gateway-system`.

Only namespaces labeled `gateway-access=allowed` may attach HTTPRoutes.

Staging hostname:
`staging.helpdesk.local`

Production hostname:
`production.helpdesk.local`

Production HTTPRoutes are prepared but remain inactive until the Production promotion phase.

## Gateway API vs Ingress

Ingress is the older Kubernetes HTTP routing API and usually combines routing configuration into an Ingress resource controlled by an Ingress Controller.

Gateway API provides a more expressive role-oriented model:

- GatewayClass defines the controller implementation.
- Gateway defines shared traffic-entry infrastructure.
- HTTPRoute defines application routing rules.
- Routes can safely attach across approved namespaces.
- Gateway API supports clearer separation between platform and application responsibilities.
- It provides richer routing and extensibility than traditional Ingress.

Project 6 uses Envoy Gateway as the Gateway API implementation.
