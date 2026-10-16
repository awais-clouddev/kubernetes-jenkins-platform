# PostgreSQL Storage

The local Kubernetes lab uses the kind default `standard` StorageClass backed by `rancher.io/local-path`.

The PostgreSQL StatefulSet uses a dynamically provisioned PersistentVolumeClaim named `data-postgres-0`.

Testing proved that deleting and recreating the PostgreSQL Pod does not delete database data because the replacement Pod mounts the same PVC.

## Local Lab Limitation

`local-path` storage is tied to storage on a kind node.

This demonstrates Pod-level persistence, but it does not provide production-grade distributed storage or automatic database failover if the underlying node or host storage is lost.

A production Kubernetes platform would normally use durable cloud or distributed storage, such as an AWS EBS-backed StorageClass on EKS, combined with an appropriate database availability design.

## Backup and Availability Boundary

Each environment runs one PostgreSQL instance. Multiple API replicas and
a PodDisruptionBudget do not make the database highly available.

A PVC preserves data across Pod replacement; it is not an independent
backup. Deleting a kind cluster or losing its node storage can lose data.
EBS alone would not provide database replication or automatic failover.

Backup recovery must be tested by restoring a dump into a separate empty
database and checking its contents. Never test restoration over the active
application database. Scheduled off-host backups and point-in-time recovery
are outside this local lab's current implementation.
