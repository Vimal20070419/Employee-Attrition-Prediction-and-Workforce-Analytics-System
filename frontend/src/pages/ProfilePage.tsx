import { motion } from 'framer-motion'
import { useAuthStore } from '@/store/authStore'
import { User } from 'lucide-react'

export default function ProfilePage() {
  const { user } = useAuthStore()

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
          <User size={24} className="text-brand-400" /> My Profile
        </h1>
        <p className="text-gray-500 text-sm mt-1">Manage your account details and role permissions</p>
      </div>

      <div className="glass-card p-8 space-y-6">
        <div className="flex items-center gap-6 pb-6 border-b border-white/5">
          <div className="w-20 h-20 rounded-2xl flex items-center justify-center text-white text-2xl font-bold"
               style={{ background: 'linear-gradient(135deg, #6366f1, #22d3ee)' }}>
            {user?.full_name?.charAt(0) || 'U'}
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">{user?.full_name}</h2>
            <p className="text-sm text-gray-500">{user?.email}</p>
            <span className="badge-medium text-xs mt-2 inline-block capitalize">{user?.role?.replace('_', ' ')}</span>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <label className="text-xs text-gray-500 font-medium block mb-1">Username</label>
            <input className="input-field cursor-not-allowed opacity-60" value={user?.username || ''} readOnly />
          </div>
          <div>
            <label className="text-xs text-gray-500 font-medium block mb-1">Email</label>
            <input className="input-field cursor-not-allowed opacity-60" value={user?.email || ''} readOnly />
          </div>
        </div>
      </div>
    </motion.div>
  )
}
