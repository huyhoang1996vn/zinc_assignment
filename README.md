# Project Design Document

## 1. High-Level Architecture Diagram

```mermaid
graph TD
    User[User / Client]
    User -->|HTTP| Nginx[Reverse Proxy (optional)]
    Nginx -->|HTTP| Gunicorn[Gunicorn + Uvicorn Workers]
    Gunicorn -->|ASGI| FastAPI[FastAPI App]
    FastAPI -->|ORM| MySQL[MySQL Database]
    FastAPI -->|Logging| Log[Log Aggregator]
    FastAPI -->|Metrics| Metrics[Monitoring]
```

## 2. API & Data Model Sketch

### Example API Endpoints
- `POST /items/` — Create an item
- `GET /items/{id}` — Retrieve item by ID
- `PUT /items/{id}` — Update item
- `DELETE /items/{id}` — Delete item

### Data Model (SQLModel Example)
```python
from sqlmodel import SQLModel, Field

class Item(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    price: float
    in_stock: bool = True
```

## 3. Infrastructure Choices
- **Language/Framework:** Python, FastAPI, SQLModel
- **Database:** MySQL (managed or self-hosted)
- **Containerization:** Docker
- **Orchestration:** (Optional) Kubernetes or Docker Compose
- **CI/CD:** GitHub Actions
- **Testing:** Pytest
- **Migrations:** Alembic

## 4. Scaling & Resilience Strategy
- **Horizontal Scaling:** Multiple Gunicorn workers and/or containers
- **Stateless API:** Enables easy scaling
- **Database:** Use managed MySQL with replication and backups
- **Health Checks:** Liveness/readiness endpoints for orchestration
- **Graceful Shutdown:** Use FastAPI's lifespan events

## 5. CI/CD & Rollback Plan
- **CI:** GitHub Actions workflow for build, migration, and test on push to `main`
- **CD:** (Optional) Deploy to staging/production via GitHub Actions or external tool
- **Rollback:** Use tagged Docker images; revert to previous tag on failure
- **Migration Safety:** Run migrations as a separate step before app start

## 6. Observability & SRE
- **Logging:** Loguru for structured logs, aggregated via ELK/Cloud logging
- **Metrics:** Integrate Prometheus/Grafana or use cloud monitoring
- **Tracing:** (Optional) OpenTelemetry integration
- **Alerting:** Set up alerts on error rates, latency, and resource usage

## 7. Trade-Off Discussion
- **Pros:**
    - FastAPI is async, modern, and easy to use
    - Docker ensures consistent environments
    - GitHub Actions provides simple, integrated CI/CD
    - SQLModel offers type safety and easy migrations
- **Cons:**
    - MySQL may not scale as easily as NoSQL for some workloads
    - Running migrations on app startup can be risky in multi-instance deployments (should be a separate job)

---
*This document provides a concise overview. For more details, see the project README and codebase.* 