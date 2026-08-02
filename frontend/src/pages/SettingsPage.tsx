import { motion } from 'framer-motion'
import { Bell } from 'lucide-react'

export default function SettingsPage() {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6 max-w-3xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <p className="text-gray-500 text-sm mt-1">Platform configuration and system preferences</p>
      </div>

      <div className="glass-card p-6 space-y-6">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Bell size={16} className="text-brand-400" /> Notifications & Alerts
        </h3>
        <div className="space-y-4 text-sm text-gray-300">
          <label className="flex items-center justify-between cursor-pointer">
            <span>Email notifications for high-risk predictions</span>
            <input type="checkbox" defaultChecked className="w-4 h-4 rounded accent-brand-500" />
          </label>
          <label className="flex items-center justify-between cursor-pointer">
            <span>Weekly scheduled report delivery</span>
            <input type="checkbox" defaultChecked className="w-4 h-4 rounded accent-brand-500" />
          </label>
        </div>
      </div>
    </motion.div>
  )
}
