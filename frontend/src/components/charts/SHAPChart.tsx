import React from 'react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface SHAPChartProps {
  data: Array<{ feature: string; importance: number }>
}

export const SHAPChart: React.FC<SHAPChartProps> = ({ data }) => (
  <div className="glass-card p-6">
    <h3 className="text-base font-bold text-white mb-4">Global Feature Importance (SHAP)</h3>
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis type="number" stroke="#6b7280" tick={{ fontSize: 11 }} />
          <YAxis dataKey="feature" type="category" stroke="#6b7280" tick={{ fontSize: 11 }} width={140} />
          <Tooltip contentStyle={{ background: '#21262d', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px' }} />
          <Bar dataKey="importance" fill="#6366f1" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  </div>
)
