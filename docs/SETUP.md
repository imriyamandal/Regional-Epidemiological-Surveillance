# Setup Guide

## Step 1: Clone & Configure

```bash
cd dopewis
cp .env.example .env
```

## Step 2: Start PostgreSQL

```bash
docker compose up postgres -d
```

## Step 3: Install Backend Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Step 4: Run API

```bash
uvicorn app.main:app --reload --port 8000
```

Tables are auto-created on startup. Default admin user is seeded.

## Step 5: Train Models

```bash
cd ../ml
pip install -r ../backend/requirements.txt
python -m training.pipeline
```

Training takes 5–15 minutes depending on hardware (TensorFlow optional for LSTM).

## Step 6: Seed Surveillance Data

```bash
cd ..
python scripts/seed_database.py
```

## Step 7: Frontend

```bash
cd frontend
npm install
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

## Step 8: Verify

1. Open http://localhost:3000
2. Login with admin credentials
3. Check dashboard metrics
4. View API docs at http://localhost:8000/docs

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DB connection refused | Ensure PostgreSQL is running on port 5432 |
| Empty dashboard | Run `seed_database.py` |
| No predictions | Run ML pipeline + seed script |
| CORS errors | Add frontend URL to `CORS_ORIGINS` |
