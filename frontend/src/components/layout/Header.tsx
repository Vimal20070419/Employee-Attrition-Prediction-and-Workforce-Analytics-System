import { Bell, Search, Moon, Sun } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useAuthStore } from '@/store/authStore'

export default function Header() {
  const { user } = useAuthStore()
  const navigate = useNavigate()
  const [darkMode, setDarkMode] = useState(false)

  return (
    <header className="h-16 flex items-center justify-between px-6 border-b border-white/80 bg-[#e6ebf2] shadow-[3px_3px_8px_rgba(180,192,208,0.45)] sticky top-0 z-40">
      {/* Search */}
      <div className="relative">
        <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
        <input
          className="input-field pl-10 pr-4 py-2 text-sm w-72 transition-all placeholder:text-slate-400 text-slate-700 font-medium"
          placeholder="Search employees, predictions..."
        />
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        {/* Theme toggle */}
        <motion.button
          whileTap={{ scale: 0.92 }}
          onClick={() => setDarkMode(!darkMode)}
          className="p-2.5 rounded-2xl text-slate-600 hover:text-slate-800 bg-[#e6ebf2] shadow-[3px_3px_8px_rgba(180,192,208,0.45),-3px_-3px_8px_#ffffff] hover:shadow-[5px_5px_12px_rgba(170,182,200,0.55),-5px_-5px_12px_#ffffff] transition-all"
        >
          {darkMode ? <Moon size={18} className="text-emerald-600" /> : <Sun size={18} className="text-amber-500" />}
        </motion.button>

        {/* Notifications */}
        <motion.button
          whileTap={{ scale: 0.92 }}
          onClick={() => navigate('/notifications')}
          className="relative p-2.5 rounded-2xl text-slate-600 hover:text-slate-800 bg-[#e6ebf2] shadow-[3px_3px_8px_rgba(180,192,208,0.45),-3px_-3px_8px_#ffffff] hover:shadow-[5px_5px_12px_rgba(170,182,200,0.55),-5px_-5px_12px_#ffffff] transition-all"
        >
          <Bell size={18} />
          <span className="absolute top-2 right-2 w-2.5 h-2.5 rounded-full bg-emerald-500" />
        </motion.button>

        {/* Avatar */}
        <button
          onClick={() => navigate('/profile')}
          className="flex items-center gap-3 p-1.5 px-3 rounded-2xl bg-[#e6ebf2] shadow-[3px_3px_8px_rgba(180,192,208,0.45),-3px_-3px_8px_#ffffff] hover:shadow-[5px_5px_12px_rgba(170,182,200,0.55),-5px_-5px_12px_#ffffff] transition-all"
        >
          <div className="w-8 h-8 rounded-xl flex items-center justify-center text-white text-xs font-bold"
               style={{ background: 'linear-gradient(145deg, #10b981, #059669)' }}>
            {user?.full_name?.charAt(0) || 'A'}
          </div>
          <div className="hidden md:block text-left">
            <p className="text-xs font-bold text-slate-700 leading-tight">{user?.full_name?.split(' ')[0] || 'User'}</p>
            <p className="text-[11px] text-slate-500 capitalize font-medium">{user?.role?.replace('_', ' ') || 'Admin'}</p>
          </div>
        </button>
      </div>
    </header>
  )
}
