# Helm

This folder contains the Helm chart for deploying the Flask application to Kubernetes.

The Helm chart is the Helm-based version of the Kubernetes deployment created earlier in this project.

## Purpose

Helm helps package Kubernetes manifests into a reusable chart.

Instead of maintaining separate Kubernetes YAML files for every environment, Helm allows configuration to be provided through `values.yaml`.

Basic flow:

```text
values.yaml
     │
     ▼
Helm templates
     │
     ▼
Rendered Kubernetes YAML
     │
     ▼
Kubernetes
```

## Folder Structure

```text
helm/
└── app/
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── deployment.yaml
        ├── service.yaml
        ├── configmap.yaml
        └── secret.yaml
```

## Chart.yaml

`Chart.yaml` contains metadata about the Helm chart.

Important fields:

```yaml
apiVersion: v2
name: argocd-app
type: application
version: 0.1.0
appVersion: "1.0"
```

### `version`

The version of the Helm chart itself.

### `appVersion`

The version of the application being deployed.

These are separate concepts.

```text
Chart version  →  0.1.0
Application    →  1.0
```

## values.yaml

`values.yaml` contains configurable values used by the templates.

Example:

```yaml
replicaCount: 1

image:
  repository: argocd-app
  tag: v1
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 9000

app:
  environment: staging
```

Templates access these values using:

```text
.Values.<path>
```

For example:

```yaml
replicas: {{ .Values.replicaCount }}
```

and:

```yaml
image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
```

This allows the same chart to be configured differently without changing the templates.

## Templates

The `templates/` directory contains Kubernetes manifests with Helm templating.

### Deployment

`deployment.yaml` creates the application Deployment.

Helm values are used for things such as:

* replica count
* container image
* image pull policy
* resource requests and limits
* application configuration
* health probes

Example:

```yaml
replicas: {{ .Values.replicaCount }}
```

### Service

`service.yaml` creates a Kubernetes Service for the application.

The service configuration comes from:

```yaml
service:
  type: ClusterIP
  port: 9000
```

### ConfigMap

`configmap.yaml` creates the application configuration.

The environment is controlled through:

```yaml
app:
  environment: staging
```

The Flask application reads this through the `APP_ENV` environment variable.

### Secret

`secret.yaml` creates a Kubernetes Secret used by the application.

The password in this learning project is a **fake demo value**.

Real credentials or secrets should not be committed to Git.

## Important Helm Commands

### Validate the chart

```bash
helm lint app
```

Checks whether the Helm chart is valid.

### Render templates locally

```bash
helm template myapp app
```

This renders the Helm templates into Kubernetes YAML without deploying anything.

Useful for checking what Helm will generate.

### Install a chart

```bash
helm install myapp app -n argocd-learning
```

### Check releases

```bash
helm list -n argocd-learning
```

### Upgrade a release

```bash
helm upgrade myapp app -n argocd-learning
```

### View release history

```bash
helm history myapp -n argocd-learning
```

### Roll back a release

```bash
helm rollback myapp 1 -n argocd-learning
```

A rollback creates a new Helm revision.

For example:

```text
Revision 1 → Install
Revision 2 → Upgrade
Revision 3 → Rollback to revision 1
```

### Remove a release

```bash
helm uninstall myapp -n argocd-learning
```

This removes the Helm-managed Kubernetes resources.

The chart files in Git remain unchanged.

## Helm Release

A Helm **release** is a deployed instance of a chart.

For example:

```bash
helm install myapp app
```

creates:

```text
Chart
  │
  ▼
Helm Release: myapp
  │
  ▼
Kubernetes resources
```

The same chart can therefore be installed multiple times with different release names and configurations.

## Helm vs Kustomize

Both can manage Kubernetes configuration, but they approach it differently.

### Kustomize

```text
Base manifests
      │
      ├── dev overlay
      ├── staging overlay
      └── prod overlay
```

Kustomize works mainly by modifying existing Kubernetes YAML using overlays and patches.

### Helm

```text
Helm chart
    │
    ├── values-dev.yaml
    ├── values-staging.yaml
    └── values-prod.yaml
          │
          ▼
      Templates
          │
          ▼
   Kubernetes manifests
```

Helm uses templates and values to generate Kubernetes manifests.

In this project, both approaches are intentionally used with the same Flask application so their differences can be understood.

## What Was Practiced

This section covered:

* Helm chart structure
* `Chart.yaml`
* `values.yaml`
* Helm templates
* `.Values`
* `.Release.Name`
* `helm lint`
* `helm template`
* `helm install`
* `helm upgrade`
* Helm releases
* Helm revisions
* `helm history`
* `helm rollback`
* `helm uninstall`
* Helm vs Kustomize

## Current State

The Helm chart remains in the repository:

```text
helm/app/
```

The Helm release has been removed from the local Kubernetes cluster.

This gives the project a clean starting point for the next phase.
