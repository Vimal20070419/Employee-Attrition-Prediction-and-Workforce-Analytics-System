"""
AttritionIQ — Database Seeder Script
======================================
Populates database tables with rich, realistic enterprise data for testing,
development, and demo purposes.

Usage:
    cd backend
    python -m app.utils.seeder
"""

import asyncio
import random
import uuid
from datetime import datetime, timedelta, date

from sqlalchemy.future import select
from sqlalchemy import delete

from app.database import AsyncSessionLocal, engine, create_tables
from app.models.user import User
from app.models.employee import Employee
from app.models.models import (
    Department, UploadedDataset, ModelRegistry,
    TrainingHistory, Prediction, Report, AuditLog
)

# Password hash for 'Admin@123'
DEFAULT_PASSWORD_HASH = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQyCjxm7BXRFL7F.RJ3e3i8Ky"

DEPARTMENTS_DATA = [
    {"name": "Research & Development", "code": "R&D", "description": "Product research, ML engineering & innovation", "manager_name": "Dr. Sarah Mitchell", "location": "Building A", "budget": 2500000.0},
    {"name": "Sales", "code": "SALES", "description": "Global enterprise sales & client growth", "manager_name": "James Carter", "location": "Building B", "budget": 1800000.0},
    {"name": "Human Resources", "code": "HR", "description": "Talent acquisition & employee experience", "manager_name": "Linda Thompson", "location": "Building C", "budget": 850000.0},
    {"name": "Finance", "code": "FIN", "description": "Corporate finance, FP&A & compliance", "manager_name": "Robert Chen", "location": "Building D", "budget": 1200000.0},
    {"name": "Marketing", "code": "MKT", "description": "Brand strategy, growth & demand gen", "manager_name": "Priya Sharma", "location": "Building E", "budget": 1100000.0},
    {"name": "Operations", "code": "OPS", "description": "Supply chain, logistics & facilities", "manager_name": "David Kumar", "location": "Building F", "budget": 1400000.0},
    {"name": "IT & Infrastructure", "code": "IT", "description": "Cloud security, DevOps & internal IT", "manager_name": "Michael Zhang", "location": "Building G", "budget": 2100000.0},
]

ROLES_BY_DEPT = {
    "Research & Development": ["Research Scientist", "Software Engineer", "Laboratory Technician", "Research Director", "Senior ML Engineer"],
    "Sales": ["Sales Executive", "Sales Representative", "Account Manager", "Regional Sales Manager"],
    "Human Resources": ["HR Specialist", "Talent Acquisition Partner", "HR Business Partner", "Compensation Analyst"],
    "Finance": ["Financial Analyst", "Senior Accountant", "Finance Manager", "Auditor"],
    "Marketing": ["Marketing Specialist", "Digital Lead", "Brand Director", "Content Strategist"],
    "Operations": ["Operations Manager", "Logistics Coordinator", "Supply Lead"],
    "IT & Infrastructure": ["Systems Administrator", "DevOps Engineer", "Cloud Architect", "Security Analyst"]
}

EDUCATION_FIELDS = ["Life Sciences", "Medical", "Marketing", "Technical Degree", "Human Resources", "Other"]

FIRST_NAMES = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa", "Matthew", "Betty", "Anthony", "Margaret", "Donald", "Sandra", "Mark", "Ashley", "Paul", "Kimberly", "Steven", "Emily", "Andrew", "Donna", "Kenneth", "Michelle", "Joshua", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa", "Edward", "Deborah"]
LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell", "Carter", "Roberts"]

