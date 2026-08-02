"""Unit tests for ML preprocessor and trainer"""
import numpy as np
import pandas as pd
from ml_service.pipeline.feature_engineer import FeatureEngineer


def test_feature_engineer():
    df = pd.DataFrame({
        "MonthlyIncome": [5000, 8000],
        "YearsAtCompany": [2, 5],
        "Age": [30, 45],
        "JobSatisfaction": [3, 4],
        "EnvironmentSatisfaction": [2, 3],
        "OverTime": ["Yes", "No"],
    })
    fe = FeatureEngineer()
    df_transformed = fe.fit_transform(df)

    assert "IncomePerYearAtCompany" in df_transformed.columns
    assert "TenureToAgeRatio" in df_transformed.columns
    assert "SatisfactionIndex" in df_transformed.columns
    assert "OverTimeRiskFactor" in df_transformed.columns
