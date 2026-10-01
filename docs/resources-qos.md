# Kubernetes Resources and QoS

## CPU

CPU requests reserve scheduling capacity for a container.

CPU limits control the maximum CPU time available to a container.

If a container tries to use more CPU than its configured limit, Linux cgroups throttle the container. The container normally remains running but receives less CPU time.

## Memory

Memory requests influence Kubernetes scheduling.

Memory limits define the maximum memory available to the container.

If a container exceeds its memory limit and the kernel cannot reclaim enough memory, the container can be terminated with OOMKilled and restarted according to Kubernetes restart behavior.

## QoS

The Help Desk frontend, API, PostgreSQL and Redis define both requests and limits, but requests are lower than limits.

Therefore the application workloads are designed to run with the Kubernetes Burstable QoS class.

## Project Configuration

Frontend:
- CPU request: 50m
- CPU limit: 250m
- Memory request: 64Mi
- Memory limit: 128Mi

API:
- CPU request: 100m
- CPU limit: 500m
- Memory request: 128Mi
- Memory limit: 256Mi

PostgreSQL:
- CPU request: 100m
- CPU limit: 500m
- Memory request: 256Mi
- Memory limit: 512Mi

Redis:
- CPU request: 50m
- CPU limit: 250m
- Memory request: 64Mi
- Memory limit: 128Mi
