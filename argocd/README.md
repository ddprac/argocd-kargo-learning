# Argo CD

Argo CD is a GitOps continuous delivery tool for Kubernetes. It continuously compares the desired state in Git with the live state in Kubernetes and reconciles differences.

## What We Learned

* Argo CD Application
* Defines the Git repository, branch, manifest path, and Kubernetes destination.
* Git as the source of truth
* Kustomize integration
* Manual Sync
* Automated Sync
* Self-Healing
* Pruning
* Drift detection
* Sync status vs Health status

  * `Synced` / `OutOfSync`
  * `Healthy` / `Progressing`

## GitOps Flow

```text
Git
 ↓
Argo CD
 ↓
Kustomize
 ↓
Kubernetes
 ↓
Application
```

### Automated Sync

Git change → Argo CD detects change → Kubernetes automatically updated

### Self-Healing

Kubernetes drift → Argo CD detects difference → desired state restored

### Pruning

Resource removed from Git → Argo CD detects difference → resource removed from Kubernetes

## Installation

Create the Argo CD namespace:

```bash
kubectl create namespace argocd
```

Install Argo CD:

```bash
kubectl apply -n argocd \
  --server-side \
  --force-conflicts \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Verify:

```bash
kubectl get pods -n argocd
```

## Access Argo CD Locally

Port-forward the Argo CD server:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open:

```text
https://localhost:8080
```

## Uninstall

Remove the Argo CD installation:

```bash
kubectl delete namespace argocd
```

This removes Argo CD and the resources inside the `argocd` namespace.

## Application

The Argo CD Application definition is maintained as:

```text
argocd/application.yaml
```
```bash
Trigger a manual sync

kubectl patch application flask-dev -n argocd \
  --type merge \
  -p '{"operation":{"sync":{}}}'

kubectl patch application flask-dev -n argocd \
  --type merge \
  -p '{"spec":{"syncPolicy":{"automated":{"selfHeal":true}}}}'

kubectl patch application flask-dev -n argocd \
  --type merge \
  -p '{"spec":{"syncPolicy":{"automated":{"prune":true}}}}'

```
The application currently deploys the development environment from:

```text
kustomize/overlays/dev
```

## Useful Commands

```bash
kubectl get application -n argocd
kubectl get application flask-dev -n argocd -o yaml
kubectl get pods -n argocd-learning
kubectl get deployment -n argocd-learning
```
