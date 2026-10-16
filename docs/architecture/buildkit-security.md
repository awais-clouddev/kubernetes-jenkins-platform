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

## Trusted Build Boundary

The no-process-sandbox option weakens isolation between build processes and
the BuildKit daemon. Unconfined seccomp and AppArmor remove additional
runtime restrictions. A dedicated CI node is scheduling separation, not a
separate kernel or virtual-machine security boundary.

This configuration is for trusted project builds. Do not execute untrusted
pull-request code with registry credentials, BuildKit client certificates,
or deployment credentials. Mutual TLS authenticates clients and encrypts
transport; it does not make an authorised malicious build safe.

BuildKit cache uses emptyDir and is disposable. It is not durable storage.
