# BuildKit Rootless Security Model

The Project 6 BuildKit daemon runs as a non-root user in the isolated `buildkit-system` namespace.

Rootless BuildKit reduces privilege compared with a rootful Docker daemon, but rootless does not automatically mean Kubernetes Restricted-compliant.

For this local lab, BuildKit uses only the compatibility exceptions required for rootless operation, including an Unconfined seccomp/AppArmor posture and `--oci-worker-no-process-sandbox`.

The BuildKit namespace therefore uses a privileged Pod Security enforcement posture while Restricted violations remain visible through audit/warn labels.

Security boundaries used by this project:

- BuildKit runs in its own `buildkit-system` namespace.
- BuildKit uses a dedicated ServiceAccount.
- ServiceAccount token automounting is disabled.
- BuildKit receives no application deployment RBAC.
- No Docker socket is mounted.
- Jenkins build agents communicate with BuildKit only through the internal Kubernetes Service.
- BuildKit TCP access requires mutual TLS.
- Build agents receive only the client CA/certificate/key Secret.
- Private keys are not committed to Git.
- Rootless operation reduces privilege but does not remove every kernel/security exception required by BuildKit.