ALGORITHMS = [
    {"name": "XGBoost Classifier", "version": "v2.1.0", "f1": 0.912, "roc_auc": 0.945, "precision": 0.895, "recall": 0.930, "status": "active"},
    {"name": "LightGBM Classifier", "version": "v2.0.4", "f1": 0.898, "roc_auc": 0.938, "precision": 0.880, "recall": 0.917, "status": "archived"},
    {"name": "CatBoost Classifier", "version": "v1.9.2", "f1": 0.905, "roc_auc": 0.941, "precision": 0.890, "recall": 0.921, "status": "archived"},
    {"name": "Random Forest Classifier", "version": "v1.8.0", "f1": 0.875, "roc_auc": 0.915, "precision": 0.860, "recall": 0.891, "status": "archived"},
    {"name": "Extra Trees Classifier", "version": "v1.5.0", "f1": 0.862, "roc_auc": 0.902, "precision": 0.850, "recall": 0.874, "status": "archived"},
    {"name": "Deep Neural Network (MLP)", "version": "v1.4.1", "f1": 0.884, "roc_auc": 0.920, "precision": 0.871, "recall": 0.898, "status": "archived"},
    {"name": "Gradient Boosting Classifier", "version": "v1.3.0", "f1": 0.869, "roc_auc": 0.908, "precision": 0.855, "recall": 0.883, "status": "archived"},
    {"name": "AdaBoost Classifier", "version": "v1.2.0", "f1": 0.841, "roc_auc": 0.885, "precision": 0.830, "recall": 0.852, "status": "archived"},
    {"name": "Support Vector Machine (SVM)", "version": "v1.1.0", "f1": 0.835, "roc_auc": 0.872, "precision": 0.820, "recall": 0.851, "status": "archived"},
    {"name": "Logistic Regression", "version": "v1.0.0", "f1": 0.812, "roc_auc": 0.854, "precision": 0.795, "recall": 0.830, "status": "archived"},
    {"name": "K-Nearest Neighbors (KNN)", "version": "v0.9.0", "f1": 0.785, "roc_auc": 0.810, "precision": 0.770, "recall": 0.801, "status": "archived"},
    {"name": "Naive Bayes Classifier", "version": "v0.8.0", "f1": 0.760, "roc_auc": 0.792, "precision": 0.745, "recall": 0.776, "status": "archived"},
    {"name": "Decision Tree Classifier", "version": "v0.7.0", "f1": 0.742, "roc_auc": 0.765, "precision": 0.720, "recall": 0.766, "status": "archived"},
]

FEATURE_NAMES = [
    "Age", "OverTime", "MonthlyIncome", "TotalWorkingYears", "YearsAtCompany",
    "StockOptionLevel", "JobSatisfaction", "EnvironmentSatisfaction", "WorkLifeBalance",
    "DistanceFromHome", "NumCompaniesWorked", "JobLevel", "YearsInCurrentRole",
    "YearsSinceLastPromotion", "YearsWithCurrManager", "PercentSalaryHike"
]

RECOMMENDATION_TEMPLATES = [
    "Schedule 1-on-1 retention review regarding workload and overtime compensation.",
    "Review compensation benchmarking — monthly income is 18% below market average for role level.",
    "Offer career growth path or promotion review; employee has been in current role for over 4 years.",
    "Provide flexible working hours or remote work options to improve WorkLifeBalance score.",
    "Grant equity/stock options refresh to align long-term incentives.",
    "Assign a senior mentor and provide leadership development training modules."
]


