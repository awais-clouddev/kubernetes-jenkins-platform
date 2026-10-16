# Operational Runbooks

Run commands against an explicitly selected kubeconfig and context.
Examples below assume a shell function named k:

    k() { kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" "$@"; }

Set those variables to the intended cluster before proceeding. Never paste
credentials, kubeconfig contents or decoded Secrets into tickets or evidence.

## Failed Jenkins Build

1. Identify the first failed stage in the build console.
2. For Pending agents, inspect Pod events in ci-build-agents or
   ci-deploy-agents. Check node labels, taints, resources and image pulls.
3. For BuildKit failures, inspect buildkit-system logs, certificate expiry,
   Service endpoints and client/server certificate names.
4. For registry failures, check credential scope without displaying tokens.
5. For Trivy failures, review the report. Do not bypass the gate to promote.
6. Correct the cause and rerun the reviewed commit. A failed functional gate
   must stop production promotion.

## Pending or Unhealthy Workloads

    k get pods,pvc -n helpdesk-staging -o wide
    k get events -n helpdesk-staging --sort-by=.metadata.creationTimestamp
    k describe pod POD_NAME -n helpdesk-staging
    k logs POD_NAME -n helpdesk-staging --all-containers --tail=100

Check scheduling, image identity, runtime Secret key names, PVC binding,
probe failures, Service endpoints, DNS and NetworkPolicies in that order.
A container-not-found error is not proof of a denied network connection.

On WSL, "too many open files" from fsnotify/systemd can indicate exhausted
inotify instances. Inspect fs.inotify.max_user_instances before adjusting
the host limit. A temporary sysctl change may reset after WSL restarts.

## Database Failure

The API health endpoint returns 503 when PostgreSQL is unavailable.
Redis failure permits degraded health and database-backed ticket reads.
Check PostgreSQL logs, readiness, PVC and API-to-database connectivity.
Do not delete the PVC or replace runtime credentials as a troubleshooting
shortcut. Changing a Secret does not rotate an existing database password.

## Backup and Recovery

Use pg_dump custom format to an access-restricted file outside Git.
Restore with pg_restore --single-transaction into a separate newly created
database. Verify schema and representative records before considering any
cutover. Remove only the disposable recovery database after testing.

The audit restored a staging dump into a separate temporary database and
read three tickets successfully. This does not establish off-host recovery,
point-in-time recovery or recovery after losing the kind node.

## Failed Release and Rollback

Inspect release history and the failed revision before selecting a known-good
revision. Use explicit cluster and namespace options:

    helm history helpdesk-staging --kubeconfig "$LAB_KUBECONFIG" --kube-context "$LAB_CONTEXT" -n helpdesk-staging
    helm rollback helpdesk-staging REVISION --kubeconfig "$LAB_KUBECONFIG" --kube-context "$LAB_CONTEXT" -n helpdesk-staging --wait --timeout 5m

Repeat rollout, image-identity and gateway functional checks afterward.
Use the corresponding production release and namespace only after review.
Helm rollback does not reverse database migrations or restore database data.

## Gateway Failure

Check Gateway Programmed and HTTPRoute Accepted/ResolvedRefs conditions,
proxy Pod readiness, Service endpoints, hostname matching and /api rewrite.
Use scripts/smoke-test.py against the gateway with the correct Host header.
A local port-forward ends when its terminal process stops.
