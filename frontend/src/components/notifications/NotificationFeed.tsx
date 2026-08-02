import React from 'react'
import { Bell, Info, AlertTriangle, CheckCircle2 } from 'lucide-react'

interface NotificationFeedProps {
  notifications: Array<{
    id: string
    title: string
    message: string
    type: string
    read: boolean
    created_at: string
  }>
  onMarkRead?: (id: string) => void
}

export const NotificationFeed: React.FC<NotificationFeedProps> = ({ notifications, onMarkRead }) => (
  <div className="glass-card overflow-hidden divide-y divide-white/5">
    {notifications.length === 0 ? (
      <div className="text-center py-12 text-gray-600">
        <Bell size={32} className="mx-auto mb-2 opacity-30" />
        <p className="text-sm">No notifications</p>
      </div>
    ) : (
      notifications.map((n) => (
        <div
          key={n.id}
          onClick={() => !n.read && onMarkRead?.(n.id)}
          className={`p-4 flex items-start gap-3 transition-colors ${!n.read ? 'bg-brand-500/[0.04]' : ''}`}
        >
          <div className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5 bg-brand-500/10">
            {n.type === 'training_complete' ? (
              <CheckCircle2 size={16} className="text-emerald-400" />
            ) : n.type === 'batch_shap_complete' ? (
              <AlertTriangle size={16} className="text-amber-400" />
            ) : (
              <Info size={16} className="text-brand-400" />
            )}
          </div>
          <div className="flex-1 min-w-0">
            <h5 className="text-xs font-semibold text-white">{n.title}</h5>
            <p className="text-xs text-gray-400 mt-0.5">{n.message}</p>
          </div>
        </div>
      ))
    )}
  </div>
)
