# Kubernetes Jenkins Platform

A senior-oriented Kubernetes / Platform Engineering portfolio project demonstrating secure CI/CD, ephemeral Jenkins agents, rootless container builds, immutable artifact promotion, Kubernetes security, networking, storage, autoscaling, observability, resilience, and production-style deployment workflows.

---

## Architecture

```text
GitHub
   ↓
Jenkins Controller
   ↓
Ephemeral Kubernetes Agents
   ↓
mTLS
   ↓
Rootless BuildKit
   ↓
GHCR Immutable Image Digests
   ↓
Helm
   ↓
Staging
   ↓
Promotion / Approval
   ↓
Same Immutable Artifact
   ↓
Production
```

---

## Core Technologies

- Kubernetes
- Jenkins
- Ephemeral Kubernetes Agents
- Rootless BuildKit
- mTLS
- GitHub Container Registry (GHCR)
- Helm
- Gateway API
- Envoy Gateway
- RBAC
- ServiceAccounts
- Pod Security
- NetworkPolicies
- Persistent Volumes
- StatefulSets
- Horizontal Pod Autoscaler (HPA)
- PodDisruptionBudget (PDB)
- Prometheus
- Grafana
- Alertmanager
- kube-state-metrics
- Node Exporter
- Docker / OCI Images
- Git / GitHub
- Kind Multi-Node Kubernetes Cluster

---

## CI/CD Architecture

Jenkins runs inside Kubernetes as the CI/CD controller.

Pipeline workloads use temporary Kubernetes agent Pods instead of permanent build workers.

```text
Jenkins Controller
       ↓
Dynamic Kubernetes Agent
       ↓
Rootless BuildKit
       ↓
GHCR
       ↓
Helm
       ↓
Staging
       ↓
Production
```

### Key CI/CD Features

- Jenkins controller deployed on Kubernetes
- Dynamic ephemeral Kubernetes build agents
- One-executor-per-agent strategy
- Rootless container builds
- BuildKit communication protected with mTLS
- Images stored in GHCR
- Immutable SHA256 image digests
- Helm-based deployments
- Staging and Production environments
- Same tested artifact promoted to Production

---

## Rootless BuildKit + mTLS

Application container images are built using rootless BuildKit.

BuildKit communication is protected using mutual TLS.

This provides:

- encrypted communication
- client authentication
- server authentication
- reduced build privileges
- isolation from the Jenkins controller

---

## Immutable Image Promotion

Deployments use immutable image digests instead of mutable tags.

### API

```text
ghcr.io/awais-clouddev/kubernetes-jenkins-platform-api@sha256:96eff54d5611f3b5d3a08fe9c0a3bc8b5fce1e99f2f9cd0331baf8c2a053adc2
```

### Frontend

```text
ghcr.io/awais-clouddev/kubernetes-jenkins-platform-frontend@sha256:005b4543ec059e9f2fb995218c9a2ceb0825865299eca9a004190aa6059bf49a
```

The same API and frontend digests were verified in both Staging and Production.

```text
Staging Artifact
      ↓
Validation
      ↓
Promotion
      ↓
Production

No rebuild between environments
```

This prevents artifact drift between Staging and Production.

---

## Helm Deployment

Helm manages the Kubernetes application deployment.

The chart contains:

- API Deployment
- Frontend Deployment
- Redis Deployment
- PostgreSQL StatefulSet
- Services
- ConfigMaps
- Secrets
- HPA
- PDB
- environment-specific values

Environment-specific configuration is separated using:

```text
values-staging.yaml
values-production.yaml
```

---

## Staging Environment

The Staging environment contains:

- 2 API replicas
- 2 Frontend replicas
- Redis
- PostgreSQL
- Persistent storage
- Horizontal Pod Autoscaler
- PodDisruptionBudget
- NetworkPolicies
- Gateway API routes

---

## Production Environment

The Production environment contains:

- 3 API replicas
- 3 Frontend replicas
- Redis
- PostgreSQL
- Persistent storage
- PodDisruptionBudget
- NetworkPolicies
- immutable API artifact
- immutable Frontend artifact

The Production deployment uses the same application image digests verified in Staging.

---

## Kubernetes Security

The platform implements multiple Kubernetes security controls.

### RBAC

Namespace-scoped RBAC limits Kubernetes API permissions.

### ServiceAccounts

Dedicated ServiceAccounts provide workload identities.

### Pod Security

Restricted Pod Security controls prevent unsafe container configurations such as:

- privilege escalation
- unrestricted Linux capabilities
- unsafe security contexts

### NetworkPolicies

Default-deny policies establish a zero-trust network baseline.

Explicit communication rules allow only required traffic.

Examples:

```text
API → PostgreSQL : 5432
API → Redis      : 6379
Pods → DNS       : 53
Envoy → Frontend
Envoy → API
Prometheus → monitored workloads
```

---

## Gateway API

Application ingress is implemented using Kubernetes Gateway API and Envoy Gateway.

Architecture:

```text
Client
  ↓
Gateway API
  ↓
Envoy Gateway
  ↓
HTTPRoute
  ↓
Kubernetes Service
  ↓
Application Pods
```

Staging HTTPRoutes expose the Helpdesk application through the configured hostname.

---

## Persistent Storage

PostgreSQL runs as a StatefulSet.

Storage uses:

- PersistentVolumeClaim
- Kubernetes StorageClass
- persistent volume lifecycle independent of Pod lifecycle

This allows PostgreSQL data to survive Pod recreation.

The local environment uses Kind/local-path storage.

---

## Horizontal Pod Autoscaler

The API workload includes an HPA.

The HPA can increase or decrease application replicas according to resource demand.

Architecture:

```text
Metrics
  ↓
HPA Controller
  ↓
Deployment
  ↓
More / Fewer Pods
```

