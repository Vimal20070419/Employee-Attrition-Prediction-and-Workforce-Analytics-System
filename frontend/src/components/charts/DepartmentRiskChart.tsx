import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface DepartmentRiskChartProps {
  data: Array<{ department: string; avg_risk_score: number; risk_category?: string }>
}

export const DepartmentRiskChart: React.FC<DepartmentRiskChartProps> = ({ data }) => (
  <div className="glass-card p-6">
    <h3 className="text-base font-bold text-white mb-4">Department Risk Index</h3>
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="department" stroke="#6b7280" tick={{ fontSize: 11 }} />
          <YAxis stroke="#6b7280" tick={{ fontSize: 11 }} />
          <Tooltip contentStyle={{ background: '#21262d', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
          <Bar dataKey="avg_risk_score" fill="#22d3ee" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  </div>
)
