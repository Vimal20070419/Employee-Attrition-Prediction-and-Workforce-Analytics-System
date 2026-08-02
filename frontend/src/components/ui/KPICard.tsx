import React from 'react'
import { LucideIcon } from 'lucide-react'

interface KPICardProps {
  label: string
  value: string | number
  icon: LucideIcon
  color?: string
  delta?: string
}

export const KPICard: React.FC<KPICardProps> = ({ label, value, icon: Icon, color = '#10b981', delta }) => (
  <div className="kpi-card group cursor-pointer" style={{ '--kpi-color': color } as React.CSSProperties}>
    <div className="flex items-center justify-between">
      <p className="text-xs text-slate-500 font-bold uppercase tracking-wider">{label}</p>
      <div className="w-10 h-10 rounded-2xl flex items-center justify-center neu-pressed">
        <Icon size={18} style={{ color }} className="drop-shadow-sm transition-transform duration-300 group-hover:scale-110" />
      </div>
    </div>
    <p className="text-3xl font-extrabold text-slate-700 mt-2 tracking-tight">{value}</p>
    {delta && <p className="text-xs font-semibold text-emerald-600 mt-1">{delta}</p>}
  </div>
)
