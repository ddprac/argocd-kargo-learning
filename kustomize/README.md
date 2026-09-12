# Kustomize

This folder contains the Kustomize configuration for the `argocd-app` Kubernetes application.

## What We Learned

Kustomize allows us to organize Kubernetes YAML into:

```text
Base
  ↓
Environment overlays
  ↓
Generated Kubernetes manifests
```

We are using:

```text
kustomize/
├── base/
└── overlays/
    ├── dev/
    ├── staging/
    └── prod/
```

### Base

The `base` contains the common Kubernetes resources:

```text
base/
├── namespace.yaml
├── deployment.yaml
├── service.yaml
├── configmap.yaml
├── secrets.yaml
└── kustomization.yaml
```

The base can be rendered with:

```bash
k kustomize base
```

The generated YAML can be applied with:

```bash
k apply -k base
```

### Overlay

An overlay references the base instead of copying all the Kubernetes YAML.

For example, Dev:

```text
overlays/dev/
├── configmap.yaml
└── kustomization.yaml
```

`kustomization.yaml`:

```yaml
resources:
  - ../../base

patches:
  - path: configmap.yaml
```

This allows Dev to change only what is different from the base.

For example:

```text
Base:
APP_ENV: staging

Dev overlay:
APP_ENV: development
```

Render the Dev overlay:

```bash
k kustomize overlays/dev
```

Apply the Dev overlay:

```bash
k apply -k overlays/dev
```

---

## Errors We Encountered

### 1. `k kustomize version` Error

We initially ran:

```bash
k kustomize version
```

and received an error similar to:

```text
error: must build at directory: not a valid directory
```

#### Why?

`kubectl kustomize` expects a directory to build.

`version` was interpreted as a directory name.

Correct usage:

```bash
k kustomize base
```

Since Kustomize is already included with our `kubectl`, we do not need to install the standalone Kustomize CLI.

---

### 2. Namespace Not Found

After deleting the old Kubernetes lab namespace, we tried:

```bash
k apply -k base
```

and received:

```text
namespaces "argocd-learning" not found
```

#### Why?

Our Kubernetes resources referenced:

```yaml
namespace: argocd-learning
```

but the namespace had been deleted.

We added `namespace.yaml` to the Kustomize base:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: argocd-learning
```

and added it to `kustomization.yaml`:

```yaml
resources:
  - namespace.yaml
  - deployment.yaml
  - service.yaml
  - configmap.yaml
  - secrets.yaml
```

This allows the Kustomize base to recreate the namespace and application resources.

---

### 3. Kustomize Patch Could Not Find ConfigMap

When creating the Dev ConfigMap patch, we initially received:

```text
no matches for Id ConfigMap.v1.[noGrp]/argocd-app-config.[noNs]
failed to find unique target for patch
```

#### Why?

The ConfigMap in the base had:

```yaml
metadata:
  name: argocd-app-config
  namespace: argocd-learning
```

But the Dev patch only specified:

```yaml
metadata:
  name: argocd-app-config
```

Kustomize could not identify the exact resource to patch.

We fixed it by specifying the namespace in the patch:

```yaml
metadata:
  name: argocd-app-config
  namespace: argocd-learning
```

Now Kustomize can match the Dev patch to the ConfigMap in the base.

---

## Useful Commands

Render the base:

```bash
k kustomize base
```

Render the Dev overlay:

```bash
k kustomize overlays/dev
```

Apply the base:

```bash
k apply -k base
```

Apply the Dev overlay:

```bash
k apply -k overlays/dev
```

Check resources:

```bash
k get all -n argocd-learning
```

Check the ConfigMap:

```bash
k get configmap argocd-app-config -n argocd-learning -o yaml
```

Check the application configuration:

```bash
k run curl-test \
  --image=curlimages/curl \
  -it \
  --rm \
  --restart=Never \
  -n argocd-learning \
  -- curl http://argocd-app:9000/config
```

---

## Key Takeaway

Kustomize lets us keep common Kubernetes configuration in a **base** and make environment-specific changes through **overlays**, without duplicating all the YAML.

```text
              Base
               │
       ┌───────┼────────┐
       ↓       ↓        ↓
      Dev   Staging    Prod
       │       │        │
       └───────┼────────┘
               ↓
       Environment-specific
          Kubernetes YAML
```
