# PostgreSQL Storage

The local Kubernetes lab uses the kind default `standard` StorageClass backed by `rancher.io/local-path`.

The PostgreSQL StatefulSet uses a dynamically provisioned PersistentVolumeClaim named `data-postgres-0`.

Testing proved that deleting and recreating the PostgreSQL Pod does not delete database data because the replacement Pod mounts the same PVC.

## Local Lab Limitation

`local-path` storage is tied to storage on a kind node.

This demonstrates Pod-level persistence, but it does not provide production-grade distributed storage or automatic database failover if the underlying node or host storage is lost.

A production Kubernetes platform would normally use durable cloud or distributed storage, such as an AWS EBS-backed StorageClass on EKS, combined with an appropriate database availability design.
