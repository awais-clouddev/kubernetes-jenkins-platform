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
