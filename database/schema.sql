-- ============================================================
-- AttritionIQ Platform — PostgreSQL Database Schema
-- Version: 1.0.0
-- ============================================================
-- Tables:
--   1. users
--   2. departments
--   3. employees
--   4. uploaded_datasets
--   5. predictions
--   6. training_history
--   7. model_registry
--   8. audit_logs
--   9. reports
-- ============================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for full-text search

-- ============================================================
-- ENUMS
-- ============================================================
CREATE TYPE user_role AS ENUM ('admin', 'hr_manager', 'hr_analyst', 'viewer');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'suspended', 'pending_verification');
CREATE TYPE gender_type AS ENUM ('Male', 'Female', 'Other');
CREATE TYPE attrition_type AS ENUM ('Yes', 'No');
CREATE TYPE risk_level AS ENUM ('Low', 'Medium', 'High', 'Critical');
CREATE TYPE model_status AS ENUM ('active', 'archived', 'training', 'failed');
CREATE TYPE report_format AS ENUM ('pdf', 'excel', 'csv', 'pptx');
CREATE TYPE report_status AS ENUM ('pending', 'generating', 'completed', 'failed');
CREATE TYPE audit_action AS ENUM (
    'login', 'logout', 'register', 'password_reset',
    'create', 'read', 'update', 'delete',
    'upload', 'download', 'train', 'predict',
    'generate_report', 'export'
);

