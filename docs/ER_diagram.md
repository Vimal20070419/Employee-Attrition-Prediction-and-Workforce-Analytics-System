# AttritionIQ Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    USERS ||--o{ EMPLOYEES : "created_by"
    USERS ||--o{ UPLOADED_DATASETS : "uploaded_by"
    USERS ||--o{ PREDICTIONS : "predicted_by"
    USERS ||--o{ AUDIT_LOGS : "user_id"
    USERS ||--o{ REPORTS : "created_by"

    DEPARTMENTS ||--o{ EMPLOYEES : "department_id"

    EMPLOYEES ||--o{ PREDICTIONS : "employee_id"

    UPLOADED_DATASETS ||--o{ MODEL_REGISTRY : "dataset_id"
    UPLOADED_DATASETS ||--o{ TRAINING_HISTORY : "dataset_id"

    MODEL_REGISTRY ||--o{ PREDICTIONS : "model_registry_id"
```

## Entity Table Summary
- **USERS**: System user accounts (role-based access)
- **DEPARTMENTS**: Company organizational units
- **EMPLOYEES**: Employee master records (demographics, job features, status)
- **UPLOADED_DATASETS**: File upload metadata & checksum deduplication
- **MODEL_REGISTRY**: Champion and archived model versions & metrics
- **PREDICTIONS**: Individual predictions, risk levels, and SHAP factors
- **TRAINING_HISTORY**: Log of ML background training runs
- **AUDIT_LOGS**: Security audit trail
- **REPORTS**: Generated multi-format reports
