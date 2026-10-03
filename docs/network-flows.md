# Project 6 Required Network Flows

## Application

Frontend → API
API → PostgreSQL
API → Redis

## Gateway

Envoy Gateway → Frontend Service
Envoy Gateway → API Service

## DNS

Application Pods → CoreDNS
CI Pods → CoreDNS
BuildKit → CoreDNS
Observability → CoreDNS

## Jenkins / CI

Build Agent → Jenkins Controller
Build Agent → BuildKit Service
Build Agent → GitHub
Build Agent → GHCR

## BuildKit

Build Agent → BuildKit over mTLS
BuildKit → GHCR
BuildKit → external image registries as required

## Deployment Agents

Deployment Agent → Kubernetes API
Deployment Agent → GitHub when source checkout is required

## Observability

Prometheus → application metrics
Prometheus → Jenkins metrics
Prometheus → Kubernetes targets
Grafana → Prometheus
Alertmanager receives alerts from Prometheus
