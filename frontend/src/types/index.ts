export interface Employee {
  id: string
  employee_number?: string
  age: number
  gender: string
  job_role: string
  monthly_income: number
  over_time: boolean
  years_at_company: number
  attrition?: 'Yes' | 'No'
  department_id?: string
  created_at: string
}

export interface Prediction {
  id: string
  employee_id?: string
  attrition_probability: number
  attrition_prediction: string
  risk_level: 'Critical' | 'High' | 'Medium' | 'Low'
  top_risk_factors: Array<{
    feature: string
    shap_value: number
    direction: string
    impact: string
  }>
  retention_recommendations: Array<{
    category: string
    recommendation: string
    priority: string
    action: string
  }>
  created_at: string
}

export interface ModelRegistryItem {
  id: string
  model_version: string
  algorithm: string
  accuracy?: number
  precision_score?: number
  recall_score?: number
  f1_score?: number
  auc_roc?: number
  status: 'active' | 'archived' | 'failed'
  training_date?: string
}
