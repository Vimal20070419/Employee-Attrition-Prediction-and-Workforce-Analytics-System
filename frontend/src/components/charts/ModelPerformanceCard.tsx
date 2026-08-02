import React from 'react'
import { Brain } from 'lucide-react'

interface ModelPerformanceCardProps {
  model?: {
    algorithm: string
    version: string
    accuracy: number
    f1_score: number
    auc_roc: number
  }
}

export const ModelPerformanceCard: React.FC<ModelPerformanceCardProps> = ({ model }) => (
  <div className="glass-card p-6">
    <h3 className="text-base font-bold text-white mb-4">Active Model Performance</h3>
    {model ? (
      <div className="space-y-4">
        <div className="p-4 rounded-xl bg-brand-500/10 border border-brand-500/20">
          <p className="text-xs text-gray-500 mb-1">Algorithm</p>
          <p className="text-lg font-bold text-white">{model.algorithm}</p>
          <p className="text-xs text-gray-500">Version: {model.version}</p>
        </div>
        {[
          { label: 'Accuracy', value: model.accuracy, color: '#10b981' },
          { label: 'F1 Score', value: model.f1_score, color: '#6366f1' },
          { label: 'AUC-ROC', value: model.auc_roc, color: '#22d3ee' },
        ].map((metric) => (
          <div key={metric.label}>
            <div className="flex justify-between text-sm mb-1.5">
              <span className="text-gray-400">{metric.label}</span>
              <span className="font-bold text-white">{((metric.value || 0) * 100).toFixed(1)}%</span>
            </div>
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${(metric.value || 0) * 100}%`, background: metric.color }} />
            </div>
          </div>
        ))}
      </div>
    ) : (
      <div className="text-center py-12 text-gray-600">
        <Brain size={32} className="mx-auto mb-3 opacity-30" />
        <p>No active model. Upload a dataset to start training.</p>
      </div>
    )}
  </div>
)
