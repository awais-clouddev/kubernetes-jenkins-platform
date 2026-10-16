# Project Evidence

Existing phase directories and final proof files record historical project
runs. They do not automatically verify later configuration or source changes.

The phase7-dynamic-agent/jenkins-cloud-config.yaml file is retained as
historical evidence. Until separately parsed and validated, treat it as a
configuration excerpt, not an installable Jenkins values file.

The historical phase19 negative tests reported "container not found".
Those errors do not prove traffic denial. A fresh audit-cluster test instead
confirmed a working HTTP connection, timeout after an ingress-deny policy,
and restored connectivity after removing that policy.

Keep historical files intact. Record new checks separately with their
cluster, image identity, result and verification limits.
