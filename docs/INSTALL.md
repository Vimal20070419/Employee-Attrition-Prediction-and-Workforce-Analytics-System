# AttritionIQ Installation & Deployment Guide

## Prerequisites
- Docker & Docker Compose (v2.20+)
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Redis 7+

## Environment Setup
1. Clone the repository.
2. Create `.env` from `.env.example`:
   ```bash
   cp .env.example .env
   ```
3. Set your secret keys (`SECRET_KEY`, `POSTGRES_PASSWORD`).

## Running with Docker Compose
```bash
docker-compose up --build -d
```

## Running Manually for Local Development

### 1. Database Setup
```bash
psql -U postgres -d attrition_db -f database/schema.sql
psql -U postgres -d attrition_db -f database/seed.sql
```

### 2. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 3. Celery Worker & Beat
```bash
celery -A app.celery_app worker --loglevel=info -Q training,reports,shap,notifications
celery -A app.celery_app beat --loglevel=info
```

### 4. ML Service
```bash
cd ml_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
```

### 5. Frontend
```bash
cd frontend
npm install
npm run dev
```
