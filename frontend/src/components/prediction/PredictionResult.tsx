import React from 'react'
import { Brain, AlertTriangle, CheckCircle2, Info } from 'lucide-react'

const RISK_CONFIG = {
  Critical: { color: '#f43f5e', bg: 'rgba(244,63,94,0.1)', icon: AlertTriangle, message: 'Very high attrition risk. Immediate HR intervention required.' },
  High: { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', icon: AlertTriangle, message: 'High attrition risk. Schedule a one-on-one retention conversation.' },
  Medium: { color: '#6366f1', bg: 'rgba(99,102,241,0.1)', icon: Info, message: 'Moderate risk. Monitor and implement proactive engagement strategies.' },
  Low: { color: '#10b981', bg: 'rgba(16,185,129,0.1)', icon: CheckCircle2, message: 'Low attrition risk. Maintain current engagement levels.' },
}

interface PredictionResultProps {
  result?: {
    attrition_probability: number
    risk_level: 'Critical' | 'High' | 'Medium' | 'Low'
    top_risk_factors?: Array<{ feature: string; shap_value: number; direction: string; impact: string }>
    retention_recommendations?: Array<{ category: string; recommendation: string; priority: string; action: string }>
  }
}

export const PredictionResult: React.FC<PredictionResultProps> = ({ result }) => {
  if (!result) {
    return (
      <div className="glass-card p-8 text-center">
        <Brain size={48} className="mx-auto mb-4 text-gray-600" />
        <p className="text-gray-500 text-sm">Fill in the form and click "Predict" to see the AI-generated attrition risk assessment</p>
      </div>
    )
  }

  const riskConfig = RISK_CONFIG[result.risk_level]

  return (
    <div className="space-y-4">
      <div className="glass-card p-6" style={{ borderColor: riskConfig.color + '40' }}>
        <div className="flex items-center gap-3 mb-4">
          <riskConfig.icon size={24} style={{ color: riskConfig.color }} />
          <div>
            <p className="text-xs text-gray-500">Attrition Probability</p>
            <p className="text-4xl font-black" style={{ color: riskConfig.color }}>
              {(result.attrition_probability * 100).toFixed(1)}%
            </p>
          </div>
        </div>
        <div className="progress-bar mb-3">
          <div className="progress-fill" style={{ width: `${result.attrition_probability * 100}%`, background: riskConfig.color }} />
        </div>
        <span style={{ background: riskConfig.bg, color: riskConfig.color, borderColor: riskConfig.color + '40' }} className="inline-block px-3 py-1 rounded-full text-xs font-semibold border mb-3">
          {result.risk_level} Risk
        </span>
        <p className="text-xs text-gray-400">{riskConfig.message}</p>
      </div>
    </div>
  )
}
