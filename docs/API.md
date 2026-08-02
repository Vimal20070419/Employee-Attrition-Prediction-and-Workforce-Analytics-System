# AttritionIQ API Specification

## Base URL
- Production: `https://api.attritioniq.com/api/v1`
- Development: `http://localhost:8000/api/v1`

## Authentication
All protected endpoints require a Bearer Token header:
`Authorization: Bearer <your_jwt_access_token>`

---

## Endpoints

### 🔐 Authentication (`/auth`)
- `POST /auth/register` — Create user account
- `POST /auth/login` — Login (OAuth2 Password Form) → returns `access_token`, `refresh_token`
- `POST /auth/refresh` — Issue new access token using refresh token
- `POST /auth/logout` — Revoke refresh token
- `GET /auth/me` — Current user profile

### 👥 Employees (`/employees`)
- `GET /employees` — List employees (params: `page`, `page_size`, `search`, `attrition`)
- `POST /employees` — Create employee record (HR Analyst+)
- `GET /employees/{id}` — Get employee by ID
- `PATCH /employees/{id}` — Update employee record
- `DELETE /employees/{id}` — Soft delete employee (HR Manager+)
- `GET /employees/stats/summary` — KPI summary values

### 🔮 Predictions (`/predictions`)
- `POST /predictions/predict` — Single attrition prediction with SHAP
- `POST /predictions/batch` — Trigger batch prediction (Celery)
- `GET /predictions` — List prediction history
- `POST /predictions/{id}/feedback` — Record actual attrition outcome

### 📁 Datasets (`/datasets`)
- `POST /datasets/upload` — Upload training CSV/Excel file
- `GET /datasets` — List uploaded datasets
- `POST /datasets/{id}/train` — Trigger 13-model training job

### 📊 Analytics (`/analytics`)
- `GET /analytics/dashboard` — Complete dashboard aggregated payload
- `GET /analytics/attrition-trend` — Monthly trend metrics
- `GET /analytics/department-risk` — Department risk index scores
- `GET /analytics/shap-importance` — Global SHAP feature importance

### 📄 Reports (`/reports`)
- `GET /reports` — List generated reports
- `POST /reports/generate` — Generate report (params: `report_type`, `format`, `email_delivery`)
- `GET /reports/{id}/status` — Check report generation status

### ⚙️ Model Registry (`/models`)
- `GET /models` — List model versions
- `GET /models/active` — Current active champion model
- `POST /models/{id}/promote` — Promote model to champion
- `POST /models/{id}/archive` — Archive model

### 🩺 Health (`/health`)
- `GET /health` — Multi-service connectivity check (DB, Redis, ML, Celery)
