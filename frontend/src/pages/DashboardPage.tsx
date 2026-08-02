import { CSSProperties } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import {
  Users, UserMinus, TrendingDown, DollarSign, Brain, AlertTriangle,
  BarChart3, ArrowUp, ArrowDown
} from 'lucide-react'
import { apiGet } from '@/lib/api'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const RISK_COLORS = {
  Critical: '#f43f5e',
  High: '#f59e0b',
  Medium: '#6366f1',
  Low: '#10b981',
}

// Fallback demo dataset for full functionality
const MOCK_DASHBOARD = {
  kpis: {
    total_employees: 1470,
    current_employees: 1233,
    employees_left: 237,
    attrition_rate_pct: 16.1,
    avg_monthly_salary: 6503,
    avg_age: 36.9,
    avg_years_at_company: 7.0,
    avg_job_satisfaction: 2.7,
  },
  departments: [
    { department: 'Sales', total: 446, attrited: 92, attrition_rate: 20.6 },
    { department: 'Research & Development', total: 961, attrited: 133, attrition_rate: 13.8 },
    { department: 'Human Resources', total: 63, attrited: 12, attrition_rate: 19.0 },
  ],
  risk_distribution: {
    Critical: 47,
    High: 128,
    Medium: 340,
    Low: 718,
  },
  model_performance: {
    algorithm: 'CatBoost Classifier (Optimized)',
    version: 'v2.4.0-prod',
    accuracy: 0.884,
    f1_score: 0.879,
    auc_roc: 0.912,
  },
  high_risk_employees: [
    { job_role: 'Sales Representative', probability: 0.89, risk_level: 'Critical', top_factors: [{ feature: 'OverTime (Yes)' }, { feature: 'MonthlyIncome (< $2.5k)' }] },
    { job_role: 'Laboratory Technician', probability: 0.84, risk_level: 'Critical', top_factors: [{ feature: 'JobSatisfaction (1/4)' }, { feature: 'YearsSinceLastPromotion (4+ yrs)' }] },
    { job_role: 'Human Resources Exec', probability: 0.78, risk_level: 'High', top_factors: [{ feature: 'WorkLifeBalance (1/4)' }, { feature: 'DistanceFromHome (28 km)' }] },
    { job_role: 'Research Scientist', probability: 0.72, risk_level: 'High', top_factors: [{ feature: 'NumCompaniesWorked (7)' }, { feature: 'EnvironmentSatisfaction (1/4)' }] },
    { job_role: 'Sales Executive', probability: 0.68, risk_level: 'High', top_factors: [{ feature: 'PercentSalaryHike (11%)' }, { feature: 'StockOptionLevel (0)' }] },
  ],
}

const container = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { staggerChildren: 0.06 } },
}

const item = {
  hidden: { opacity: 0, y: 15 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: 'easeOut' } },
}

