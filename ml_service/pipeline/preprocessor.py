"""
AttritionIQ — Data Preprocessor
===================================
Handles all preprocessing steps:
- Missing value imputation
- Duplicate removal
- Outlier detection & capping
- Categorical encoding (OrdinalEncoder + OneHotEncoder)
- Feature scaling (StandardScaler / RobustScaler)
- Class imbalance handling (SMOTE)
- Generates validation report
"""

import json
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from fastapi import APIRouter
from imblearn.over_sampling import SMOTE
from scipy import stats
from sklearn.preprocessing import LabelEncoder, OrdinalEncoder, RobustScaler, StandardScaler

warnings.filterwarnings("ignore")
router = APIRouter()


# IBM HR Dataset column definitions
IBM_CATEGORICAL_COLS = [
    "BusinessTravel", "Department", "EducationField",
    "Gender", "JobRole", "MaritalStatus", "OverTime",
]
IBM_ORDINAL_COLS = {
    "BusinessTravel": ["Non-Travel", "Travel_Rarely", "Travel_Frequently"],
    "Education": [1, 2, 3, 4, 5],
}
IBM_DROP_COLS = ["EmployeeCount", "EmployeeNumber", "Over18", "StandardHours"]
TARGET_COL = "Attrition"


class DataPreprocessor:
    """
    End-to-end preprocessing pipeline for IBM HR Attrition dataset.

    Usage:
        preprocessor = DataPreprocessor()
        X_train, X_test, y_train, y_test, report = preprocessor.fit_transform(df)
    """

    def __init__(self, test_size: float = 0.20, apply_smote: bool = True, random_state: int = 42):
        self.test_size = test_size
        self.apply_smote = apply_smote
        self.random_state = random_state
        self.scaler = RobustScaler()
        self.label_encoders: Dict[str, LabelEncoder] = {}
        self.feature_names: List[str] = []
        self.validation_report: Dict = {}
        self._is_fitted = False

    def load_data(self, file_path: str) -> pd.DataFrame:
        """Load CSV or Excel file into DataFrame."""
        path = Path(file_path)
        if path.suffix.lower() == ".csv":
            df = pd.read_csv(file_path)
        elif path.suffix.lower() in (".xlsx", ".xls"):
            df = pd.read_excel(file_path)
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
        return df

    def validate(self, df: pd.DataFrame) -> Dict:
        """Validate dataset structure and generate validation report."""
        report = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "missing_values": df.isnull().sum().to_dict(),
            "missing_pct": (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
            "duplicate_rows": int(df.duplicated().sum()),
            "target_distribution": {},
            "issues": [],
            "passed": True,
        }

        # Check target column
        if TARGET_COL not in df.columns and "Attrition" not in df.columns:
            report["issues"].append("Missing target column 'Attrition'")
            report["passed"] = False

        # Target distribution
        if TARGET_COL in df.columns:
            vc = df[TARGET_COL].value_counts(normalize=True).round(4) * 100
            report["target_distribution"] = vc.to_dict()

        # Check imbalance
        if TARGET_COL in df.columns:
            vc_raw = df[TARGET_COL].value_counts()
            if "Yes" in vc_raw and "No" in vc_raw:
                ratio = vc_raw["No"] / vc_raw["Yes"]
                if ratio > 5:
                    report["issues"].append(f"High class imbalance (ratio={ratio:.1f}x) — SMOTE will be applied")

        self.validation_report = report
        return report

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates and drop constant columns."""
        original_len = len(df)
        df = df.drop_duplicates()
        if len(df) < original_len:
            self.validation_report["duplicates_removed"] = original_len - len(df)

        # Drop IBM-specific constant columns
        cols_to_drop = [c for c in IBM_DROP_COLS if c in df.columns]
        df = df.drop(columns=cols_to_drop, errors="ignore")

        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values: median for numeric, mode for categorical."""
        for col in df.columns:
            if df[col].isnull().sum() == 0:
                continue
            if df[col].dtype in (np.float64, np.int64):
                df[col] = df[col].fillna(df[col].median())
            else:
                df[col] = df[col].fillna(df[col].mode()[0])
        return df

    def detect_and_cap_outliers(self, df: pd.DataFrame, z_threshold: float = 3.5) -> pd.DataFrame:
        """Cap outliers using Z-score (for numeric columns only)."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        numeric_cols = [c for c in numeric_cols if c != TARGET_COL]
        outlier_count = 0
        for col in numeric_cols:
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            col_outliers = (np.abs(stats.zscore(df[col])) > z_threshold).sum()
            outlier_count += col_outliers
            lower = df[col].quantile(0.01)
            upper = df[col].quantile(0.99)
            df[col] = df[col].clip(lower=lower, upper=upper)
        self.validation_report["outliers_capped"] = int(outlier_count)
        return df

    def encode_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features using LabelEncoder."""
        cat_cols = df.select_dtypes(include=["object"]).columns.tolist()
        if TARGET_COL in cat_cols:
            cat_cols.remove(TARGET_COL)

        for col in cat_cols:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            self.label_encoders[col] = le

        # Encode target
        if TARGET_COL in df.columns:
            df[TARGET_COL] = (df[TARGET_COL] == "Yes").astype(int)

        return df

    def split_features_target(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Separate features (X) and target (y)."""
        y = df[TARGET_COL]
        X = df.drop(columns=[TARGET_COL])
        self.feature_names = X.columns.tolist()
        return X, y

    def scale_features(self, X_train: np.ndarray, X_test: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Apply RobustScaler (handles outliers better than StandardScaler)."""
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        return X_train_scaled, X_test_scaled

    def apply_smote_resampling(
        self, X_train: np.ndarray, y_train: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Apply SMOTE to handle class imbalance on training set only."""
        smote = SMOTE(random_state=self.random_state, k_neighbors=5)
        X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
        self.validation_report["smote_applied"] = True
        self.validation_report["smote_original_size"] = len(y_train)
        self.validation_report["smote_resampled_size"] = len(y_resampled)
        return X_resampled, y_resampled

    def fit_transform(self, file_path: str) -> Tuple:
        """
        Full preprocessing pipeline.

        Returns:
            X_train, X_test, y_train, y_test, feature_names, validation_report
        """
        from sklearn.model_selection import train_test_split

        # 1. Load
        df = self.load_data(file_path)

        # 2. Validate
        self.validate(df)

        # 3. Clean
        df = self.clean(df)

        # 4. Handle missing values
        df = self.handle_missing_values(df)

        # 5. Detect and cap outliers
        df = self.detect_and_cap_outliers(df)

        # 6. Encode
        df = self.encode_features(df)

        # 7. Split
        X, y = self.split_features_target(df)

        # 8. Train/test split (stratified)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=self.test_size, stratify=y, random_state=self.random_state
        )

        # 9. Scale
        X_train_arr = X_train.values
        X_test_arr = X_test.values
        X_train_scaled, X_test_scaled = self.scale_features(X_train_arr, X_test_arr)

        # 10. SMOTE (only on training set)
        if self.apply_smote:
            X_train_scaled, y_train_arr = self.apply_smote_resampling(X_train_scaled, y_train.values)
        else:
            y_train_arr = y_train.values

        self._is_fitted = True
        self.validation_report["final_train_size"] = len(X_train_scaled)
        self.validation_report["final_test_size"] = len(X_test_scaled)
        self.validation_report["feature_count"] = len(self.feature_names)

        return (
            X_train_scaled,
            X_test_scaled,
            y_train_arr,
            y_test.values,
            self.feature_names,
            self.validation_report,
        )

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        """Transform new data using fitted preprocessor (for inference)."""
        if not self._is_fitted:
            raise RuntimeError("Preprocessor not fitted. Call fit_transform() first.")

        # Encode categorical columns
        for col, le in self.label_encoders.items():
            if col in X.columns:
                X[col] = X[col].astype(str).map(
                    lambda val: le.transform([val])[0] if val in le.classes_ else -1
                )

        # Align features
        X = X.reindex(columns=self.feature_names, fill_value=0)
        return self.scaler.transform(X.values)
