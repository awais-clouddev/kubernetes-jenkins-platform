# Deployment RBAC Trust Model

Jenkins build agents use the `jenkins-build-agent` ServiceAccount in the `ci-build-agents` namespace.

The build-agent identity does not have permission to deploy workloads into staging and cannot create Pods in the `ci-deploy-agents` namespace. This prevents build Pods from directly using the staging or production deployment identities.

Staging and production deployment agents use separate ServiceAccounts:

- `staging-deployer`
- `production-deployer`

Their permissions are namespace-scoped using Kubernetes Roles and RoleBindings.

Deployment agents are ephemeral and are created only when Jenkins needs to perform a deployment.

## Jenkins Controller Trust

The Jenkins controller remains a high-trust component because it can request deployment-agent Pods that run with the staging or production deployment ServiceAccounts.

Therefore, compromise of the Jenkins controller could potentially allow an attacker to request a privileged deployment agent even though normal build agents do not possess deployment permissions.

Protecting the Jenkins controller, its configuration, credentials, RBAC permissions, and administrative access is therefore critical.

## Secret Access and Deployment Trust

Both deployer Roles grant Secret read and write access throughout their
respective application namespaces. Helm uses Secrets for release records,
but these permissions also cover runtime credentials and image-pull Secrets.
Kubernetes RBAC does not restrict this access by Secret label or prefix.

Deployers must therefore be treated as trusted namespace operators.
Permission to modify workload specifications also permits creating workloads
that consume namespace Secrets. These Roles do not provide isolation from
application credentials.

Keep staging and production identities separate. Production approval is a
workflow control; it does not remove permissions from a credential already
available to a running deploy agent. Only trusted, reviewed pipeline code
should receive these identities.
