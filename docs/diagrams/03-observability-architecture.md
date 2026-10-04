# Observability Architecture

This diagram documents the monitoring and alerting architecture used by the Kubernetes platform.

```mermaid
flowchart TD

    subgraph K8S["Kubernetes Cluster"]
        subgraph APP["Application Workloads"]
            STG["helpdesk-staging<br/>Frontend / API / PostgreSQL / Redis"]
            PRD["helpdesk-production<br/>Frontend / API / PostgreSQL / Redis"]
        end

        subgraph INFRA["Cluster / Platform Metrics"]
            KSM["kube-state-metrics<br/>Kubernetes object state"]
            NE["node-exporter<br/>Node / host metrics"]
        end

        subgraph OBS["observability namespace"]
            PROM["Prometheus<br/>Metrics collection + alert evaluation"]
            AlERT["Alert Rules<br/>HelpdeskDeploymentUnavailable"]
            AM["Alertmanager<br/>Alert routing / lifecycle"]
            GRAF["Grafana<br/>Dashboards"]
        end
    end

    STG -->|"application / workload metrics"| PROM
    PRD -->|"application / workload metrics"| PROM
    KSM -->|"cluster state metrics"| PROM
    NE -->|"node metrics"| PROM

    PROM --> GRAF
    PROM --> ALERT
    ALERT --> AM    PROM -. "query metrics" .-> GRAF
```

## Monitoring flow

```text
Application / Kubernetes Workloads
              |
              +--> kube-state-metrics
              |
              +--> node-exporter
              |
              v
          Prometheus
          /        \
         v          v
      Grafana    Alert Rules
                    |
                    v
               Alertmanager
```

## Validated platform components

- Prometheus
- Grafana
- Alertmanager
- kube-state-metrics
- node-exporter
- Kubernetes workload and node metrics
- Custom `HelpdeskDeploymentUnavailable` alert
- Alert lifecycle validated from Inactive -> Pending -> Firing -> Alertmanager -> Resolved

## Scope note

This platform provides metrics, dashboards, and alerts. It does not claim a centralized logging stack such as Loki or ELK.
