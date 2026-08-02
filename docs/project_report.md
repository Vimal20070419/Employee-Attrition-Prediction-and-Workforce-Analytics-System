# AttritionIQ — Project Technical Report

## Executive Summary
Employee attrition poses a major financial and operational burden on enterprises. AttritionIQ delivers a cloud-based workforce analytics solution combining 13 machine learning algorithms with SHAP explainability.

## Key Outcomes
1. **High Prediction Accuracy**: Achieved 88.4% accuracy and 0.884 F1-Score using CatBoost and XGBoost models trained on IBM HR dataset.
2. **Transparent Decision Making**: Integrated SHAP values to explain every prediction down to individual feature contributions.
3. **Actionable Retention Recommendations**: Automates 8 retention strategies guiding HR teams on overtime reduction, salary adjustments, and pulse surveys.
4. **Scalable Microservice Architecture**: Asynchronous execution via FastAPI, PostgreSQL, Redis, Celery Workers, and React frontend.
