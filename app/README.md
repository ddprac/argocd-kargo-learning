# Argo CD + Kargo Learning Project

A hands-on learning project to understand Kubernetes, Kustomize, Helm, Argo CD, and Kargo progressively through a single application.


## Phase 1 — Application

A simple Flask application was created with two endpoints:

```text
GET /
GET /health
```

The application runs locally on port `9000`.

### Create Python Virtual Environment

From the `app/` directory:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Verify Python:

```bash
python --version
which python
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

Current dependency:

```text
Flask
```

### Run Application Locally

```bash
python src/app.py
```

Test the application:

```bash
curl http://localhost:9000/
```

Test the health endpoint:

```bash
curl http://localhost:9000/health
```

## Phase 2 — Docker

The Flask application was containerized using Docker.

### Build Image

```bash
docker build -t argocd-app:v1 .
```

### Run Container

```bash
docker run --rm -p 9000:9000 argocd-app:v1
```

### Test Container

```bash
curl http://localhost:9000/
```

```bash
curl http://localhost:9000/health
```