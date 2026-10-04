# AWS / EKS Production Mapping

This diagram maps the validated local Kind platform to a production-oriented AWS architecture.

> **Scope:** AWS resources are architectural equivalents only. This project was validated locally on a multi-node Kind cluster; Amazon EKS, RDS, ElastiCache, EBS/EFS, and managed AWS observability services were not deployed by this project.

```mermaid
flowchart LR

    subgraph LOCAL["Validated Local Platform"]
        KIND["Kind Multi-Node Kubernetes"]
        JENKINS["Jenkins Controller + Ephemeral Agents"]
        BUILDKIT["Rootless BuildKit + mTLS"]
        GHCR["GHCR<br/>Immutable SHA256 Digests"]
        ENVOY["Gateway API + Envoy Gateway"]
        STORAGE["local-path Persistent Storage"]
        PG["PostgreSQL StatefulSet"]
        REDIS["Redis Deployment"]
        OBS["Prometheus + Grafana + Alertmanager"]

        KIND --> JENKINS
        JENKINS --> BUILDKIT
        BUILDKIT --> GHCR
        KIND --> ENVOY
        KIND --> STORAGE
        KIND --> PG
        KIND --> REDIS
        KIND --> OBS
    end

    subgraph AWS["Production-Oriented AWS Mapping"]
        EKS["Amazon EKS"]
        NODES["EC2 Managed Node Groups"]
        JCI["Jenkins Controller + Ephemeral Agents on EKS"]
        BKAWS["Rootless BuildKit on EKS<br/>or managed build service"]
        ECR["Amazon ECR<br/>or GHCR"]
        LB["AWS ALB / NLB Integration"]
        EBS["Amazon EBS / EFS"]
        RDS["Amazon RDS for PostgreSQL"]
        CACHE["Amazon ElastiCache for Redis"]
        MON["Amazon Managed Prometheus / Grafana<br/>or self-managed"]
        IAM["EKS Pod Identity / IAM"]
        NET["VPC + Security Groups + NetworkPolicies"]

        EKS --> NODES
        EKS --> JCI
        JCI --> BKAWS
        BKAWS --> ECR
        EKS --> LB
        EKS --> EBS
        EKS --> RDS
        EKS --> CACHE
        EKS --> MON
        EKS --> IAM
        EKS --> NET
    end

    KIND -. "platform equivalent" .-> EKS
    JENKINS -. "same CI/CD pattern" .-> JCI
    BUILDKIT -. "secure image build" .-> BKAWS
    GHCR -. "container registry" .-> ECR
    ENVOY -. "external traffic integration" .-> LB
    STORAGE -. "persistent volumes" .-> EBS
    PG -. "managed database" .-> RDS
    REDIS -. "managed cache" .-> CACHE
    OBS -. "metrics / dashboards / alerts" .-> MON
```

## Local to AWS mapping

| Local implementation | Production-oriented AWS equivalent |
|---|---|
| Kind multi-node Kubernetes | Amazon EKS |
| Local worker nodes | EC2 managed node groups |
| Jenkins controller + ephemeral Kubernetes agents | Jenkins controller + ephemeral agents on EKS |
| Rootless BuildKit + mTLS | Rootless BuildKit on EKS or a managed build service |
| GHCR | Amazon ECR or GHCR |
| Gateway API + Envoy Gateway | AWS ALB / NLB integration |
| local-path storage | Amazon EBS / EFS |
| PostgreSQL StatefulSet | Amazon RDS for PostgreSQL |
| Redis Deployment | Amazon ElastiCache for Redis |
| Kubernetes ServiceAccounts | EKS Pod Identity / IAM |
| Kubernetes RBAC | Kubernetes RBAC + AWS IAM / EKS access controls |
| NetworkPolicies | VPC + Security Groups + Kubernetes NetworkPolicies |
| Prometheus / Grafana / Alertmanager | Amazon Managed Prometheus / Grafana or self-managed |

## Production design principles

- Preserve immutable SHA256 artifact promotion between environments.
- Keep build and deployment workers ephemeral.
- Replace local storage and stateful database/cache workloads with managed AWS services where appropriate.
- Use AWS identity integration instead of static cloud credentials.
- Keep namespace-scoped RBAC and NetworkPolicy controls inside EKS.
- Use private networking and production-specific Kubernetes API access rules.
- Treat this diagram as a production mapping, not evidence that AWS resources were deployed.
