"""
AttritionIQ — ML Service Main Application
============================================
FastAPI app exposing training, prediction, SHAP, EDA, and report endpoints.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pipeline.preprocessor import router as preprocess_router
from pipeline.trainer import router as train_router
from prediction.predictor import router as predict_router
from explainability.shap_explainer import router as shap_router
from eda.eda_generator import router as eda_router
from reports.report_generator import router as reports_router


app = FastAPI(
    title="AttritionIQ — ML Service",
    description="Machine Learning microservice: training, prediction, SHAP, EDA, reports",
    version="1.0.0",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(train_router, prefix="/train", tags=["Training"])
app.include_router(predict_router, prefix="", tags=["Prediction"])
app.include_router(shap_router, prefix="/shap", tags=["SHAP"])
app.include_router(eda_router, prefix="/eda", tags=["EDA"])
app.include_router(reports_router, prefix="/reports", tags=["Reports"])


@app.get("/health")
async def health():
    import os
    return {
        "status": "healthy",
        "service": "ml_service",
        "models_dir": os.path.exists("/app/artifacts/models"),
        "version": "1.0.0",
    }
