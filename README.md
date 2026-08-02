# AttritionIQ — Enterprise Cloud-Based Employee Attrition Prediction Platform

[![CI/CD Pipeline](https://github.com/organization/attrition-iq/actions/workflows/ci-cd.yml/badge.svg)](https://github.com/organization/attrition-iq/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AttritionIQ** is an enterprise-grade, cloud-hosted intelligent HR analytics platform powered by **Explainable AI (SHAP)** and **13 Machine Learning algorithms**.

---

## 🌟 Key Features

- 🔮 **13 ML Algorithms**: XGBoost, LightGBM, CatBoost, Random Forest, Neural Networks, SVM, AdaBoost, Extra Trees, KNN, Naive Bayes, Decision Trees, Gradient Boosting, Logistic Regression.
- 💡 **Explainable AI (SHAP)**: Understand individual and global drivers of attrition.
- 🎯 **Actionable Retention Recommendations**: 8-rule AI recommendation engine providing targeted HR interventions.
- 📊 **Real-time Analytics**: 20+ interactive Plotly/Recharts visualizations.
- 📄 **Multi-Format Export**: Automated background generation of PDF, Excel, CSV, and PowerPoint executive reports.
- 🔒 **Enterprise Security**: JWT auth with rotation, Role-Based Access Control (RBAC), bcrypt password encryption, security audit logs, OWASP headers.
- ⚡ **Background Processing**: Celery + Redis for asynchronous training, batch SHAP scans, and scheduled Beat reports.

---

## 🏗️ Architecture

- **Frontend**: React 18, Vite, TypeScript, TailwindCSS, Framer Motion, Recharts, Plotly, Zustand, Axios.
- **Backend API**: FastAPI (Python 3.11), Pydantic v2, Async SQLAlchemy 2.0, PostgreSQL 16.
- **ML Service**: FastAPI, Scikit-Learn, SHAP, XGBoost, LightGBM, CatBoost, WeasyPrint, openpyxl, python-pptx.
- **Async Workers**: Celery + Redis broker & result backend.
- **Proxy**: Nginx reverse proxy with SSL termination and rate limiting.

---

## 🚀 Quick Start

```bash
# 1. Clone repository
git clone https://github.com/organization/attrition-iq.git
cd attrition-iq

# 2. Copy environment file
cp .env.example .env

# 3. Build and launch services
docker-compose up --build -d

# 4. Open applications:
# Web App:  http://localhost:5173
# API Docs: http://localhost:8000/docs
# ML Docs:  http://localhost:8001/docs
```

---

## 📜 Documentation

- [API Specification](docs/API.md)
- [Installation Guide](docs/INSTALL.md)
- [Project Technical Report](docs/project_report.md)
- [Database ER Diagram](docs/ER_diagram.md)
