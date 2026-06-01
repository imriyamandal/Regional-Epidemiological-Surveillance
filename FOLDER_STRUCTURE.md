# Complete Folder Structure

```
dopewis/
├── .env.example
├── docker-compose.yml
├── README.md
├── FOLDER_STRUCTURE.md
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── artifacts/
│   │   ├── best_model.joblib
│   │   ├── model_meta.joblib
│   │   ├── leakage_audit.json
│   │   └── reports/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── router.py
│   │   │       ├── auth.py
│   │   │       ├── analytics.py
│   │   │       ├── alerts.py
│   │   │       ├── explainability.py
│   │   │       ├── reports.py
│   │   │       └── admin.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── security.py
│   │   ├── database/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── models.py
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   └── analytics.py
│   │   └── services/
│   │       ├── auth_service.py
│   │       ├── analytics_service.py
│   │       ├── alert_service.py
│   │       ├── prediction_service.py
│   │       └── report_service.py
│   └── tests/
│       └── test_auth.py
├── ml/
│   ├── data/
│   │   ├── ingestion.py
│   │   └── processed/
│   ├── features/
│   │   └── engineering.py
│   ├── evaluation/
│   │   └── leakage_audit.py
│   ├── models/
│   │   ├── classical.py
│   │   ├── timeseries.py
│   │   ├── deep_learning.py
│   │   └── ensemble.py
│   └── training/
│       ├── pipeline.py
│       └── retrain.py
├── frontend/
│   ├── Dockerfile
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx                 # Landing
│   │   │   ├── login/page.tsx
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── forecasting/page.tsx
│   │   │   ├── risk/page.tsx
│   │   │   ├── map/page.tsx
│   │   │   ├── explainability/page.tsx
│   │   │   ├── reports/page.tsx
│   │   │   ├── alerts/page.tsx
│   │   │   └── admin/page.tsx
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   ├── layout/
│   │   │   ├── dashboard/
│   │   │   └── map/
│   │   └── lib/
│   └── package.json
├── scripts/
│   └── seed_database.py
└── docs/
    ├── ARCHITECTURE.md
    ├── DATABASE.md
    ├── DEPLOYMENT.md
    ├── SETUP.md
    ├── PROJECT_REPORT.md
    └── PRESENTATION.md
```
