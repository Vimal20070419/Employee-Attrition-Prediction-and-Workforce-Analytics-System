import React from 'react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface AttritionTrendChartProps {
  data: Array<{ month: string; rate: number; total?: number }>
}

export const AttritionTrendChart: React.FC<AttritionTrendChartProps> = ({ data }) => (
  <div className="glass-card p-6">
    <h3 className="text-base font-bold text-white mb-4">Attrition Trend</h3>
    <div className="h-56">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="colorRate" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
          <XAxis dataKey="month" stroke="#6b7280" tick={{ fontSize: 12 }} />
          <YAxis stroke="#6b7280" tick={{ fontSize: 12 }} />
          <Tooltip contentStyle={{ background: '#21262d', border: '1px solid rgba(255,255,255,0.08)', borderRadius: '12px', color: '#f0f6fc' }} />
          <Area type="monotone" dataKey="rate" stroke="#6366f1" fill="url(#colorRate)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  </div>
)
