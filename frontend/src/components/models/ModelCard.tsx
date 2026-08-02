import React from 'react'
import { Cpu } from 'lucide-react'

interface ModelCardProps {
  model: {
    id: string
    model_version: string
    algorithm: string
    accuracy?: number
    f1_score?: number
    auc_roc?: number
    status: string
    training_date?: string
  }
  onPromote?: (id: string) => void
  onArchive?: (id: string) => void
}

export const ModelCard: React.FC<ModelCardProps> = ({ model, onPromote, onArchive }) => (
  <div className="glass-card p-6 flex flex-col justify-between">
    <div className="flex items-center gap-3 mb-4">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-brand-500/20 text-brand-400">
        <Cpu size={20} />
      </div>
      <div>
        <span className={model.status === 'active' ? 'badge-low' : 'badge-medium'}>{model.status}</span>
        <h4 className="text-lg font-bold text-white mt-1">{model.algorithm}</h4>
        <p className="text-xs text-gray-500 font-mono">{model.model_version}</p>
      </div>
    </div>
    <div className="grid grid-cols-3 gap-2 py-3 border-y border-white/5 text-center">
      <div>
        <p className="text-[10px] text-gray-500 uppercase">Accuracy</p>
        <p className="text-sm font-bold text-emerald-400">{model.accuracy ? `${(model.accuracy * 100).toFixed(1)}%` : '—'}</p>
      </div>
      <div>
        <p className="text-[10px] text-gray-500 uppercase">F1 Score</p>
        <p className="text-sm font-bold text-brand-400">{model.f1_score ? `${(model.f1_score * 100).toFixed(1)}%` : '—'}</p>
      </div>
      <div>
        <p className="text-[10px] text-gray-500 uppercase">AUC-ROC</p>
        <p className="text-sm font-bold text-cyan-400">{model.auc_roc ? `${(model.auc_roc * 100).toFixed(1)}%` : '—'}</p>
      </div>
    </div>
    {model.status !== 'active' && (onPromote || onArchive) && (
      <div className="mt-4 flex gap-2">
        {onPromote && (
          <button onClick={() => onPromote(model.id)} className="btn-secondary flex-1 justify-center py-2 text-xs">Promote</button>
        )}
        {onArchive && (
          <button onClick={() => onArchive(model.id)} className="p-2 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-500/10 text-xs border border-white/5 transition-colors">Archive</button>
        )}
      </div>
    )}
  </div>
)
