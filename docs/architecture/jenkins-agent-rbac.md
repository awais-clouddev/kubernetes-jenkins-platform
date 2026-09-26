# Jenkins Dynamic Agent RBAC

The Jenkins controller is allowed to manage dynamic agent Pods only inside:

- ci-build-agents
- ci-deploy-agents

Minimum resources and verbs:

- pods: get, list, watch, create, delete
- pods/log: get
- pods/exec: get, create
- events: get, list, watch

Access is namespace-scoped with Roles and RoleBindings.
No ClusterRole is granted to the Jenkins controller for agent provisioning.
