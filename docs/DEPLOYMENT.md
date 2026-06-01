# Deployment Guide

## Docker Compose (All Platforms)

```bash
docker compose up -d --build
```

Set production secrets in `.env`:

- `SECRET_KEY` — 64+ character random string
- `POSTGRES_PASSWORD` — strong password
- `SMTP_*` — for email alerts
- `NEXT_PUBLIC_MAPBOX_TOKEN` — optional Mapbox tiles

## Render

1. Create PostgreSQL database
2. Deploy backend as **Web Service** (Dockerfile: `backend/Dockerfile`)
3. Set `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`
4. Deploy frontend with `NEXT_PUBLIC_API_URL=https://your-api.onrender.com`

## Railway

```bash
railway init
railway add -d postgres
railway up
```

Configure environment variables from `.env.example`.

## AWS

| Component | Service |
|-----------|---------|
| API | ECS Fargate + ALB |
| Frontend | Amplify or S3 + CloudFront |
| Database | RDS PostgreSQL |
| MLflow | EC2 or SageMaker |
| Artifacts | S3 bucket |

## Azure

- App Service for FastAPI
- Static Web Apps for Next.js
- Azure Database for PostgreSQL
- Azure ML for experiment tracking (optional MLflow replacement)

## GCP

- Cloud Run for backend/frontend containers
- Cloud SQL PostgreSQL
- Cloud Storage for model artifacts

## Health Checks

- Backend: `GET /health`
- Frontend: root page load
- MLflow: port 5000 UI

## CI/CD Recommendation

```yaml
# .github/workflows/ci.yml
- pytest backend/tests
- npm run build frontend
- docker build validation
```
