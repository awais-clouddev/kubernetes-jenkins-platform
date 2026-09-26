# Dedicated Rootless BuildKit Platform

- Namespace: buildkit-system
- Deployment: one rootless buildkitd Pod
- Image: moby/buildkit:v0.33.0-rootless
- Internal Service: buildkitd.buildkit-system.svc.cluster.local:1234
- Authentication: mutual TLS
- Jenkins build agents use buildctl as clients
- No Docker socket is mounted
- BuildKit receives only the security exceptions required by rootless operation
