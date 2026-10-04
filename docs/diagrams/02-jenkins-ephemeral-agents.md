# Jenkins Controller and Ephemeral Agent Architecture

This diagram documents how the Jenkins controller orchestrates short-lived Kubernetes agents for build, staging deployment, and production deployment.

```mermaid
flowchart TD

    GH["GitHub<br/>Source Repository"]

    subgraph JNS["jenkins namespace"]
        JC["Jenkins Controller<br/>always running"]
        JPVC["Jenkins Persistent Volume<br/>JENKINS_HOME"]
        JC --- JPVC
    end

    subgraph CB["ci-build-agents namespace"]
        BA["Ephemeral Build Agent Pod<br/>ServiceAccount: jenkins-build-agent"]
    end

    subgraph BKNS["buildkit-system namespace"]
        BK["Rootless BuildKit<br/>mTLS endpoint"]
    end

    REG["GitHub Container Registry<br/>GHCR"]
    TV["Trivy Security Gate"]

    subgraph CD["ci-deploy-agents namespace"]
        SDA["Ephemeral Staging Deploy Agent<br/>ServiceAccount: staging-deployer"]
        PDA["Ephemeral Production Deploy Agent<br/>ServiceAccount: production-deployer"]
    end

    STG["helpdesk-staging namespace"]
    AP{"Manual Production Approval<br/>No deploy agent held while waiting"}
    PRD["helpdesk-production namespace"]
    KAPI["Kubernetes API Server"]

    GH --> JC
    JC -->|"creates"| BA
    BA --> BK
    BK --> REG
    REG --> TV
    TV --> JC

    JC -->|"creates after security gate"| SDA
    SDA -->|"Helm deploy + verify"| STG
    SDA -->|"job complete: pod removed"| JC

    STG --> AP
    AP -->|"approved"| JC
    JC -->|"creates only after approval"| PDA
    PDA -->|"Helm deploy same SHA256 digests"| PRD
    PDA -->|"job complete: pod removed"| JC

    JC --> KAPI
    BA --> KAPI
    SDA --> KAPI
    PDA --> KAPI
```

## Agent lifecycle

```text
Jenkins Controller
      |
      +--> create Build Agent
      |       |
      |       +--> checkout / test / BuildKit / GHCR / Trivy
      |       |
      |       +--> delete Build Agent
      |
      +--> create Staging Deploy Agent
      |       |
      |       +--> Helm deploy + verify staging
      |       |
      |       +--> delete Staging Deploy Agent
      |
      +--> Manual Approval
      |       |
      |       +--> no deploy agent held while waiting
      |
      +--> create Production Deploy Agent
              |
              +--> Helm deploy same immutable digests
              |
              +--> delete Production Deploy Agent
```

## Security boundaries

- Jenkins controller runs separately from build and deployment agents.
- Build agent uses its dedicated `jenkins-build-agent` ServiceAccount.
- Staging uses the dedicated `staging-deployer` ServiceAccount.
- Production uses the dedicated `production-deployer` ServiceAccount.
- BuildKit is isolated in `buildkit-system` and requires client/server mTLS.
- Deploy agents are ephemeral and protected by NetworkPolicies.
- Staging and production RBAC are separated.
- Production deploy agent is created only after manual approval.
