-- ============================================================
-- Seed Data — AttritionIQ Platform
-- ============================================================

-- ============================================================
-- 1. Departments
-- ============================================================
INSERT INTO departments (id, name, code, description, manager_name, location, budget) VALUES
    ('d1000000-0000-0000-0000-000000000001', 'Research & Development', 'R&D', 'Product research, ML engineering & innovation', 'Dr. Sarah Mitchell', 'Block A', 2500000.00),
    ('d1000000-0000-0000-0000-000000000002', 'Sales', 'SALES', 'Global enterprise sales and growth', 'James Carter', 'Block B', 1800000.00),
    ('d1000000-0000-0000-0000-000000000003', 'Human Resources', 'HR', 'Human resources management & talent', 'Linda Thompson', 'Block C', 850000.00),
    ('d1000000-0000-0000-0000-000000000004', 'Finance', 'FIN', 'Corporate finance, FP&A & compliance', 'Robert Chen', 'Block D', 1200000.00),
    ('d1000000-0000-0000-0000-000000000005', 'Marketing', 'MKT', 'Brand and digital growth marketing', 'Priya Sharma', 'Block E', 1100000.00),
    ('d1000000-0000-0000-0000-000000000006', 'Operations', 'OPS', 'Supply chain, logistics and facilities', 'David Kumar', 'Block F', 1400000.00),
    ('d1000000-0000-0000-0000-000000000007', 'IT & Infrastructure', 'IT', 'Cloud infrastructure and security', 'Michael Zhang', 'Block G', 2100000.00)
ON CONFLICT (name) DO NOTHING;

-- ============================================================
-- 2. System Users (password: Admin@123 — bcrypt hashed)
-- ============================================================
INSERT INTO users (
    id, email, username, full_name, hashed_password,
    role, status, is_active, is_verified,
    department, job_title, email_verified_at
) VALUES 
(
    'u1000000-0000-0000-0000-000000000001',
    'admin@attritioniq.com',
    'admin',
    'System Administrator',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCjxm7BXRFL7F.RJ3e3i8Ky',
    'admin',
    'active',
    TRUE,
    TRUE,
    'IT & Infrastructure',
    'System Administrator',
    NOW()
),
(
    'u1000000-0000-0000-0000-000000000002',
    'hr.manager@attritioniq.com',
    'hrmanager',
    'Linda Thompson',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCjxm7BXRFL7F.RJ3e3i8Ky',
    'hr_manager',
    'active',
    TRUE,
    TRUE,
    'Human Resources',
    'HR Manager',
    NOW()
),
(
    'u1000000-0000-0000-0000-000000000003',
    'hr.analyst@attritioniq.com',
    'hranalyst',
    'Alex Rivera',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCjxm7BXRFL7F.RJ3e3i8Ky',
    'hr_analyst',
    'active',
    TRUE,
    TRUE,
    'Human Resources',
    'Senior HR Data Analyst',
    NOW()
),
(
    'u1000000-0000-0000-0000-000000000004',
    'viewer@attritioniq.com',
    'viewer',
    'Department Viewer',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCjxm7BXRFL7F.RJ3e3i8Ky',
    'viewer',
    'active',
    TRUE,
    TRUE,
    'Operations',
    'Business Executive',
    NOW()
)
ON CONFLICT (email) DO NOTHING;

