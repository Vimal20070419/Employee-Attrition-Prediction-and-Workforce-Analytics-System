"""AttritionIQ — Feature Engineering Module"""

import numpy as np
import pandas as pd


class FeatureEngineer:
    """
    Creates domain-specific HR features:
    - IncomePerYearAtCompany
    - TenureToAgeRatio
    - SatisfactionIndex
    - OverTimeRiskFactor
    """

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        if "MonthlyIncome" in df.columns and "YearsAtCompany" in df.columns:
            df["IncomePerYearAtCompany"] = df["MonthlyIncome"] / (df["YearsAtCompany"] + 1)

        if "YearsAtCompany" in df.columns and "Age" in df.columns:
            df["TenureToAgeRatio"] = df["YearsAtCompany"] / (df["Age"] + 1e-5)

        sat_cols = [c for c in ["JobSatisfaction", "EnvironmentSatisfaction", "RelationshipSatisfaction"] if c in df.columns]
        if sat_cols:
            df["SatisfactionIndex"] = df[sat_cols].mean(axis=1)

        if "OverTime" in df.columns and "MonthlyIncome" in df.columns:
            ot_val = df["OverTime"].map(lambda x: 1 if str(x).lower() in ("yes", "true", "1") else 0)
            df["OverTimeRiskFactor"] = ot_val * (10000 / (df["MonthlyIncome"] + 1))

        return df
