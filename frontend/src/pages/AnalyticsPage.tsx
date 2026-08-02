import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Layers, Cpu } from 'lucide-react'
import { apiGet } from '@/lib/api'
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip
} from 'recharts'

export default function AnalyticsPage() {
  const { data: deptRiskData } = useQuery({
    queryKey: ['deptRisk'],
    queryFn: () => apiGet<any>('/analytics/department-risk'),
  })

  const { data: shapData } = useQuery({
    queryKey: ['shapImportance'],
    queryFn: () => apiGet<any>('/analytics/shap-importance'),
  })

  const deptScores = deptRiskData?.department_risk || []
  const shapFeatures = shapData?.features || ['OverTime', 'MonthlyIncome', 'Age', 'YearsAtCompany', 'JobSatisfaction', 'TotalWorkingYears', 'WorkLifeBalance', 'EnvironmentSatisfaction']
  const shapImportance = shapData?.importance || [0.35, 0.28, 0.22, 0.19, 0.18, 0.15, 0.12, 0.10]

  const shapChartData = shapFeatures.slice(0, 8).map((f: string, i: number) => ({
    feature: f,
    importance: shapImportance[i] || 0.1,
  }))

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white">Workforce Analytics</h1>
        <p className="text-gray-500 text-sm mt-1">Deep-dive EDA visualizations and global feature importance</p>
      </div>

      {/* Grid */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* SHAP Feature Importance */}
        <div className="glass-card p-6">
          <h3 className="text-base font-bold text-white mb-1 flex items-center gap-2">
            <Cpu size={18} className="text-brand-400" /> Global Feature Importance (SHAP)
          </h3>
          <p className="text-xs text-gray-500 mb-6">Top drivers of employee attrition across the organization</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={shapChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis type="number" stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis dataKey="feature" type="category" stroke="#6b7280" tick={{ fontSize: 11 }} width={140} />
                <Tooltip contentStyle={{ background: '#21262d', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
                <Bar dataKey="importance" fill="#6366f1" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Department Risk Scores */}
        <div className="glass-card p-6">
          <h3 className="text-base font-bold text-white mb-1 flex items-center gap-2">
            <Layers size={18} className="text-accent-cyan" /> Department Risk Index
          </h3>
          <p className="text-xs text-gray-500 mb-6">Average attrition probability score by department</p>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={deptScores}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="department" stroke="#6b7280" tick={{ fontSize: 11 }} />
                <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ background: '#21262d', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
                <Bar dataKey="avg_risk_score" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </motion.div>
  )
}
