"""
AttritionIQ — Locust Load Testing Script
===========================================
Simulates 500+ concurrent HR Analysts making predictions,
fetching analytics, viewing employee lists, and generating reports.

Usage:
  locust -f tests/load/locustfile.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between


class AttritionIQUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Authenticate user on start."""
        response = self.client.post(
            "/api/v1/auth/login",
            data={"username": "admin@attritioniq.com", "password": "Admin@123"},
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.headers = {}

    @task(5)
    def view_dashboard(self):
        """Fetch main dashboard analytics."""
        self.client.get("/api/v1/analytics/dashboard", headers=self.headers)

    @task(3)
    def list_employees(self):
        """Fetch paginated employee list."""
        self.client.get("/api/v1/employees?page=1&page_size=20", headers=self.headers)

    @task(2)
    def run_single_prediction(self):
        """Trigger single employee attrition prediction."""
        payload = {
            "age": 32,
            "gender": "Female",
            "job_role": "Sales Executive",
            "monthly_income": 4500,
            "over_time": True,
            "years_at_company": 3,
            "job_satisfaction": 2,
            "environment_satisfaction": 2,
            "work_life_balance": 2,
            "total_working_years": 8,
            "num_companies_worked": 3,
            "training_times_last_year": 2,
            "distance_from_home": 15,
            "education": 3,
            "job_level": 2,
            "performance_rating": 3,
            "years_in_current_role": 2,
            "years_since_last_promotion": 1,
            "years_with_curr_manager": 2,
            "stock_option_level": 0,
            "job_involvement": 2,
            "percent_salary_hike": 12,
        }
        self.client.post("/api/v1/predictions/predict", json=payload, headers=self.headers)

    @task(1)
    def health_check(self):
        """Check system health endpoint."""
        self.client.get("/health")
