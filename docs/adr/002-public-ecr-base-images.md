# ADR 002 — Public ECR for Docker Official Base Images

Docker Hub HTTPS access from the local CI node timed out while GitHub, GHCR, and Amazon ECR Public HTTPS access succeeded.

For the local Project 6 lab, Docker Official base images are pulled through Amazon ECR Public.

Frontend:
`public.ecr.aws/docker/library/nginx:alpine`

API:
`public.ecr.aws/docker/library/python:3.13-slim`

This changes only the registry source of the base images and does not change the application architecture.
