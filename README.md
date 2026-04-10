# URL Shortener Service

A production-ready URL shortening service built with FastAPI and Python 3.12. Supports custom aliases, link expiry, owner-based listing, and redirect resolution — deployed to Kubernetes via Kustomize overlays.

---

## What it does

| Feature | Detail |
|---------|--------|
| **Shorten URLs** | `POST /links` — generates a 6-char random alias or accepts a custom one |
| **Redirect** | `GET /{alias}` — resolves alias to original URL, enforces expiry |
| **Owner listing** | `GET /links?owner_id=...` — lists all links for a given owner |
| **Expiry** | Optional `expires_at` datetime; expired links return 410 Gone |
| **Validation** | Pydantic rejects non-HTTP/HTTPS URLs and malformed inputs |

---

## Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI 0.115, Uvicorn ASGI |
| ORM | SQLAlchemy 2.0, Alembic migrations |
| Database | PostgreSQL (psycopg2) |
| Process model | Gunicorn (2 workers × 2 threads) |
| Containers | Docker multi-stage, non-root user, read-only filesystem |
| Kubernetes | Kustomize overlays (dev/staging/prod) |
| CI/CD | GitHub Actions → ECR (via reusable workflow) |

---

## Architecture

```
Client → ALB → K8s Service → Pod (Gunicorn + Uvicorn workers)
                                      ↓
                               SQLAlchemy ORM
                                      ↓
                               PostgreSQL (RDS)
```

Timing middleware measures per-request latency. Readiness and liveness probes on `/health` ensure Kubernetes only routes to healthy replicas.

---

## Design decisions

### Non-root container + read-only filesystem

The Docker image creates a dedicated `app` user and sets `USER app`. The Kubernetes `securityContext` adds `readOnlyRootFilesystem: true`, drops all Linux capabilities, and runs as non-root.

This limits blast radius if the app is compromised — an attacker can't write to the container filesystem or escalate privileges.

### Cryptographically secure random aliases

Short codes are generated with `secrets.choice()` rather than `random.choice()`. The difference matters: `random` is seeded by time and predictable; `secrets` uses the OS CSPRNG, making alias enumeration infeasible.

### Kustomize overlays for environment promotion

A single `base/` directory holds the canonical Kubernetes manifests. Each environment (`dev/`, `staging/`, `prod/`) has a `kustomization.yaml` that patches only what differs — image tag, replica count, ingress hostname. No templating language, no Helm chart complexity.

### Rolling deployments with zero downtime

`maxSurge: 1, maxUnavailable: 0` means Kubernetes brings up a new pod before terminating the old one. Combined with readiness probes, this guarantees no traffic is routed to a pod until it's confirmed healthy.

---

## Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

```bash
# Create a short link
curl -X POST http://localhost:8000/links \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/very/long/path", "owner_id": "user-123"}'

# Redirect
curl -L http://localhost:8000/{alias}
```

## Deployment

The GitHub Actions pipeline builds a multi-platform image (amd64 + arm64) and pushes to ECR using OIDC federation — no stored AWS credentials. Apply to Kubernetes with:

```bash
kubectl apply -k k8s/overlays/dev
```