---

## PodDisruptionBudget

The API workload uses a PodDisruptionBudget.

The PDB maintains minimum application availability during voluntary disruptions such as node maintenance.

This was validated during a Kubernetes worker drain.

Observed behavior:

```text
Worker Drain
    ↓
Pod Eviction
    ↓
PDB Protection
    ↓
Pod Rescheduling
    ↓
Application Recovery
```

---

## Observability

The platform uses `kube-prometheus-stack`.

Components include:

- Prometheus
- Grafana
- Alertmanager
- kube-state-metrics
- Node Exporter
- Prometheus Operator

Prometheus collects infrastructure and Kubernetes metrics.

Grafana provides visualization.

Alertmanager handles Prometheus alerts.

---

## Real Alert Validation

A custom application availability alert was implemented.

Alert lifecycle tested:

```text
Healthy
   ↓
Condition triggered
   ↓
Pending
   ↓
Firing
   ↓
Alertmanager received alert
   ↓
Condition removed
   ↓
Resolved
```

This proves the complete Prometheus → Alert Rule → Alertmanager flow.

---

## Helm Failure and Rollback

A deliberately invalid application image digest was deployed to create a controlled Helm failure.

Helm recorded the failed release.

The application was then restored using Helm rollback.

Verified sequence:

```text
Working Release
      ↓
Bad Image Digest
      ↓
Failed Helm Release
      ↓
helm history
      ↓
helm rollback
      ↓
Previous Immutable Release Restored
```

The final Helm history confirmed rollback to the known-good release.

---

## Worker Drain Resilience

A Kubernetes worker node was drained to test workload resilience.

During the test:

- the node was cordoned
- Pods were evicted
- PDB behavior was observed
- replacement Pods were scheduled
- application availability recovered
- the worker was uncordoned

Both Staging and Production workloads recovered successfully.

---

## Final Platform Validation

Final validation confirmed:

- all Kubernetes nodes Ready
- Staging API healthy
- Staging Frontend healthy
- Staging Redis healthy
- Staging PostgreSQL healthy
- Production API healthy
- Production Frontend healthy
- Production Redis healthy
- Production PostgreSQL healthy
- Gateway programmed
- HTTPRoutes configured
- Prometheus running
- Grafana running
- Alertmanager running
- Helm rollback completed
- immutable artifact promotion verified

Final evidence is stored in:

```text
evidence/final-platform-proof.txt
```

---

## Repository Structure

```text
kubernetes-jenkins-platform/
│
├── docs/
│
├── evidence/
│
├── helm/
│   └── helpdesk/
│       ├── templates/
│       ├── values.yaml
│       ├── values-staging.yaml
│       └── values-production.yaml
│
├── jenkins/
│
├── k8s/
│   ├── gateway-api/
│   └── network-policies/
│
├── observability/
│   ├── alerts/
│   └── kube-prometheus-stack-values.yaml
│
└── README.md
```

---

## Evidence

The repository contains evidence from implementation and validation.

Examples include:

```text
evidence/
├── final-platform-proof.txt
├── phase10-pipeline/
├── phase19-network-policy-tests.txt
├── phase20-pod-security-denial.txt
└── phase21-hpa-autoscaling.txt
```

---

## Production-Oriented Design

This project runs locally on a multi-node Kind Kubernetes cluster but models production-oriented Platform Engineering patterns.

### Local → AWS Production Mapping

| Local Project | AWS Production Equivalent |
|---|---|
| Kind Kubernetes | Amazon EKS |
| GHCR | Amazon ECR or GHCR |
| Local-path storage | Amazon EBS / EFS |
| PostgreSQL StatefulSet | Amazon RDS |
| Envoy Gateway | AWS ALB / NLB integration |
| ServiceAccounts | IAM / EKS Pod Identity |
| Kubernetes RBAC | EKS RBAC + IAM |
| Prometheus / Grafana | Amazon Managed Prometheus / Grafana or self-managed |
| Local worker nodes | EC2 / managed node groups |
| Kubernetes networking | VPC / Security Groups / Network Policies |

---

## Key Engineering Concepts Demonstrated

This project demonstrates:

- Kubernetes platform architecture
- dynamic CI/CD workers
- secure image building
- mTLS
- immutable artifacts
- GitOps-style deployment principles
- environment promotion
- Helm release management
- rollback
- RBAC
- workload identity
- Pod Security
- zero-trust NetworkPolicies
- application routing
- persistent storage
- autoscaling
- disruption protection
- monitoring
- alerting
- resilience testing
- production-oriented troubleshooting

---

## Local Lab Limitations

This is a local engineering laboratory and not a real public Production system.

Some managed cloud capabilities are intentionally represented by local Kubernetes equivalents.

The purpose is to demonstrate the architecture, security model, automation, deployment flow, troubleshooting process and engineering concepts.

---

## Project Goal

The goal of Project 6 is to demonstrate how:

```text
CI/CD
Kubernetes
Security
Networking
Storage
Scaling
Observability
Resilience
Artifact Promotion
```

work together as one integrated Platform Engineering system rather than as isolated technologies.

---

## Project Status

**Core Kubernetes / Platform Engineering implementation complete.**

Completed areas include:

- Jenkins Kubernetes integration
- ephemeral Kubernetes agents
- rootless BuildKit
- mTLS
- GHCR immutable artifacts
- Helm deployments
- Staging environment
- Production environment
- immutable artifact promotion
- RBAC
- ServiceAccounts
- Pod Security
- NetworkPolicies
- Gateway API
- persistent storage
- HPA
- PDB
- Prometheus
- Grafana
- Alertmanager
- real alert validation
- Helm rollback
- worker-drain resilience
- final platform evidence