async def seed_database():
    """Execute complete database seeding process."""
    print("[SEED] Starting AttritionIQ Database Seeding...")

    async with AsyncSessionLocal() as session:
        # Create schema if not exists
        await create_tables()

        # 1. Seed Users
        print("[USERS] Seeding Users...")
        admin_user = User(
            id=uuid.uuid4(),
            email="admin@attritioniq.com",
            username="admin",
            full_name="System Administrator",
            hashed_password=DEFAULT_PASSWORD_HASH,
            role="admin",
            status="active",
            is_active=True,
            is_verified=True,
            department="IT & Infrastructure",
            job_title="System Administrator",
            email_verified_at=datetime.utcnow()
        )
        hr_manager = User(
            id=uuid.uuid4(),
            email="hr.manager@attritioniq.com",
            username="hrmanager",
            full_name="Linda Thompson",
            hashed_password=DEFAULT_PASSWORD_HASH,
            role="hr_manager",
            status="active",
            is_active=True,
            is_verified=True,
            department="Human Resources",
            job_title="HR Manager",
            email_verified_at=datetime.utcnow()
        )
        hr_analyst = User(
            id=uuid.uuid4(),
            email="hr.analyst@attritioniq.com",
            username="hranalyst",
            full_name="Alex Rivera",
            hashed_password=DEFAULT_PASSWORD_HASH,
            role="hr_analyst",
            status="active",
            is_active=True,
            is_verified=True,
            department="Human Resources",
            job_title="Senior HR Data Analyst",
            email_verified_at=datetime.utcnow()
        )
        viewer_user = User(
            id=uuid.uuid4(),
            email="viewer@attritioniq.com",
            username="viewer",
            full_name="Department Viewer",
            hashed_password=DEFAULT_PASSWORD_HASH,
            role="viewer",
            status="active",
            is_active=True,
            is_verified=True,
            department="Operations",
            job_title="Business Executive",
            email_verified_at=datetime.utcnow()
        )

        session.add_all([admin_user, hr_manager, hr_analyst, viewer_user])
        await session.flush()

        # 2. Seed Departments
        print("[DEPTS] Seeding Departments...")
        dept_objs = []
        for dept_info in DEPARTMENTS_DATA:
            dept = Department(
                id=uuid.uuid4(),
                name=dept_info["name"],
                code=dept_info["code"],
                description=dept_info["description"],
                manager_name=dept_info["manager_name"],
                location=dept_info["location"],
                budget=dept_info["budget"],
                headcount=0,
                is_active=True
            )
            dept_objs.append(dept)
            session.add(dept)
        await session.flush()

        # 3. Seed Uploaded Dataset Record
        print("[DATASETS] Seeding Uploaded Dataset Record...")
        sample_dataset = UploadedDataset(
            id=uuid.uuid4(),
            name="IBM HR Employee Attrition & Performance Dataset",
            description="Complete enterprise historical HR dataset with 1,470 records and 35 employee attributes.",
            file_name="IBM_HR_Employee_Attrition_v1.csv",
            file_path="uploads/datasets/IBM_HR_Employee_Attrition_v1.csv",
            file_size_bytes=245800,
            file_format="csv",
            version="v1.0",
            row_count=1470,
            column_count=35,
            columns_info={"Age": "int", "Attrition": "string", "BusinessTravel": "string", "MonthlyIncome": "float", "OverTime": "string"},
            is_validated=True,
            is_processed=True,
            is_active=True,
            uploaded_by=hr_analyst.id
        )
        session.add(sample_dataset)
        await session.flush()

        # 4. Seed Employees (210 realistic records)
        print("[EMPLOYEES] Seeding 210 Employees...")
        employees_list = []
        random.seed(42)  # Deterministic seed for repeatable test data

        emp_counter = 1001
        for dept in dept_objs:
            roles_in_dept = ROLES_BY_DEPT.get(dept.name, ["Staff Specialist"])
            # Generate ~30 employees per department
            dept_emp_count = 30
            for _ in range(dept_emp_count):
                gender = random.choice(["Male", "Female"])
                age = random.randint(22, 60)
                total_working_years = max(1, age - 21 - random.randint(0, 3))
                years_at_company = min(total_working_years, random.randint(1, 20))
                years_in_role = min(years_at_company, random.randint(0, 10))
                years_since_promo = min(years_at_company, random.randint(0, 7))
                years_with_mgr = min(years_at_company, random.randint(0, 8))

                job_role = random.choice(roles_in_dept)
                job_level = random.randint(1, 5)
                monthly_income = float(random.randint(2500, 19500) + (job_level * 2500))
                over_time = random.choice([True, False, False, False])  # 25% overtime
                
                env_sat = random.randint(1, 4)
                job_sat = random.randint(1, 4)
                work_life = random.randint(1, 4)
                
                if (job_sat <= 2 or work_life == 1) and over_time:
                    attrition = "Yes" if random.random() < 0.65 else "No"
                else:
                    attrition = "Yes" if random.random() < 0.12 else "No"

                emp = Employee(
                    id=uuid.uuid4(),
                    employee_number=f"EMP-{emp_counter}",
                    age=age,
                    gender=gender,
                    marital_status=random.choice(["Single", "Married", "Divorced"]),
                    education=random.randint(1, 5),
                    education_field=random.choice(EDUCATION_FIELDS),
                    distance_from_home=random.randint(1, 29),
                    department_id=dept.id,
                    job_role=job_role,
                    job_level=job_level,
                    job_involvement=random.randint(1, 4),
                    monthly_income=monthly_income,
                    hourly_rate=float(random.randint(30, 100)),
                    daily_rate=float(random.randint(400, 1500)),
                    monthly_rate=float(random.randint(10000, 28000)),
                    percent_salary_hike=float(random.randint(11, 25)),
                    stock_option_level=random.randint(0, 3),
                    over_time=over_time,
                    business_travel=random.choice(["Travel_Rarely", "Travel_Frequently", "Non-Travel"]),
                    num_companies_worked=random.randint(0, 9),
                    total_working_years=total_working_years,
                    years_at_company=years_at_company,
                    years_in_current_role=years_in_role,
                    years_since_last_promotion=years_since_promo,
                    years_with_curr_manager=years_with_mgr,
                    training_times_last_year=random.randint(0, 6),
                    environment_satisfaction=env_sat,
                    job_satisfaction=job_sat,
                    relationship_satisfaction=random.randint(1, 4),
                    work_life_balance=work_life,
                    performance_rating=random.choice([3, 3, 3, 4]),
                    attrition=attrition,
                    hire_date=date.today() - timedelta(days=years_at_company * 365),
                    is_active=True,
                    dataset_id=sample_dataset.id,
                    created_by=hr_analyst.id
                )
                employees_list.append(emp)
                session.add(emp)
                emp_counter += 1

            dept.headcount = dept_emp_count

        await session.flush()

        # 5. Seed Model Registry (13 Algorithms)
        print("[MODELS] Seeding 13 ML Algorithms in Model Registry...")
        model_objs = []
        active_model = None

        for algo in ALGORITHMS:
            model = ModelRegistry(
                id=uuid.uuid4(),
                model_version=f"{algo['name'].split()[0]}-{algo['version']}",
                experiment_id=f"EXP-2026-{random.randint(100, 999)}",
                algorithm=algo["name"],
                accuracy=round(algo["f1"] + 0.02, 3),
                precision_score=algo["precision"],
                recall_score=algo["recall"],
                f1_score=algo["f1"],
                auc_roc=algo["roc_auc"],
                auc_pr=round(algo["roc_auc"] - 0.03, 3),
                log_loss=round(0.25 - (algo["f1"] * 0.15), 3),
                training_duration_seconds=round(random.uniform(4.5, 45.2), 2),
                hyperparameters={
                    "n_estimators": 200, "max_depth": 6, "learning_rate": 0.05,
                    "subsample": 0.8, "colsample_bytree": 0.8
                },
                feature_names=FEATURE_NAMES,
                status=algo["status"],
                dataset_id=sample_dataset.id,
                created_by=hr_analyst.id,
                notes=f"Tuned {algo['name']} trained on 80% split of IBM HR dataset with 10-fold cross validation.",
                tags=["production", "shap-enabled", "v2.0"]
            )
            if algo["status"] == "active":
                model.promoted_at = datetime.utcnow() - timedelta(days=15)
                active_model = model
            model_objs.append(model)
            session.add(model)

        await session.flush()

        # 6. Seed Predictions with SHAP values & Risk Levels
        print("[PREDICTIONS] Seeding 60 Predictions with SHAP Explainability & Risk Levels...")
        prediction_objs = []
        
        for idx, emp in enumerate(employees_list[:60]):
            prob = 0.15
            shap_impacts = {}
            top_factors = []
            
            if emp.over_time:
                prob += 0.25
                shap_impacts["OverTime"] = +0.25
                top_factors.append({"feature": "OverTime", "value": "Yes", "impact": "+25% Risk"})

            if (emp.job_satisfaction or 3) <= 2:
                prob += 0.20
                shap_impacts["JobSatisfaction"] = +0.20
                top_factors.append({"feature": "JobSatisfaction", "value": emp.job_satisfaction, "impact": "+20% Risk"})

            if float(emp.monthly_income) < 4500:
                prob += 0.18
                shap_impacts["MonthlyIncome"] = +0.18
                top_factors.append({"feature": "MonthlyIncome", "value": f"${emp.monthly_income:,.0f}", "impact": "+18% Risk"})

            if (emp.years_since_last_promotion or 0) >= 4:
                prob += 0.12
                shap_impacts["YearsSinceLastPromotion"] = +0.12
                top_factors.append({"feature": "YearsSinceLastPromotion", "value": f"{emp.years_since_last_promotion} yrs", "impact": "+12% Risk"})

            if (emp.work_life_balance or 3) <= 2:
                prob += 0.15
                shap_impacts["WorkLifeBalance"] = +0.15
                top_factors.append({"feature": "WorkLifeBalance", "value": emp.work_life_balance, "impact": "+15% Risk"})

            prob = round(min(0.98, max(0.02, prob)), 3)

            if prob >= 0.70:
                risk_level = "Critical"
                pred_type = "Yes"
            elif prob >= 0.45:
                risk_level = "High"
                pred_type = "Yes"
            elif prob >= 0.25:
                risk_level = "Medium"
                pred_type = "No"
            else:
                risk_level = "Low"
                pred_type = "No"

            recs = random.sample(RECOMMENDATION_TEMPLATES, k=min(2, len(RECOMMENDATION_TEMPLATES)))

            prediction = Prediction(
                id=uuid.uuid4(),
                employee_id=emp.id,
                model_registry_id=active_model.id if active_model else model_objs[0].id,
                input_features={
                    "Age": emp.age,
                    "JobRole": emp.job_role,
                    "MonthlyIncome": float(emp.monthly_income),
                    "OverTime": "Yes" if emp.over_time else "No",
                    "JobSatisfaction": emp.job_satisfaction,
                    "WorkLifeBalance": emp.work_life_balance,
                    "YearsAtCompany": emp.years_at_company
                },
                attrition_probability=prob,
                attrition_prediction=pred_type,
                risk_level=risk_level,
                shap_values=shap_impacts,
                top_risk_factors=top_factors,
                retention_recommendations=recs,
                explanation_text=f"Employee has a {prob*100:.1f}% risk of attrition driven primarily by {', '.join([f['feature'] for f in top_factors]) if top_factors else 'baseline parameters'}.",
                prediction_type="individual",
                predicted_by=hr_analyst.id,
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 120))
            )
            prediction_objs.append(prediction)
            session.add(prediction)

        await session.flush()

        # 7. Seed Reports
        print("[REPORTS] Seeding Executive Reports...")
        reports_data = [
            {"title": "Q3 Executive Attrition Risk Summary", "type": "attrition_summary", "format": "pdf", "status": "completed", "url": "/reports/q3_attrition_summary.pdf", "size": 1845000},
            {"title": "High Risk Employee Retention Roster", "type": "high_risk_list", "format": "excel", "status": "completed", "url": "/reports/high_risk_roster.xlsx", "size": 420000},
            {"title": "Departmental SHAP Feature Importance Breakdown", "type": "shap_insights", "format": "pptx", "status": "completed", "url": "/reports/department_shap_breakdown.pptx", "size": 3120000},
            {"title": "Monthly Attrition Data Export", "type": "full_export", "format": "csv", "status": "completed", "url": "/reports/monthly_export.csv", "size": 512000},
            {"title": "Scheduled HR Leader Weekly Risk Digest", "type": "scheduled_digest", "format": "pdf", "status": "completed", "url": "/reports/weekly_digest.pdf", "size": 950000, "scheduled": True},
        ]

        for rep in reports_data:
            report_obj = Report(
                id=uuid.uuid4(),
                title=rep["title"],
                description=f"Generated report providing {rep['type']} analysis for HR leadership.",
                report_type=rep["type"],
                format=rep["format"],
                status=rep["status"],
                file_path=rep["url"],
                file_size_bytes=rep["size"],
                download_url=rep["url"],
                is_scheduled=rep.get("scheduled", False),
                schedule_cron="0 8 * * 1" if rep.get("scheduled") else None,
                created_by=hr_manager.id
            )
            session.add(report_obj)

        # 8. Seed Audit Logs
        print("[AUDIT] Seeding Security & System Audit Logs...")
        logs_data = [
            {"action": "USER_LOGIN", "resource": "Auth", "desc": "User admin logged in successfully.", "ip": "192.168.1.10", "suspicious": False},
            {"action": "DATASET_UPLOAD", "resource": "UploadedDataset", "desc": "Uploaded IBM_HR_Employee_Attrition_v1.csv (1470 rows).", "ip": "192.168.1.25", "suspicious": False},
            {"action": "MODEL_TRAIN_SUCCESS", "resource": "ModelRegistry", "desc": "Successfully trained XGBoost Classifier with F1 0.912.", "ip": "127.0.0.1", "suspicious": False},
            {"action": "MODEL_PROMOTED", "resource": "ModelRegistry", "desc": "Promoted XGBoost-v2.1.0 to production model.", "ip": "192.168.1.15", "suspicious": False},
            {"action": "BATCH_PREDICTION_RUN", "resource": "Prediction", "desc": "Ran batch attrition scan on 210 active employees.", "ip": "192.168.1.25", "suspicious": False},
            {"action": "REPORT_GENERATED", "resource": "Report", "desc": "Generated PDF report: Q3 Executive Attrition Risk Summary.", "ip": "192.168.1.15", "suspicious": False},
            {"action": "UNAUTHORIZED_ACCESS_ATTEMPT", "resource": "UserManagement", "desc": "Failed login attempt for account 'admin_backup' from unrecognized IP.", "ip": "198.51.100.44", "suspicious": True},
        ]

        for log in logs_data:
            audit = AuditLog(
                id=uuid.uuid4(),
                user_id=admin_user.id if not log["suspicious"] else None,
                action=log["action"],
                resource_type=log["resource"],
                resource_id=str(uuid.uuid4()),
                description=log["desc"],
                ip_address=log["ip"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                request_method="POST" if "UPLOAD" in log["action"] or "LOGIN" in log["action"] else "GET",
                request_path=f"/api/v1/{log['resource'].lower()}",
                response_status=200 if not log["suspicious"] else 401,
                is_suspicious=log["suspicious"],
                created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
            )
            session.add(audit)

        await session.commit()
        print("[SUCCESS] Database Seeding Completed Successfully!")
        print("--------------------------------------------------")
        print(f"  • Users Created:        4")
        print(f"  • Departments Created:  {len(dept_objs)}")
        print(f"  • Employees Created:    {len(employees_list)}")
        print(f"  • ML Models Registered: {len(model_objs)}")
        print(f"  • Predictions Seeded:   {len(prediction_objs)}")
        print(f"  • Reports Created:      {len(reports_data)}")
        print(f"  • Audit Logs Logged:    {len(logs_data)}")
        print("--------------------------------------------------")


if __name__ == "__main__":
    asyncio.run(seed_database())
