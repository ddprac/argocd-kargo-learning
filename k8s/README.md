# Kubernetes — Configuration, Health & Resources

This section covers the basic Kubernetes concepts used in this project.

## ConfigMap

ConfigMap stores **non-sensitive configuration** separately from the application image.

Example:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-app-config
  namespace: argocd-learning
data:
  APP_ENV: "development"
```


### Apply

```bash
k apply -f configmap.yaml
```

### Check

```bash
k get configmap -n argocd-learning
k describe configmap argocd-app-config -n argocd-learning
k get configmap argocd-app-config -n argocd-learning -o yaml
```

### Use in Pod

```yaml
env:
  - name: APP_ENV
    valueFrom:
      configMapKeyRef:
        name: argocd-app-config
        key: APP_ENV
```
```bash
k run curl-test \
  --image=curlimages/curl \
  -it \
  --rm \
  --restart=Never \
  -n argocd-learning \
  -- curl http://argocd-app:9000/health
```

**Important:** When a ConfigMap is consumed as an environment variable, an existing Pod does not automatically receive a changed value. Restart/recreate the Pod.

```bash
k rollout restart deployment/argocd-app -n argocd-learning
```

---

## Secret

Secret is used for **sensitive configuration** such as passwords, tokens and keys.

Example:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: argocd-app-secret
  namespace: argocd-learning
type: Opaque
stringData:
  DB_PASSWORD: "my-demo-password"
```

> The password above is only a demo value. Never commit real credentials to Git.

### Apply

```bash
k apply -f secret.yaml
```

### Check

```bash
k get secrets -n argocd-learning
k describe secret argocd-app-secret -n argocd-learning
```

### Use in Pod

```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: argocd-app-secret
        key: DB_PASSWORD
```

### Execute a command inside a Pod

```bash
k get pods -n argocd-learning
k exec -n argocd-learning <pod-name> -- env
```

`kubectl exec` operates on a **Pod/container**. A Deployment only manages Pods.

---

## Readiness Probe

Readiness answers:

> **Can this Pod receive traffic?**

Example:

```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 9000
  initialDelaySeconds: 5
  periodSeconds: 10
```

If the Pod is not ready, the Service should not send traffic to it.

---

## Liveness Probe

Liveness answers:

> **Is this container still healthy, or should Kubernetes restart it?**

Example:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 9000
  initialDelaySeconds: 10
  periodSeconds: 10
```

### Difference

```text
Readiness → Should I send traffic to this Pod?

Liveness  → Should I restart this container?
```

---

## Resource Requests & Limits

Requests and limits control how much CPU and memory a container needs and can consume.

Example:

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "256Mi"
```

### Simple meaning

```text
requests → resources the workload asks for

limits   → maximum resources the container can use
```

### Verify

```bash
k describe pod <pod-name> -n argocd-learning
```

Look for the **Requests** and **Limits** section.

---

## Useful Kubernetes Commands

```bash
k get pods -n argocd-learning
k get deployments -n argocd-learning
k get services -n argocd-learning
k get configmaps -n argocd-learning
k get secrets -n argocd-learning
```

Check deployment rollout:

```bash
k rollout status deployment/argocd-app -n argocd-learning
```

Restart deployment:

```bash
k rollout restart deployment/argocd-app -n argocd-learning
```

Describe a Pod:

```bash
k describe pod <pod-name> -n argocd-learning
```

View Pod logs:

```bash
k logs <pod-name> -n argocd-learning
```

Execute a command inside a Pod:

```bash
k exec -n argocd-learning <pod-name> -- <command>
```

## Key Concepts to Remember

```text
ConfigMap  → non-sensitive configuration
Secret     → sensitive configuration

Readiness  → controls whether Pod receives traffic
Liveness   → determines whether container should restart

Requests   → resources requested by the container
Limits     → maximum resources allowed
```
