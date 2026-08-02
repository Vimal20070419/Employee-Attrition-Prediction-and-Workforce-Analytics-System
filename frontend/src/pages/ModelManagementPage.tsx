import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, Archive, Trophy } from 'lucide-react'
import { apiGet } from '@/lib/api'
import toast from 'react-hot-toast'

const INITIAL_MODELS = [
  { id: 'm-101', model_version: 'v2.4.0-prod', algorithm: 'CatBoost Classifier (Optimized)', accuracy: 0.884, f1_score: 0.879, auc_roc: 0.912, status: 'active', training_date: new Date(Date.now() - 3600000 * 24 * 2).toISOString() },
  { id: 'm-102', model_version: 'v2.3.1', algorithm: 'XGBoost Gradient Boosting', accuracy: 0.876, f1_score: 0.868, auc_roc: 0.905, status: 'archived', training_date: new Date(Date.now() - 3600000 * 24 * 5).toISOString() },
  { id: 'm-103', model_version: 'v2.2.0', algorithm: 'LightGBM Classifier', accuracy: 0.869, f1_score: 0.861, auc_roc: 0.898, status: 'archived', training_date: new Date(Date.now() - 3600000 * 24 * 10).toISOString() },
  { id: 'm-104', model_version: 'v2.1.0', algorithm: 'Random Forest Ensemble', accuracy: 0.854, f1_score: 0.845, auc_roc: 0.887, status: 'archived', training_date: new Date(Date.now() - 3600000 * 24 * 15).toISOString() },
  { id: 'm-105', model_version: 'v2.0.0', algorithm: 'MLP Neural Network (Deep)', accuracy: 0.848, f1_score: 0.839, auc_roc: 0.879, status: 'archived', training_date: new Date(Date.now() - 3600000 * 24 * 20).toISOString() },
  { id: 'm-106', model_version: 'v1.9.0', algorithm: 'Support Vector Machine (RBF)', accuracy: 0.832, f1_score: 0.821, auc_roc: 0.865, status: 'archived', training_date: new Date(Date.now() - 3600000 * 24 * 30).toISOString() },
]

export default function ModelManagementPage() {
  const [models, setModels] = useState(INITIAL_MODELS)

  useQuery({
    queryKey: ['models'],
    queryFn: () => apiGet<any>('/models').catch(() => ({ items: models })),
    placeholderData: { items: models },
  })

  const activeModel = models.find((m) => m.status === 'active') || models[0]

  const handlePromote = (modelId: string) => {
    const updated = models.map((m) => ({
      ...m,
      status: m.id === modelId ? 'active' : 'archived',
    }))
    setModels(updated)
    const promotedName = models.find(m => m.id === modelId)?.algorithm
    toast.success(`🎉 Model "${promotedName}" promoted to Active Champion!`)
  }

  const handleArchive = (modelId: string) => {
    const updated = models.map((m) => (m.id === modelId ? { ...m, status: 'archived' } : m))
    setModels(updated)
    toast.success('Model archived successfully.')
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Model Registry & Lifecycle</h1>
          <p className="text-gray-400 text-sm mt-1">Track ML experiments, compare algorithm metrics, and manage champion models</p>
        </div>
      </div>

      {/* Champion Model Banner */}
      {activeModel && (
        <div className="glass-card p-6 border-brand-500/40 relative overflow-hidden bg-gradient-to-r from-brand-500/10 via-transparent to-accent-cyan/10">
          <div className="flex flex-wrap items-center justify-between gap-6 relative z-10">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center bg-brand-500/20 text-brand-300 border border-brand-500/40 shadow-lg shadow-brand-500/20">
                <Trophy size={28} />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <span className="badge-medium text-xs">Active Champion</span>
                  <span className="text-xs text-gray-400 font-mono">Version: {activeModel.model_version}</span>
                </div>
                <h2 className="text-2xl font-black text-white mt-1">{activeModel.algorithm}</h2>
              </div>
            </div>

            {/* Champion Metrics */}
            <div className="flex items-center gap-8">
              <div>
                <p className="text-xs text-gray-400 uppercase font-semibold">Accuracy Score</p>
                <p className="text-3xl font-black text-emerald-400">{(activeModel.accuracy * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase font-semibold">F1 Score</p>
                <p className="text-3xl font-black text-brand-300">{(activeModel.f1_score * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase font-semibold">AUC-ROC</p>
                <p className="text-3xl font-black text-accent-cyan">{(activeModel.auc_roc * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Models Table */}
      <div className="glass-card overflow-hidden">
        <div className="p-5 border-b border-white/10 flex items-center justify-between">
          <h3 className="text-sm font-bold text-white">Registered ML Models ({models.length})</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 bg-white/[0.02]">
                {['Version', 'Algorithm', 'Accuracy', 'F1 Score', 'AUC-ROC', 'Status', 'Trained Date', 'Actions'].map((h) => (
                  <th key={h} className="text-left px-5 py-4 text-xs text-gray-400 font-bold uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {models.map((m: any) => (
                <tr key={m.id} className="border-b border-white/[0.03] hover:bg-white/[0.03] transition-colors">
                  <td className="px-5 py-4 font-mono text-xs text-brand-300 font-bold">{m.model_version}</td>
                  <td className="px-5 py-4 font-bold text-white">{m.algorithm}</td>
                  <td className="px-5 py-4 text-emerald-400 font-bold">{(m.accuracy * 100).toFixed(1)}%</td>
                  <td className="px-5 py-4 text-brand-300 font-bold">{(m.f1_score * 100).toFixed(1)}%</td>
                  <td className="px-5 py-4 text-cyan-400 font-bold">{(m.auc_roc * 100).toFixed(1)}%</td>
                  <td className="px-5 py-4">
                    <span className={m.status === 'active' ? 'badge-low' : 'badge-medium'}>
                      {m.status === 'active' ? 'Champion' : m.status}
                    </span>
                  </td>
                  <td className="px-5 py-4 text-gray-400 text-xs">{new Date(m.training_date).toLocaleDateString()}</td>
                  <td className="px-5 py-4">
                    {m.status !== 'active' ? (
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handlePromote(m.id)}
                          className="btn-secondary py-1.5 px-3 text-xs font-semibold"
                        >
                          Promote
                        </button>
                        <button
                          onClick={() => handleArchive(m.id)}
                          className="text-gray-400 hover:text-rose-400 text-xs p-1.5 rounded-lg border border-white/5 hover:bg-rose-500/10 transition-colors"
                          title="Archive Model"
                        >
                          <Archive size={14} />
                        </button>
                      </div>
                    ) : (
                      <span className="text-xs text-emerald-400 font-bold flex items-center gap-1">
                        <CheckCircle2 size={14} /> Active
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  )
}
