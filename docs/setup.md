# Local Platform Setup

## Scope and prerequisites

This guide describes the intended full platform setup. The current validation
verified the application, Envoy routing, probes, API egress discovery,
deploy-agent gateway access and a disposable database restore. A complete
fresh Jenkins/BuildKit/monitoring installation using this guide remains
unverified.

Use Docker, kind, kubectl, Helm, OpenSSL, Python 3 and Git. Recorded platform
versions are in ../platform-versions.md. Run commands from the repository root.

Use a dedicated cluster name and kubeconfig. Do not delete an existing
cluster to reproduce this lab.

## 1. Create and select the cluster

Example:

    export LAB_KUBECONFIG="$HOME/jenkins-audit.kubeconfig"
    export LAB_CONTEXT="kind-jenkins-audit"
    kind create cluster --name jenkins-audit --config cluster/kind-config.yaml --kubeconfig "$LAB_KUBECONFIG" --wait 120s
    k() { kubectl --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" "$@"; }
    k get nodes -L workload

The configuration creates two application workers and one tainted CI worker.
The audited node version was Kubernetes v1.37.0 with kind v0.33.0.

On WSL, inspect inotify limits if systemd or kubelet reports fsnotify
"too many open files". The validation required max_user_instances=1024.
A temporary sysctl change resets after some WSL restarts.

## 2. Verify networking

Confirm kindnet and kube-proxy are Ready. Test a working Pod-to-Pod HTTP
connection, apply a deny policy, confirm timeout, then remove the policy and
confirm recovery. Do not interpret missing containers or DNS errors as proof
of isolation. Repeat application-specific allowed and denied paths after
installing repository policies.

## 3. Create namespaces and security posture

    for ns in helpdesk-staging helpdesk-production ci-build-agents ci-deploy-agents jenkins buildkit-system envoy-gateway-system observability; do
      k create namespace "$ns" --dry-run=client -o yaml | k apply -f -
    done

    for ns in helpdesk-staging helpdesk-production ci-deploy-agents; do
      k label namespace "$ns" pod-security.kubernetes.io/enforce=restricted --overwrite
    done

    k label namespace buildkit-system pod-security.kubernetes.io/enforce=privileged pod-security.kubernetes.io/audit=restricted pod-security.kubernetes.io/warn=restricted --overwrite
    k label namespace helpdesk-staging helpdesk-production gateway-access=allowed --overwrite

Review vendor compatibility before enforcing Restricted in controller,
monitoring or build namespaces. BuildKit exceptions are documented in
architecture/buildkit-security.md.

## 4. Runtime and registry credentials

Create separate runtime credentials for each application namespace:

    export DATABASE_NAME=helpdesk DATABASE_USER=helpdesk
    read -rsp 'Database password: ' DATABASE_PASSWORD; echo
    export DATABASE_PASSWORD
    bash scripts/bootstrap-runtime-secret.sh helpdesk-staging "$LAB_KUBECONFIG" "$LAB_CONTEXT"
    unset DATABASE_PASSWORD

Repeat for helpdesk-production with its own password. The helper refuses
existing Secrets. Changing a Secret does not rotate an initialized database.

The chart references ghcr-pull. Provision a kubernetes.io/dockerconfigjson
Secret with that name in each application namespace when private images
require authentication. Use a protected temporary Docker configuration file,
pass it through --from-file=.dockerconfigjson=PATH, and securely remove it.
Do not put tokens in Git, command history or published evidence.

## 5. BuildKit mutual TLS

Create a private CA, a server certificate and a separate client certificate
outside the repository using an access-restricted temporary directory.

The server certificate must have serverAuth extended key usage and DNS SANs:

- buildkitd
- buildkitd.buildkit-system
- buildkitd.buildkit-system.svc
- buildkitd.buildkit-system.svc.cluster.local

The client certificate must have clientAuth extended key usage. Verify both
against the CA and check expiry before use. Create these runtime Secrets:

- buildkit-system/buildkit-server-tls: ca.crt, tls.crt, tls.key
- ci-build-agents/buildkit-client-tls: ca.crt, tls.crt, tls.key

Keep the CA private key outside Kubernetes and Git. Do not reuse the server
private key as a client key. Deploy only after both Secrets exist:

    k apply -f buildkit/serviceaccount.yaml -f buildkit/service.yaml -f buildkit/deployment.yaml
    k rollout status deployment/buildkitd -n buildkit-system --timeout=180s

## 6. Agent identities and network policies

    k apply -f jenkins/rbac/
    k apply -f k8s/rbac/
    k apply -f k8s/network-policies/

Generate the API allow policy separately; it is no longer hard-coded:

    python3 scripts/render-api-egress.py --kubeconfig "$LAB_KUBECONFIG" --context "$LAB_CONTEXT" > /tmp/helpdesk-api-egress.json
    k apply -f /tmp/helpdesk-api-egress.json
    rm /tmp/helpdesk-api-egress.json

Regenerate after API endpoint changes. These are CNI-dependent egress rules;
verify connectivity from an actual deploy-agent Pod. Confirm that staging
and production identities have only their intended namespace access.

## 7. Jenkins

    helm repo add jenkins https://charts.jenkins.io
    helm repo update
    helm upgrade --install jenkins jenkins/jenkins --version 5.9.45 --namespace jenkins --kubeconfig "$LAB_KUBECONFIG" --kube-context "$LAB_CONTEXT" -f jenkins/values.yaml --wait --timeout 10m

Access Jenkins through a localhost port-forward. Retrieve bootstrap
credentials privately; never include their values in evidence.

Create a username/password credential with ID ghcr-credentials, using the
registry username and a suitably scoped token. Configure a Pipeline from SCM
for this repository with script path Jenkinsfile. Confirm the build, staging
and production agent labels match jenkins/values.yaml.

Only trusted, reviewed pipeline code may receive credentials. Do not enable
credential-bearing builds for untrusted pull requests.

## 8. Envoy Gateway and routes

    helm upgrade --install eg oci://docker.io/envoyproxy/gateway-helm --version v1.9.1 --namespace envoy-gateway-system --kubeconfig "$LAB_KUBECONFIG" --kube-context "$LAB_CONTEXT" --wait --timeout 5m
    k apply -f k8s/gateway-api/envoyproxy.yaml -f k8s/gateway-api/gatewayclass.yaml -f k8s/gateway-api/gateway.yaml
    k apply -f k8s/gateway-api/staging-api-route.yaml -f k8s/gateway-api/staging-frontend-route.yaml
    k apply -f k8s/gateway-api/production-api-route.yaml -f k8s/gateway-api/production-frontend-route.yaml

Wait for Gateway Programmed and inspect HTTPRoute Accepted/ResolvedRefs.
Confirm the generated proxy Service name matches the smoke-test URL in
Jenkinsfile. Update that URL if gateway naming changes. Envoy container
traffic uses port 10080; its Service exposes port 80.

## 9. Metrics and monitoring

    helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update

Install metrics-server chart 3.14.0. For kind, review whether the
--kubelet-insecure-tls compatibility setting is required; keep that exception
local to this lab. Verify kubectl top works before enabling staging HPA.

    helm upgrade --install monitoring prometheus-community/kube-prometheus-stack --version 91.5.1 --namespace observability --kubeconfig "$LAB_KUBECONFIG" --kube-context "$LAB_CONTEXT" -f observability/kube-prometheus-stack-values.yaml --wait --timeout 10m
    k apply -f observability/alerts/helpdesk-availability-alert.yaml

Review observability-scope.md. Test firing and resolution deliberately before
claiming current alert delivery. Logging and tracing are outside lab scope.

## 10. Delivery and acceptance

Run Jenkins against the reviewed commit. Require API tests, image builds,
the vulnerability gate, staging rollout, digest verification and gateway
functional checks before production approval. Promote the same digests.

Frontend structure checks and HTTP asset checks do not prove browser
rendering or JavaScript behavior. Verify production independently after
approval. See runbooks/README.md for failures and rollback.

Local validation images were loaded into kind; this does not verify a revised
registry publication or a complete Jenkins run.
