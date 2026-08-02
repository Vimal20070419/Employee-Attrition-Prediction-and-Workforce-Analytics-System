"""AttritionIQ — Recommendation Engine Module"""

from typing import Dict, List


class RetentionRecommender:
    """Generates personalized HR retention strategies based on risk factors."""

    def generate(self, features: Dict, probability: float, top_factors: List[Dict]) -> List[Dict]:
        recs = []
        for factor in top_factors[:5]:
            feat = factor["feature"].lower()
            if "overtime" in feat:
                recs.append({
                    "category": "Workload & Overtime",
                    "recommendation": "Cap weekly overtime to under 5 hours. Offer flexitime.",
                    "priority": "High",
                    "action": "Conduct immediate workload review with team lead.",
                })
            elif "income" in feat or "salary" in feat:
                recs.append({
                    "category": "Compensation & Benefits",
                    "recommendation": "Review base salary against industry benchmark.",
                    "priority": "High",
                    "action": "Submit out-of-cycle compensation adjustment request.",
                })
            elif "satisfaction" in feat:
                recs.append({
                    "category": "Employee Engagement",
                    "recommendation": "Schedule 1-on-1 pulse check to address dissatisfiers.",
                    "priority": "High",
                    "action": "Assign a senior mentor and conduct stay interview.",
                })
        if not recs:
            recs.append({
                "category": "General Retention",
                "recommendation": "Maintain regular 1-on-1 check-ins and performance recognition.",
                "priority": "Low",
                "action": "Schedule quarterly career progression review.",
            })
        return recs