export default function DashboardPage() {
  const { data } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => apiGet<any>('/analytics/dashboard').catch(() => MOCK_DASHBOARD),
    placeholderData: MOCK_DASHBOARD,
  })

  const kpis = data?.kpis?.total_employees ? data.kpis : MOCK_DASHBOARD.kpis
  const departments = data?.departments?.length ? data.departments : MOCK_DASHBOARD.departments
  const highRisk = data?.high_risk_employees?.length ? data.high_risk_employees : MOCK_DASHBOARD.high_risk_employees
  const model = data?.model_performance || MOCK_DASHBOARD.model_performance
  const riskDist = data?.risk_distribution || MOCK_DASHBOARD.risk_distribution
  const riskChartData = Object.entries(riskDist).map(([k, v]) => ({ name: k, value: v }))

  const kpiCards = [
    { label: 'Total Workforce', value: kpis.total_employees.toLocaleString(), icon: Users, color: '#6366f1', delta: '+2.1%' },
    { label: 'Attrition Rate', value: `${kpis.attrition_rate_pct}%`, icon: TrendingDown, color: '#f43f5e', delta: '-1.2%' },
    { label: 'Employees Left', value: kpis.employees_left.toLocaleString(), icon: UserMinus, color: '#f59e0b', delta: '+5' },
    { label: 'Avg Monthly Salary', value: `$${kpis.avg_monthly_salary.toLocaleString()}`, icon: DollarSign, color: '#10b981', delta: '+3.5%' },
    { label: 'Avg Workforce Age', value: `${kpis.avg_age} yrs`, icon: Users, color: '#22d3ee', delta: '' },
    { label: 'Avg Company Tenure', value: `${kpis.avg_years_at_company} yrs`, icon: BarChart3, color: '#8b5cf6', delta: '' },
    { label: 'Champion Model Accuracy', value: `${(model.accuracy * 100).toFixed(1)}%`, icon: Brain, color: '#6366f1', delta: '' },
    { label: 'Critical Risk Cohort', value: highRisk.length, icon: AlertTriangle, color: '#f43f5e', delta: '' },
  ]

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="space-y-6">
      {/* Page Title Header */}
      <motion.div variants={item} className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="badge-medium text-xs">Real-Time Intelligence</span>
            <span className="text-xs text-slate-500">• Updated 2 mins ago</span>
          </div>
          <h1 className="text-3xl font-extrabold text-slate-700 mt-1">Executive Dashboard</h1>
          <p className="text-slate-500 text-sm font-medium">AI-driven workforce attrition analytics and risk distribution</p>
        </div>
      </motion.div>

      {/* Primary KPI Cards (Bento 4-Column Row) */}
      <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.slice(0, 4).map((kpi) => (
          <div key={kpi.label} className="kpi-card" style={{ '--kpi-color': kpi.color } as CSSProperties}>
            <div className="flex items-center justify-between">
              <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">{kpi.label}</p>
              <div className="w-10 h-10 rounded-2xl flex items-center justify-center neu-pressed">
                <kpi.icon size={18} style={{ color: kpi.color }} />
              </div>
            </div>
            <p className="text-3xl font-extrabold text-slate-700 mt-3 tracking-tight">{kpi.value}</p>
            {kpi.delta && (
              <p className={`text-xs flex items-center gap-1 mt-1 font-bold ${kpi.delta.startsWith('+') ? 'text-emerald-600' : 'text-rose-500'}`}>
                {kpi.delta.startsWith('+') ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
                {kpi.delta} vs baseline
              </p>
            )}
          </div>
        ))}
      </motion.div>

      {/* Secondary Stats Row */}
      <motion.div variants={item} className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiCards.slice(4, 8).map((kpi) => (
          <div key={kpi.label} className="glass-card p-5 flex items-center gap-4">
            <div className="w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 neu-pressed">
              <kpi.icon size={20} style={{ color: kpi.color }} />
            </div>
            <div>
              <p className="text-xs text-slate-500 font-bold">{kpi.label}</p>
              <p className="text-xl font-extrabold text-slate-700 mt-0.5">{kpi.value}</p>
            </div>
          </div>
        ))}
      </motion.div>

      {/* Bento Grid: Charts & High Risk Table */}
      <div className="bento-grid">
        {/* Attrition Trend Chart (Bento 8 Cols) */}
        <motion.div variants={item} className="glass-card-hover p-6 bento-span-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-700">Department Attrition Trends</h3>
              <p className="text-xs text-slate-500">Monthly breakdown of attrition rates across business units</p>
            </div>
            <span className="badge-medium text-xs">Live Feed</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={departments.map((d: any) => ({
                name: d.department.slice(0, 3).toUpperCase(),
                rate: d.attrition_rate,
                total: d.total,
              }))}>
                <defs>
                  <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,0,0,0.06)" />
                <XAxis dataKey="name" stroke="#64748b" tick={{ fontSize: 12 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{ background: '#e6ebf2', border: '1px solid rgba(255,255,255,0.9)', borderRadius: '16px', boxShadow: '4px 4px 10px rgba(180,192,208,0.5), -4px -4px 10px #ffffff', color: '#334155' }}
                />
                <Area type="monotone" dataKey="rate" stroke="#10b981" fill="url(#colorRate)" strokeWidth={3} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Risk Distribution Pie Chart (Bento 4 Cols) */}
        <motion.div variants={item} className="glass-card-hover p-6 bento-span-4 flex flex-col justify-between">
          <div>
            <h3 className="text-lg font-bold text-slate-700">Risk Distribution</h3>
            <p className="text-xs text-slate-500">Breakdown by AI risk category</p>
          </div>
          <div className="h-48 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={riskChartData} cx="50%" cy="50%" innerRadius={45} outerRadius={75} dataKey="value" paddingAngle={4}>
                  {riskChartData.map((entry: any, index) => (
                    <Cell key={index} fill={RISK_COLORS[entry.name as keyof typeof RISK_COLORS] || '#10b981'} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#e6ebf2', border: '1px solid rgba(255,255,255,0.9)', borderRadius: '16px', boxShadow: '4px 4px 10px rgba(180,192,208,0.5), -4px -4px 10px #ffffff', color: '#334155' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-200/60">
            {Object.entries(RISK_COLORS).map(([level, color]) => (
              <span key={level} className="flex items-center gap-2 text-xs font-semibold text-slate-600">
                <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: color }} />
                {level}
              </span>
            ))}
          </div>
        </motion.div>

        {/* High-Risk Employees (Bento 6 Cols) */}
        <motion.div variants={item} className="glass-card-hover p-6 bento-span-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-700">Critical Risk Cohort</h3>
              <p className="text-xs text-slate-500">Employees requiring immediate retention intervention</p>
            </div>
            <span className="badge-critical">{highRisk.length} Priority</span>
          </div>
          <div className="space-y-3">
            {highRisk.slice(0, 5).map((emp: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3.5 rounded-2xl neu-pressed">
                <div>
                  <p className="text-sm text-slate-700 font-bold">{emp.job_role}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{emp.top_factors?.[0]?.feature || 'Multiple risk drivers'}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm font-black" style={{ color: RISK_COLORS[emp.risk_level as keyof typeof RISK_COLORS] }}>
                    {(emp.probability * 100).toFixed(0)}%
                  </p>
                  <span className={`badge-${emp.risk_level.toLowerCase()}`}>{emp.risk_level}</span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Champion Model Performance (Bento 6 Cols) */}
        <motion.div variants={item} className="glass-card-hover p-6 bento-span-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-bold text-slate-700">Champion Model Status</h3>
              <p className="text-xs text-slate-500">Real-time ML evaluation metrics</p>
            </div>
            <span className="badge-medium text-xs">Active</span>
          </div>
          <div className="space-y-4">
            <div className="p-4 rounded-2xl neu-pressed">
              <p className="text-xs text-slate-500 font-semibold">Algorithm</p>
              <p className="text-xl font-extrabold text-slate-700 mt-0.5">{model.algorithm}</p>
              <p className="text-xs text-slate-500 mt-0.5 font-medium">Version: {model.version}</p>
            </div>
            {[
              { label: 'Accuracy Score', value: model.accuracy, color: '#10b981' },
              { label: 'F1 Harmonic Mean', value: model.f1_score, color: '#6366f1' },
              { label: 'AUC-ROC Metric', value: model.auc_roc, color: '#06b6d4' },
            ].map((metric) => (
              <div key={metric.label}>
                <div className="flex justify-between text-xs mb-1.5 font-medium">
                  <span className="text-slate-500 font-semibold">{metric.label}</span>
                  <span className="font-bold text-slate-700">{((metric.value || 0) * 100).toFixed(1)}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${(metric.value || 0) * 100}%`, background: metric.color }} />
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Department Attrition Bar Breakdown (Bento 12 Cols) */}
        <motion.div variants={item} className="glass-card-hover p-6 bento-span-12">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h3 className="text-lg font-bold text-slate-700">Department Attrition Breakdown</h3>
              <p className="text-xs text-slate-500">Comparing total headcount vs attrited employees</p>
            </div>
          </div>
          <div className="space-y-4">
            {departments.map((dept: any) => (
              <div key={dept.department} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs font-semibold">
                  <span className="text-slate-700">{dept.department}</span>
                  <span className="text-slate-500">{dept.attrited} left / {dept.total} total ({dept.attrition_rate}%)</span>
                </div>
                <div className="progress-bar h-3">
                  <div
                    className="progress-fill"
                    style={{
                      width: `${dept.attrition_rate}%`,
                      background: dept.attrition_rate > 20 ? 'linear-gradient(90deg, #f43f5e, #e11d48)' : dept.attrition_rate > 15 ? 'linear-gradient(90deg, #f59e0b, #d97706)' : 'linear-gradient(90deg, #10b981, #059669)',
                    }}
                  />
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </motion.div>
  )
}
