import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Bell, CheckCheck, Trash2, Info, AlertTriangle, CheckCircle2 } from 'lucide-react'
import { apiGet, apiPost, apiDelete } from '@/lib/api'
import toast from 'react-hot-toast'

export default function NotificationsPage() {
  const qc = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['notifications'],
    queryFn: () => apiGet<any>('/notifications'),
    refetchInterval: 15000,
  })

  const notifications = data?.items || []
  const unreadCount = data?.unread_count || 0

  const markReadMutation = useMutation({
    mutationFn: (id: string) => apiPost(`/notifications/${id}/read`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  })

  const markAllReadMutation = useMutation({
    mutationFn: () => apiPost('/notifications/read-all'),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] })
      toast.success('All notifications marked as read')
    },
  })

  const clearAllMutation = useMutation({
    mutationFn: () => apiDelete('/notifications'),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] })
      toast.success('Notifications cleared')
    },
  })

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6 max-w-4xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Notifications</h1>
          <p className="text-gray-500 text-sm mt-1">{unreadCount} unread notification{unreadCount === 1 ? '' : 's'}</p>
        </div>
        <div className="flex items-center gap-3">
          {unreadCount > 0 && (
            <button onClick={() => markAllReadMutation.mutate()} className="btn-secondary text-xs py-2 px-3">
              <CheckCheck size={14} /> Mark all read
            </button>
          )}
          {notifications.length > 0 && (
            <button onClick={() => clearAllMutation.mutate()} className="text-gray-500 hover:text-red-400 text-xs py-2 px-3 flex items-center gap-1 transition-colors">
              <Trash2 size={14} /> Clear all
            </button>
          )}
        </div>
      </div>

      {/* List */}
      <div className="glass-card overflow-hidden divide-y divide-white/5">
        {isLoading ? (
          Array(4).fill(0).map((_, i) => (
            <div key={i} className="p-5 space-y-2">
              <div className="skeleton h-4 w-48" />
              <div className="skeleton h-3 w-80" />
            </div>
          ))
        ) : notifications.length === 0 ? (
          <div className="text-center py-16 text-gray-600">
            <Bell size={36} className="mx-auto mb-3 opacity-30" />
            <p>No notifications yet</p>
          </div>
        ) : (
          notifications.map((n: any) => (
            <div
              key={n.id}
              onClick={() => !n.read && markReadMutation.mutate(n.id)}
              className={`p-5 transition-colors cursor-pointer flex items-start gap-4 ${
                !n.read ? 'bg-brand-500/[0.04]' : 'hover:bg-white/[0.01]'
              }`}
            >
              <div className="w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 mt-0.5"
                   style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.2)' }}>
                {n.type === 'training_complete' ? (
                  <CheckCircle2 size={18} className="text-emerald-400" />
                ) : n.type === 'batch_shap_complete' ? (
                  <AlertTriangle size={18} className="text-amber-400" />
                ) : (
                  <Info size={18} className="text-brand-400" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-4">
                  <h4 className={`text-sm font-semibold ${!n.read ? 'text-white' : 'text-gray-300'}`}>{n.title}</h4>
                  <span className="text-[10px] text-gray-500 flex-shrink-0">{new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                </div>
                <p className="text-xs text-gray-400 mt-1 leading-relaxed">{n.message}</p>
              </div>
              {!n.read && (
                <span className="w-2 h-2 rounded-full bg-brand-500 flex-shrink-0 mt-2" />
              )}
            </div>
          ))
        )}
      </div>
    </motion.div>
  )
}