-- ============================================================
-- TABLE 1: users
-- ============================================================
CREATE TABLE users (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email                       VARCHAR(255) NOT NULL UNIQUE,
    username                    VARCHAR(100) NOT NULL UNIQUE,
    full_name                   VARCHAR(255) NOT NULL,
    hashed_password             TEXT NOT NULL,
    role                        user_role NOT NULL DEFAULT 'viewer',
    status                      user_status NOT NULL DEFAULT 'pending_verification',
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    is_verified                 BOOLEAN NOT NULL DEFAULT FALSE,
    avatar_url                  TEXT,
    phone                       VARCHAR(20),
    department                  VARCHAR(100),
    job_title                   VARCHAR(100),

    -- Email verification
    email_verification_token    TEXT,
    email_verified_at           TIMESTAMP WITH TIME ZONE,

    -- Password reset
    password_reset_token        TEXT,
    password_reset_expires_at   TIMESTAMP WITH TIME ZONE,

    -- Refresh token
    refresh_token               TEXT,
    refresh_token_expires_at    TIMESTAMP WITH TIME ZONE,

    -- Preferences
    preferences                 JSONB DEFAULT '{}',

    -- Timestamps
    last_login_at               TIMESTAMP WITH TIME ZONE,
    created_at                  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for users
CREATE INDEX idx_users_email ON users (email);
CREATE INDEX idx_users_username ON users (username);
CREATE INDEX idx_users_role ON users (role);
CREATE INDEX idx_users_status ON users (status);
CREATE INDEX idx_users_created_at ON users (created_at DESC);

-- ============================================================
-- TABLE 2: departments
-- ============================================================
CREATE TABLE departments (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    code            VARCHAR(20) NOT NULL UNIQUE,
    description     TEXT,
    manager_name    VARCHAR(255),
    headcount       INTEGER DEFAULT 0,
    budget          DECIMAL(15,2),
    location        VARCHAR(100),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_departments_name ON departments (name);
CREATE INDEX idx_departments_code ON departments (code);

-- ============================================================
-- TABLE 3: employees
-- ============================================================
CREATE TABLE employees (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_number             VARCHAR(50) UNIQUE,

    -- Personal Info
    age                         INTEGER NOT NULL CHECK (age BETWEEN 18 AND 70),
    gender                      gender_type NOT NULL,
    marital_status              VARCHAR(20) CHECK (marital_status IN ('Single','Married','Divorced')),
    education                   INTEGER CHECK (education BETWEEN 1 AND 5),
    -- 1=Below College, 2=College, 3=Bachelor, 4=Master, 5=Doctor
    education_field             VARCHAR(50),
    distance_from_home          INTEGER CHECK (distance_from_home >= 0),

    -- Job Info
    department_id               UUID REFERENCES departments(id) ON DELETE SET NULL,
    job_role                    VARCHAR(100) NOT NULL,
    job_level                   INTEGER CHECK (job_level BETWEEN 1 AND 5),
    job_involvement             INTEGER CHECK (job_involvement BETWEEN 1 AND 4),

    -- Compensation
    monthly_income              DECIMAL(10,2) NOT NULL CHECK (monthly_income > 0),
    hourly_rate                 DECIMAL(8,2),
    daily_rate                  DECIMAL(8,2),
    monthly_rate                DECIMAL(10,2),
    percent_salary_hike         DECIMAL(5,2) CHECK (percent_salary_hike >= 0),
    stock_option_level          INTEGER CHECK (stock_option_level BETWEEN 0 AND 3),

    -- Work Details
    over_time                   BOOLEAN NOT NULL DEFAULT FALSE,
    business_travel             VARCHAR(50) CHECK (business_travel IN ('Non-Travel','Travel_Rarely','Travel_Frequently')),
    num_companies_worked        INTEGER DEFAULT 0 CHECK (num_companies_worked >= 0),

    -- Tenure & Experience
    total_working_years         INTEGER DEFAULT 0 CHECK (total_working_years >= 0),
    years_at_company            INTEGER DEFAULT 0 CHECK (years_at_company >= 0),
    years_in_current_role       INTEGER DEFAULT 0 CHECK (years_in_current_role >= 0),
    years_since_last_promotion  INTEGER DEFAULT 0 CHECK (years_since_last_promotion >= 0),
    years_with_curr_manager     INTEGER DEFAULT 0 CHECK (years_with_curr_manager >= 0),
    training_times_last_year    INTEGER DEFAULT 0 CHECK (training_times_last_year >= 0),

    -- Satisfaction Scores (1-4 scale)
    environment_satisfaction    INTEGER CHECK (environment_satisfaction BETWEEN 1 AND 4),
    job_satisfaction            INTEGER CHECK (job_satisfaction BETWEEN 1 AND 4),
    relationship_satisfaction   INTEGER CHECK (relationship_satisfaction BETWEEN 1 AND 4),
    work_life_balance           INTEGER CHECK (work_life_balance BETWEEN 1 AND 4),

    -- Performance
    performance_rating          INTEGER CHECK (performance_rating BETWEEN 1 AND 4),

    -- Attrition (actual outcome)
    attrition                   attrition_type,

    -- Metadata
    hire_date                   DATE,
    termination_date            DATE,
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,
    dataset_id                  UUID,  -- FK added after datasets table
    created_by                  UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at                  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes for employees
CREATE INDEX idx_employees_department ON employees (department_id);
CREATE INDEX idx_employees_attrition ON employees (attrition);
CREATE INDEX idx_employees_job_role ON employees (job_role);
CREATE INDEX idx_employees_monthly_income ON employees (monthly_income);
CREATE INDEX idx_employees_age ON employees (age);
CREATE INDEX idx_employees_dataset ON employees (dataset_id);
CREATE INDEX idx_employees_is_active ON employees (is_active);
CREATE INDEX idx_employees_created_at ON employees (created_at DESC);
-- Full-text search on job_role
CREATE INDEX idx_employees_job_role_trgm ON employees USING gin (job_role gin_trgm_ops);

-- ============================================================
-- TABLE 4: uploaded_datasets
-- ============================================================
CREATE TABLE uploaded_datasets (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                VARCHAR(255) NOT NULL,
    description         TEXT,
    file_name           VARCHAR(500) NOT NULL,
    file_path           TEXT NOT NULL,
    file_size_bytes     BIGINT NOT NULL,
    file_format         VARCHAR(10) NOT NULL CHECK (file_format IN ('csv','xlsx','xls')),
    version             VARCHAR(20) NOT NULL DEFAULT 'v1.0',
    row_count           INTEGER,
    column_count        INTEGER,
    columns_info        JSONB DEFAULT '{}',     -- column names, types, nullability
    preprocessing_config JSONB DEFAULT '{}',
    validation_report   JSONB DEFAULT '{}',
    eda_report_path     TEXT,
    checksum            VARCHAR(64),            -- SHA-256 of file
    is_validated        BOOLEAN DEFAULT FALSE,
    is_processed        BOOLEAN DEFAULT FALSE,
    is_active           BOOLEAN DEFAULT TRUE,
    uploaded_by         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_datasets_uploaded_by ON uploaded_datasets (uploaded_by);
CREATE INDEX idx_datasets_created_at ON uploaded_datasets (created_at DESC);
CREATE INDEX idx_datasets_is_active ON uploaded_datasets (is_active);

-- Add FK from employees to datasets
ALTER TABLE employees ADD CONSTRAINT fk_employees_dataset
    FOREIGN KEY (dataset_id) REFERENCES uploaded_datasets(id) ON DELETE SET NULL;

-- ============================================================
-- TABLE 5: model_registry
-- ============================================================
CREATE TABLE model_registry (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version       VARCHAR(50) NOT NULL,
    experiment_id       VARCHAR(100),
    algorithm           VARCHAR(100) NOT NULL,

    -- Metrics
    accuracy            FLOAT CHECK (accuracy BETWEEN 0 AND 1),
    precision_score     FLOAT CHECK (precision_score BETWEEN 0 AND 1),
    recall_score        FLOAT CHECK (recall_score BETWEEN 0 AND 1),
    f1_score            FLOAT CHECK (f1_score BETWEEN 0 AND 1),
    auc_roc             FLOAT CHECK (auc_roc BETWEEN 0 AND 1),
    auc_pr              FLOAT CHECK (auc_pr BETWEEN 0 AND 1),
    log_loss            FLOAT,
    training_duration_seconds FLOAT,

    -- Configuration
    hyperparameters     JSONB DEFAULT '{}',
    feature_names       JSONB DEFAULT '[]',
    training_config     JSONB DEFAULT '{}',
    cv_scores           JSONB DEFAULT '[]',

    -- Storage
    model_path          TEXT,
    scaler_path         TEXT,
    encoder_path        TEXT,
    shap_values_path    TEXT,
    feature_importance_path TEXT,

    -- Status
    status              model_status NOT NULL DEFAULT 'archived',

    -- Relations
    dataset_id          UUID REFERENCES uploaded_datasets(id) ON DELETE SET NULL,
    created_by          UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Notes
    notes               TEXT,
    tags                JSONB DEFAULT '[]',

    training_date       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    promoted_at         TIMESTAMP WITH TIME ZONE,
    archived_at         TIMESTAMP WITH TIME ZONE,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_model_registry_status ON model_registry (status);
CREATE INDEX idx_model_registry_algorithm ON model_registry (algorithm);
CREATE INDEX idx_model_registry_training_date ON model_registry (training_date DESC);
CREATE INDEX idx_model_registry_f1 ON model_registry (f1_score DESC);
CREATE UNIQUE INDEX idx_model_registry_active ON model_registry (status) WHERE status = 'active';

-- ============================================================
-- TABLE 6: training_history
-- ============================================================
CREATE TABLE training_history (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id              VARCHAR(100) NOT NULL,     -- Celery task ID
    dataset_id          UUID REFERENCES uploaded_datasets(id) ON DELETE SET NULL,
    model_registry_id   UUID REFERENCES model_registry(id) ON DELETE SET NULL,

    -- Configuration
    algorithms_trained  JSONB DEFAULT '[]',
    training_config     JSONB DEFAULT '{}',

    -- Status
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending','running','completed','failed','cancelled')),
    started_at          TIMESTAMP WITH TIME ZONE,
    completed_at        TIMESTAMP WITH TIME ZONE,
    duration_seconds    FLOAT,

    -- Results
    best_algorithm      VARCHAR(100),
    best_f1_score       FLOAT,
    all_results         JSONB DEFAULT '{}',
    error_message       TEXT,
    log_output          TEXT,

    triggered_by        UUID REFERENCES users(id) ON DELETE SET NULL,
    is_auto_retrain     BOOLEAN DEFAULT FALSE,
    created_at          TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_training_history_status ON training_history (status);
CREATE INDEX idx_training_history_dataset ON training_history (dataset_id);
CREATE INDEX idx_training_history_created ON training_history (created_at DESC);
CREATE INDEX idx_training_history_job ON training_history (job_id);

-- ============================================================
-- TABLE 7: predictions
-- ============================================================
CREATE TABLE predictions (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id             UUID REFERENCES employees(id) ON DELETE SET NULL,
    model_registry_id       UUID REFERENCES model_registry(id) ON DELETE SET NULL,

    -- Input features snapshot
    input_features          JSONB NOT NULL DEFAULT '{}',

    -- Prediction Results
    attrition_probability   FLOAT NOT NULL CHECK (attrition_probability BETWEEN 0 AND 1),
    attrition_prediction    attrition_type NOT NULL,
    risk_level              risk_level NOT NULL,

    -- Explanation
    shap_values             JSONB DEFAULT '{}',
    top_risk_factors        JSONB DEFAULT '[]',
    retention_recommendations JSONB DEFAULT '[]',
    explanation_text        TEXT,

    -- SHAP artifacts
    shap_plot_path          TEXT,
    waterfall_plot_path     TEXT,

    -- Meta
    prediction_type         VARCHAR(20) DEFAULT 'individual'
                                CHECK (prediction_type IN ('individual','batch','scheduled')),
    batch_id                UUID,
    predicted_by            UUID REFERENCES users(id) ON DELETE SET NULL,
    is_verified             BOOLEAN DEFAULT FALSE,
    actual_attrition        attrition_type,   -- for feedback loop
    feedback_given_at       TIMESTAMP WITH TIME ZONE,

    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_predictions_employee ON predictions (employee_id);
CREATE INDEX idx_predictions_model ON predictions (model_registry_id);
CREATE INDEX idx_predictions_risk ON predictions (risk_level);
CREATE INDEX idx_predictions_probability ON predictions (attrition_probability DESC);
CREATE INDEX idx_predictions_created ON predictions (created_at DESC);
CREATE INDEX idx_predictions_batch ON predictions (batch_id);

-- ============================================================
-- TABLE 8: reports
-- ============================================================
CREATE TABLE reports (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title           VARCHAR(500) NOT NULL,
    description     TEXT,
    report_type     VARCHAR(50) NOT NULL,   -- 'attrition_summary','eda','model_performance','prediction_batch'
    format          report_format NOT NULL,
    status          report_status NOT NULL DEFAULT 'pending',

    -- File
    file_path       TEXT,
    file_size_bytes BIGINT,
    download_url    TEXT,

    -- Scheduling
    is_scheduled    BOOLEAN DEFAULT FALSE,
    schedule_cron   VARCHAR(100),           -- cron expression
    next_run_at     TIMESTAMP WITH TIME ZONE,
    last_run_at     TIMESTAMP WITH TIME ZONE,

    -- Email delivery
    email_delivery  BOOLEAN DEFAULT FALSE,
    recipient_emails JSONB DEFAULT '[]',

    -- Config
    filters         JSONB DEFAULT '{}',
    job_id          VARCHAR(100),           -- Celery task ID
    error_message   TEXT,

    -- Meta
    dataset_id      UUID REFERENCES uploaded_datasets(id) ON DELETE SET NULL,
    model_id        UUID REFERENCES model_registry(id) ON DELETE SET NULL,
    created_by      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_reports_created_by ON reports (created_by);
CREATE INDEX idx_reports_status ON reports (status);
CREATE INDEX idx_reports_created ON reports (created_at DESC);
CREATE INDEX idx_reports_scheduled ON reports (is_scheduled) WHERE is_scheduled = TRUE;

-- ============================================================
-- TABLE 9: audit_logs
-- ============================================================
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id) ON DELETE SET NULL,
    action          audit_action NOT NULL,
    resource_type   VARCHAR(100),           -- 'employee', 'prediction', 'model', etc.
    resource_id     VARCHAR(255),
    description     TEXT,
    ip_address      INET,
    user_agent      TEXT,
    request_method  VARCHAR(10),
    request_path    TEXT,
    response_status INTEGER,
    metadata        JSONB DEFAULT '{}',
    is_suspicious   BOOLEAN DEFAULT FALSE,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user ON audit_logs (user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs (action);
CREATE INDEX idx_audit_logs_created ON audit_logs (created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX idx_audit_logs_ip ON audit_logs (ip_address);
CREATE INDEX idx_audit_logs_suspicious ON audit_logs (is_suspicious) WHERE is_suspicious = TRUE;

-- ============================================================
-- AUTO-UPDATE TRIGGERS
-- ============================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to all tables with updated_at
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_departments_updated_at
    BEFORE UPDATE ON departments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_employees_updated_at
    BEFORE UPDATE ON employees FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_datasets_updated_at
    BEFORE UPDATE ON uploaded_datasets FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_model_registry_updated_at
    BEFORE UPDATE ON model_registry FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_reports_updated_at
    BEFORE UPDATE ON reports FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- VIEWS
-- ============================================================

-- Active model view
CREATE VIEW v_active_model AS
    SELECT * FROM model_registry WHERE status = 'active' LIMIT 1;

-- Attrition summary per department
CREATE VIEW v_department_attrition AS
    SELECT
        d.name AS department,
        COUNT(e.id) AS total_employees,
        COUNT(CASE WHEN e.attrition = 'Yes' THEN 1 END) AS attrition_count,
        ROUND(
            COUNT(CASE WHEN e.attrition = 'Yes' THEN 1 END)::DECIMAL /
            NULLIF(COUNT(e.id), 0) * 100, 2
        ) AS attrition_rate_pct,
        ROUND(AVG(e.monthly_income)::DECIMAL, 2) AS avg_monthly_income,
        ROUND(AVG(e.age)::DECIMAL, 1) AS avg_age
    FROM employees e
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE e.is_active = TRUE
    GROUP BY d.name
    ORDER BY attrition_rate_pct DESC;

-- High-risk employees (latest predictions > 70%)
CREATE VIEW v_high_risk_employees AS
    SELECT
        e.id, e.employee_number, e.age, e.gender, e.job_role,
        d.name AS department,
        e.monthly_income, e.years_at_company,
        p.attrition_probability, p.risk_level,
        p.top_risk_factors, p.retention_recommendations,
        p.created_at AS predicted_at
    FROM predictions p
    JOIN employees e ON p.employee_id = e.id
    LEFT JOIN departments d ON e.department_id = d.id
    WHERE p.attrition_probability >= 0.70
      AND p.id = (
          SELECT id FROM predictions p2
          WHERE p2.employee_id = e.id
          ORDER BY p2.created_at DESC LIMIT 1
      )
    ORDER BY p.attrition_probability DESC;

-- ============================================================
-- COMMENTS
-- ============================================================
COMMENT ON TABLE users IS 'Platform users with role-based access control';
COMMENT ON TABLE departments IS 'Organizational department master table';
COMMENT ON TABLE employees IS 'Employee records with IBM attrition dataset fields';
COMMENT ON TABLE uploaded_datasets IS 'Versioned dataset uploads with validation metadata';
COMMENT ON TABLE model_registry IS 'ML model versions with metrics and status tracking';
COMMENT ON TABLE training_history IS 'Training job execution history linked to Celery tasks';
COMMENT ON TABLE predictions IS 'Individual and batch attrition predictions with SHAP explanations';
COMMENT ON TABLE reports IS 'Generated report metadata with scheduling and email delivery';
COMMENT ON TABLE audit_logs IS 'Security and change audit trail for all user actions';
