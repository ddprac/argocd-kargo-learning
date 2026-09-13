# GitHub, GHCR & Kargo CLI Setup

This section documents the GitHub, GitHub Container Registry (GHCR), and Kargo CLI setup used in this project.

## 2. GitHub Container Registry

GitHub Container Registry (GHCR) is used to store the application container image.

Registry:

```text
ghcr.io
```

Application image:

```text
ghcr.io/ddprac/argocd-app
```

The image was tagged for GHCR:

```bash
docker tag argocd-app:v1 ghcr.io/ddprac/argocd-app:v1
```

A Semantic Version tag was also created for Kargo:

```text
ghcr.io/ddprac/argocd-app:v1.0.0
```

The image was pushed to GHCR:

```bash
docker push ghcr.io/ddprac/argocd-app:v1.0.0
```

The GHCR package was made **Public** so that the image can be pulled without authentication.

### Why `v1.0.0`?

The Kargo Warehouse uses:

```yaml
tagSelectionStrategy: SemVer
```

Kargo's strict Semantic Version matching does not consider `v1` a complete Semantic Version.

Therefore:

```text
v1       → not a complete SemVer
v1.0.0   → valid SemVer
```

## 3. GitHub CLI Authentication

GitHub CLI was already authenticated on the local machine.

Check authentication:

```bash
gh auth status
```

The existing GitHub token can be retrieved locally with:

```bash
gh auth token
```

The token should never be committed to the Git repository.

## 4. Docker Authentication to GHCR

Docker was authenticated to GHCR using the existing GitHub CLI authentication:

```bash
gh auth token | docker login ghcr.io -u ddprac --password-stdin
```

Expected output:

```text
Login Succeeded
```

This allows Docker to push images to GHCR.

## 5. Kargo CLI Installation

The Kargo CLI was installed on macOS using Homebrew:

```bash
brew install kargo
```

Verify the installation:

```bash
kargo version
```

Example:

```text
Client Version: 1.11.4
```

## 6. Kargo CLI Login

Kargo is running locally in Rancher Desktop Kubernetes and is exposed through port-forwarding:

```bash
kubectl port-forward -n kargo svc/kargo-api 3000:443
```

The Kargo CLI can then authenticate against the local Kargo API.

Because the local Kargo API uses a self-signed certificate, TLS verification is skipped for this local learning environment:

```bash
kargo login https://localhost:3000 \
  --admin \
  --insecure-skip-tls-verify
```

The Kargo admin password is entered interactively.

> `--insecure-skip-tls-verify` is being used only because this is a local learning environment with a self-signed certificate. It should not be treated as a production configuration.

## 7. Kargo GitHub Repository Credentials

Kargo runs inside Kubernetes, so it cannot directly use the GitHub credentials stored by the local `gh` CLI.

The existing GitHub CLI token can be temporarily passed to Kargo:

```bash
export KARGO_GITHUB_TOKEN="$(gh auth token)"
```

Create a Git repository credential in the Kargo Project:

```bash
kargo create repo-credentials \
  --project=argocd-learning \
  github-creds \
  --git \
  --repo-url=https://github.com/ddprac/argocd-kargo-learning.git \
  --username=ddprac \
  --password="$KARGO_GITHUB_TOKEN"
```

Remove the temporary environment variable afterward:

```bash
unset KARGO_GITHUB_TOKEN
```

Kargo creates a Kubernetes Secret for the repository credential:

```text
Kubernetes
└── argocd-learning
    └── Secret: github-creds
```

This credential allows Kargo promotion steps to perform Git operations such as cloning, committing, and pushing changes to the repository.

## 8. Kargo Warehouse

Kargo monitors the GHCR image repository using a Warehouse:

```yaml
apiVersion: kargo.akuity.io/v1alpha1
kind: Warehouse
metadata:
  name: argocd-app
  namespace: argocd-learning

spec:
  subscriptions:
    - image:
        repoURL: ghcr.io/ddprac/argocd-app
        tagSelectionStrategy: SemVer
```

The Warehouse discovers available image versions and creates Freight that can later be promoted through Kargo Stages.

The flow is:

```text
GitHub Container Registry
        │
        │ image: v1.0.0
        ▼
     Warehouse
        │
        ▼
      Freight
        │
        ▼
   Kargo Stage
        │
        ▼
 Git repository update
        │
        ▼
     Argo CD
        │
        ▼
    Kubernetes
```
