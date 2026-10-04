# CI/CD Pipeline Flow

Secure delivery flow from GitHub to Kubernetes staging and production using ephemeral agents and immutable artifact promotion.

 ```mermaid
flowchart TD

    GH["GitHub<br/>Source Code"]
    JC["Jenkins Controller"]
    BA["Ephemeral Build Agent"]
    BK["Rootless BuildKit<br/>mTLS"]
    REG["GitHub Container Registry<br/>GHCR"]
    TV["Trivy Security Gate"]
    SD["Staging Deploy Agent<br/>Helm"]
    STG["helpdesk-staging<br/>namespace"]
    AP{"Manual Production<br/>Approval"}
    PD["Production Deploy Agent<br/>Helm"]
    PRD["helpdesk-production<br/>namespace"]

    GH --> JC
    JC --> BA
    BA --> BK
    BK --> REG
    REG --> TV
    TV --> SD
    SD --> STG
    STG --> AP
    AP --> PD
    PD --> PRD

    REG -. "Same verified SHA256 digests" .-> PD
```

## Key Controls

- Ephemeral Kubernetes build and deployment agents
- Rootless BuildKit with client/server mTLS
- Immutable GHCR SHA256 image digests
- Trivy HIGH/CRITICAL vulnerability gate
- Separate staging and production namespaces
- Dedicated ServiceAccounts and RBAC
- NetworkPolicies
- Manual production approval
- Same verified artifacts promoted from staging to production