-- ============================================================
-- 3. Uploaded Datasets
-- ============================================================
INSERT INTO uploaded_datasets (
    id, name, description, file_name, file_path, file_size_bytes, file_format,
    version, row_count, column_count, is_validated, is_processed, is_active, uploaded_by
) VALUES (
    'b1000000-0000-0000-0000-000000000001',
    'IBM HR Employee Attrition & Performance Dataset',
    'Complete enterprise historical HR dataset with 1,470 records and 35 employee attributes.',
    'IBM_HR_Employee_Attrition_v1.csv',
    'uploads/datasets/IBM_HR_Employee_Attrition_v1.csv',
    245800,
    'csv',
    'v1.0',
    1470,
    35,
    TRUE,
    TRUE,
    TRUE,
    'u1000000-0000-0000-0000-000000000003'
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 4. ML Model Registry
-- ============================================================
INSERT INTO model_registry (
    id, model_version, experiment_id, algorithm, accuracy, precision_score, recall_score,
    f1_score, auc_roc, auc_pr, log_loss, training_duration_seconds, status, dataset_id, created_by, notes
) VALUES
(
    'm1000000-0000-0000-0000-000000000001',
    'XGBoost-v2.1.0',
    'EXP-2026-901',
    'XGBoost Classifier',
    0.932, 0.895, 0.930, 0.912, 0.945, 0.915, 0.113, 18.5,
    'active',
    'b1000000-0000-0000-0000-000000000001',
    'u1000000-0000-0000-0000-000000000003',
    'Production XGBoost model trained on IBM HR dataset with SHAP feature explainability.'
),
(
    'm1000000-0000-0000-0000-000000000002',
    'LightGBM-v2.0.4',
    'EXP-2026-902',
    'LightGBM Classifier',
    0.918, 0.880, 0.917, 0.898, 0.938, 0.908, 0.115, 12.3,
    'archived',
    'b1000000-0000-0000-0000-000000000001',
    'u1000000-0000-0000-0000-000000000003',
    'LightGBM benchmark model.'
),
(
    'm1000000-0000-0000-0000-000000000003',
    'CatBoost-v1.9.2',
    'EXP-2026-903',
    'CatBoost Classifier',
    0.925, 0.890, 0.921, 0.905, 0.941, 0.911, 0.114, 24.1,
    'archived',
    'b1000000-0000-0000-0000-000000000001',
    'u1000000-0000-0000-0000-000000000003',
    'CatBoost benchmark model with categorical feature handling.'
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 5. Sample Core Employees
-- ============================================================
INSERT INTO employees (
    id, employee_number, age, gender, marital_status, education, education_field,
    distance_from_home, department_id, job_role, job_level, monthly_income, over_time,
    total_working_years, years_at_company, years_in_current_role, years_since_last_promotion,
    job_satisfaction, work_life_balance, performance_rating, attrition, is_active
) VALUES
(
    'e1000000-0000-0000-0000-000000000001',
    'EMP-1001',
    41, 'Female', 'Single', 2, 'Life Sciences', 1,
    'd1000000-0000-0000-0000-000000000001', 'Research Scientist', 2, 5993.00, TRUE,
    8, 6, 4, 0, 4, 1, 3, 'Yes', TRUE
),
(
    'e1000000-0000-0000-0000-000000000002',
    'EMP-1002',
    49, 'Male', 'Married', 1, 'Life Sciences', 8,
    'd1000000-0000-0000-0000-000000000001', 'Research Director', 5, 19098.00, FALSE,
    10, 10, 7, 1, 2, 3, 4, 'No', TRUE
),
(
    'e1000000-0000-0000-0000-000000000003',
    'EMP-1003',
    37, 'Male', 'Single', 4, 'Other', 2,
    'd1000000-0000-0000-0000-000000000001', 'Laboratory Technician', 1, 2090.00, TRUE,
    7, 0, 0, 0, 3, 3, 3, 'Yes', TRUE
),
(
    'e1000000-0000-0000-0000-000000000004',
    'EMP-1004',
    33, 'Female', 'Married', 4, 'Life Sciences', 3,
    'd1000000-0000-0000-0000-000000000002', 'Sales Executive', 2, 2909.00, FALSE,
    8, 8, 7, 3, 3, 3, 3, 'No', TRUE
),
(
    'e1000000-0000-0000-0000-000000000005',
    'EMP-1005',
    27, 'Male', 'Married', 1, 'Medical', 2,
    'd1000000-0000-0000-0000-000000000002', 'Sales Representative', 1, 3468.00, FALSE,
    6, 2, 2, 2, 2, 3, 3, 'No', TRUE
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 6. Sample Predictions
-- ============================================================
INSERT INTO predictions (
    id, employee_id, model_registry_id, input_features, attrition_probability,
    attrition_prediction, risk_level, explanation_text, prediction_type, predicted_by
) VALUES (
    'p1000000-0000-0000-0000-000000000001',
    'e1000000-0000-0000-0000-000000000001',
    'm1000000-0000-0000-0000-000000000001',
    '{"Age": 41, "OverTime": "Yes", "MonthlyIncome": 5993, "JobSatisfaction": 4, "WorkLifeBalance": 1}',
    0.825,
    'Yes',
    'Critical',
    'Employee has a 82.5% risk of attrition driven by excessive OverTime and low WorkLifeBalance.',
    'individual',
    'u1000000-0000-0000-0000-000000000003'
)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 7. Audit Logs
-- ============================================================
INSERT INTO audit_logs (
    id, user_id, action, resource_type, description, ip_address, request_method, response_status
) VALUES
(
    'a1000000-0000-0000-0000-000000000001',
    'u1000000-0000-0000-0000-000000000001',
    'DATABASE_SEED',
    'System',
    'Database successfully populated with production seed dataset.',
    '127.0.0.1',
    'POST',
    200
);
