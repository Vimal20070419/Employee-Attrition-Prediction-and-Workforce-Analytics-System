import React from 'react'

const RISK_COLORS: Record<string, string> = {
  Critical: '#f43f5e',
  High: '#f59e0b',
  Medium: '#6366f1',
  Low: '#10b981',
}

interface HighRiskTableProps {
  employees: Array<{
    job_role: string
    probability: number
    risk_level: string
    top_factors?: Array<{ feature: string }>
  }>
}

export const HighRiskTable: React.FC<HighRiskTableProps> = ({ employees }) => (
  <div className="glass-card p-6">
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-base font-bold text-white">High-Risk Employees</h3>
      <span className="badge-critical">{employees.length} at risk</span>
    </div>
    <div className="space-y-3">
      {employees.slice(0, 5).map((emp, i) => (
        <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-white/[0.02] border border-white/5">
          <div>
            <p className="text-sm text-white font-medium">{emp.job_role}</p>
            <p className="text-xs text-gray-500">{emp.top_factors?.[0]?.feature || 'Multiple factors'}</p>
          </div>
          <div className="text-right">
            <p className="text-sm font-bold" style={{ color: RISK_COLORS[emp.risk_level] }}>
              {(emp.probability * 100).toFixed(0)}%
            </p>
            <span className={`badge-${emp.risk_level.toLowerCase()}`}>{emp.risk_level}</span>
          </div>
        </div>
      ))}
      {!employees.length && (
        <p className="text-gray-600 text-sm text-center py-4">No high-risk employees detected</p>
      )}
    </div>
  </div>
)
