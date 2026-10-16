# Observability Scope

The committed custom availability rule covers Deployments in
helpdesk-staging only. It does not cover production, PostgreSQL StatefulSets,
database queries, Redis availability, gateway HTTP behavior or user journeys.

Its historical firing and resolution test demonstrates that specific rule
and Alertmanager path. It does not establish alert coverage for every
component. Current audit-cluster monitoring has not yet been installed.

Default kube-prometheus-stack rules depend on the installed chart and
configuration; their presence is not proof that each alert was tested.
External notification delivery is not established by Alertmanager receipt.

Centralized logging and distributed tracing are future work. Current
troubleshooting uses Kubernetes events and container logs.
