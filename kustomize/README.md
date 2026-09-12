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
## Environment Overlays

Kustomize allows us to keep common configuration in `base` and customize it for different environments using overlays.

```text
base
 │
 ├── dev
 ├── staging
 └── prod
```

The overlays reference the base instead of copying all the Kubernetes YAML.

---

## Dev Overlay

The Dev overlay currently changes:

* Resource name prefix
* `APP_ENV`
* Deployment replicas
* Container image tag

Structure:

```text
overlays/dev/
├── kustomization.yaml
├── configmap.yaml
└── deployment.yaml
```

Example `kustomization.yaml`:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namePrefix: dev-

patches:
  - path: configmap.yaml
  - path: deployment.yaml

images:
  - name: argocd-app
    newTag: v2
```

### Dev Configuration

```text
APP_ENV: development
replicas: 2
image: argocd-app:v2
namePrefix: dev-
```

Render the Dev overlay:

```bash
k kustomize overlays/dev
```

Apply it:

```bash
k apply -k overlays/dev
```

---

## Staging Overlay

The Staging overlay follows the same pattern.

Structure:

```text
overlays/staging/
├── kustomization.yaml
├── configmap.yaml
└── deployment.yaml
```

Example:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

namePrefix: staging-

patches:
  - path: configmap.yaml
  - path: deployment.yaml

images:
  - name: argocd-app
    newTag: v2
```

### Staging Configuration

```text
APP_ENV: staging
replicas: 1
image: argocd-app:v2
namePrefix: staging-
```

Render the Staging overlay:

```bash
k kustomize overlays/staging
```

Apply it:

```bash
k apply -k overlays/staging
```

---

## Kustomize Features Learned

### `resources`

References the Kubernetes manifests that make up the base or overlay.

```yaml
resources:
  - ../../base
```

### `patches`

Allows an overlay to modify only specific fields from the base instead of duplicating the entire resource.

Example:

```yaml
patches:
  - path: deployment.yaml
```

The Dev Deployment patch only changes:

```yaml
spec:
  replicas: 2
```

### `namePrefix`

Adds a prefix to generated resource names.

```yaml
namePrefix: dev-
```

Example:

```text
argocd-app
↓
dev-argocd-app
```

Kustomize also updates references to renamed resources.

### `nameSuffix`

Adds a suffix to generated resource names.

```yaml
nameSuffix: -dev
```

Example:

```text
argocd-app
↓
argocd-app-dev
```

We learned the concept but are using `namePrefix` in this project.

### `images`

Allows an overlay to change the container image without modifying the base Deployment.

```yaml
images:
  - name: argocd-app
    newTag: v2
```

Base:

```text
argocd-app:v1
```

Dev/Staging:

```text
argocd-app:v2
```

This is particularly useful for CI/CD and GitOps workflows where image versions change frequently.

---

## Errors Encountered

### Patch Could Not Find ConfigMap

Error:

```text
no matches for Id ConfigMap...
failed to find unique target for patch
```

Cause:

The base ConfigMap contained:

```yaml
metadata:
  name: argocd-app-config
  namespace: argocd-learning
```

but the patch did not specify the namespace.

Fix:

```yaml
metadata:
  name: argocd-app-config
  namespace: argocd-learning
```

A Kustomize patch needs to identify the correct resource.

---

## Useful Commands

Render the base:

```bash
k kustomize base
```

Render Dev:

```bash
k kustomize overlays/dev
```

Render Staging:

```bash
k kustomize overlays/staging
```

Apply Dev:

```bash
k apply -k overlays/dev
```

Apply Staging:

```bash
k apply -k overlays/staging
```

Check resources:

```bash
k get all -n argocd-learning
```

Check generated configuration:

```bash
k get configmap -n argocd-learning
```

Check Deployments:

```bash
k get deployments -n argocd-learning
```

---

## Final Kustomize Concept

The main purpose of our Kustomize setup is to avoid duplicating Kubernetes YAML for every environment.

```text
                    BASE
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       ▼             ▼             ▼
      DEV         STAGING         PROD
       │             │             │
       ▼             ▼             ▼
   Customize      Customize      Customize
       │             │             │
       └─────────────┼─────────────┘
                     ▼
             Final Kubernetes YAML
```

The base contains the common application configuration, while overlays contain environment-specific differences.
