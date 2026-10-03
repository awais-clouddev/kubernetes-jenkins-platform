# Pod Disruption Budget

## API PDB

The helpdesk API uses a PodDisruptionBudget with:

- minAvailable: 1
- selector: app=helpdesk-api

This ensures that at least one healthy API Pod remains available during voluntary disruptions.

## Voluntary disruption

Voluntary disruptions are controlled Kubernetes operations such as:

- Pod eviction
- Node drain
- Cluster maintenance
- Planned workload movement

The API PDB can block these disruptions if they would reduce available API Pods below the configured minimum.

Observed evidence:

- With 2 healthy API Pods, one eviction was allowed.
- Kubernetes created a replacement Pod.
- With only 1 healthy API Pod, eviction was blocked.
- Kubernetes returned TooManyRequests because the disruption would violate the PDB.

## Involuntary disruption

Involuntary disruptions include events such as:

- Node failure
- Hardware failure
- Kernel crash
- Sudden power loss
- Container or Pod crash

A PDB does not prevent involuntary failures.

The Deployment and Kubernetes controllers are responsible for recreating failed Pods, while the PDB mainly protects availability during voluntary disruptions.
