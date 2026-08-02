import { NavLink, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, Users, Brain, BarChart3, FileText,
  Cpu, Bell, User, Shield, LogOut, ChevronLeft, ChevronRight,
  Plus, Edit2, Sliders, Database, Sparkles, Home, Pin
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useSidebarStore } from '@/store/sidebarStore'
import toast from 'react-hot-toast'

const menuItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/predictions', icon: Brain, label: 'My Tasks', badge: '3' },
  { to: '/employees', icon: Users, label: 'Employees' },
  { to: '/notifications', icon: Bell, label: 'Notifications', badge: '5', badgeColor: 'bg-rose-500' },
  { to: '/analytics', icon: BarChart3, label: 'Analytics' },
  { to: '/reports', icon: FileText, label: 'Reports' },
  { to: '/models', icon: Cpu, label: 'Models' },
]

const pluginItems = [
  { name: 'CatBoost ML', color: 'bg-emerald-500', icon: Sparkles },
  { name: 'PostgreSQL DB', color: 'bg-blue-500', icon: Database },
  { name: 'Google AI / SHAP', color: 'bg-amber-500', icon: Cpu },
]

export default function Sidebar() {
  const { user, logout } = useAuthStore()
  const { isCollapsed, toggleCollapsed } = useSidebarStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    toast.success('Logged out successfully')
    navigate('/login')
  }

  const handleCreateTask = () => {
    navigate('/predictions')
    toast.success('Opening prediction task workspace')
  }

  return (
    <aside className={`sidebar ${isCollapsed ? 'w-[84px]' : 'w-[280px]'}`}>
      {/* Top Window Controls & Collapse Toggle */}
      <div className="p-4 flex items-center justify-between border-b border-slate-200/50">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-400 shadow-sm" />
          <span className="w-2.5 h-2.5 rounded-full bg-amber-400 shadow-sm" />
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-sm" />
        </div>
        <button
          onClick={toggleCollapsed}
          className="p-1.5 rounded-xl neu-hover text-slate-500 hover:text-emerald-600 transition-colors"
          title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
        </button>
      </div>

      {/* User Profile Concept Header */}
      <div className={`p-4 border-b border-slate-200/50 ${isCollapsed ? 'flex justify-center' : ''}`}>
        {isCollapsed ? (
          <div
            onClick={() => navigate('/profile')}
            className="w-11 h-11 rounded-2xl neu-pressed flex items-center justify-center cursor-pointer relative"
            title={user?.full_name || 'Amol Kuntla'}
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-bold text-sm shadow-sm">
              {user?.full_name?.charAt(0) || 'A'}
            </div>
          </div>
        ) : (
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl neu-pressed p-1 flex items-center justify-center flex-shrink-0">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center text-white font-bold text-base shadow-sm">
                {user?.full_name?.charAt(0) || 'A'}
              </div>
            </div>
            <div className="overflow-hidden">
              <p className="text-xs text-slate-400 font-semibold tracking-wide">Hello,</p>
              <p className="text-base font-extrabold text-slate-700 truncate">{user?.full_name || 'Amol Kuntla'}</p>
            </div>
          </div>
        )}
      </div>

      {/* Scrollable Body */}
      <div className="flex-1 p-3 space-y-5 overflow-y-auto custom-scrollbar">
        {/* Section 1: Menu */}
        <div>
          {!isCollapsed && (
            <div className="flex items-center justify-between px-2 mb-2">
              <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">Menu</span>
              <button className="text-slate-400 hover:text-slate-600 transition-colors">
                <Edit2 size={13} />
              </button>
            </div>
          )}

          <nav className="space-y-1.5">
            {menuItems.map((item, i) => (
              <motion.div
                key={item.to}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <NavLink
                  to={item.to}
                  className={({ isActive }) =>
                    `sidebar-link group ${isActive ? 'active' : ''} ${isCollapsed ? 'justify-center px-0' : ''}`
                  }
                  title={isCollapsed ? item.label : undefined}
                >
                  {({ isActive }) => (
                    <>
                      {/* Left Active Indicator Bar */}
                      {isActive && (
                        <motion.span
                          layoutId="activeBar"
                          className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-6 rounded-r-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]"
                        />
                      )}

                      <item.icon size={19} className={isActive ? 'text-emerald-600' : 'text-slate-500 group-hover:text-emerald-600'} />

                      {!isCollapsed && (
                        <span className={`flex-1 truncate ${isActive ? 'font-bold text-emerald-700' : ''}`}>
                          {item.label}
                        </span>
                      )}

                      {/* Item Badges */}
                      {item.badge && (
                        <span
                          className={`${
                            item.badgeColor || 'bg-emerald-500'
                          } text-white text-[10px] font-extrabold rounded-full ${
                            isCollapsed
                              ? 'absolute top-1.5 right-1.5 w-4 h-4 flex items-center justify-center'
                              : 'px-2 py-0.5'
                          }`}
                        >
                          {item.badge}
                        </span>
                      )}
                    </>
                  )}
                </NavLink>
              </motion.div>
            ))}

            {/* Admin Panel Link */}
            {user?.role === 'admin' && (
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  `sidebar-link ${isActive ? 'active' : ''} ${isCollapsed ? 'justify-center px-0' : ''}`
                }
              >
                {({ isActive }) => (
                  <>
                    {isActive && (
                      <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1.5 h-6 rounded-r-full bg-emerald-500" />
                    )}
                    <Shield size={19} className={isActive ? 'text-emerald-600' : 'text-slate-500'} />
                    {!isCollapsed && <span>Admin Panel</span>}
                  </>
                )}
              </NavLink>
            )}
          </nav>
        </div>

        {/* Section 2: Plugins / Integrations */}
        <div>
          {!isCollapsed ? (
            <div>
              <div className="flex items-center justify-between px-2 mb-2">
                <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">Plugins</span>
                <button className="text-slate-400 hover:text-slate-600 transition-colors">
                  <Edit2 size={13} />
                </button>
              </div>

              <div className="p-2.5 rounded-2xl neu-pressed space-y-2">
                {pluginItems.map((plugin) => (
                  <div key={plugin.name} className="flex items-center gap-2.5 p-1.5 rounded-xl hover:bg-slate-200/50 transition-colors cursor-pointer text-slate-600">
                    <span className={`w-2.5 h-2.5 rounded-full ${plugin.color}`} />
                    <span className="text-xs font-semibold truncate">{plugin.name}</span>
                  </div>
                ))}
                <button className="w-full mt-1 flex items-center gap-2 px-2 py-1.5 rounded-xl text-xs font-bold text-slate-500 hover:text-emerald-600 transition-colors">
                  <Plus size={14} />
                  <span>Add new plugin</span>
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2 pt-2 border-t border-slate-200/50">
              <span className="text-[10px] font-bold text-slate-400 uppercase">Plugins</span>
              {pluginItems.map((plugin) => (
                <div key={plugin.name} title={plugin.name} className="w-8 h-8 rounded-xl neu-pressed flex items-center justify-center cursor-pointer">
                  <span className={`w-2.5 h-2.5 rounded-full ${plugin.color}`} />
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Section 3: Settings Quick Action Bar */}
        <div>
          {!isCollapsed ? (
            <div>
              <div className="flex items-center justify-between px-2 mb-2">
                <span className="text-[11px] font-bold tracking-wider text-slate-400 uppercase">Settings</span>
                <button className="text-slate-400 hover:text-slate-600 transition-colors">
                  <Edit2 size={13} />
                </button>
              </div>

              {/* Horizontal Icon Strip */}
              <div className="flex items-center justify-between p-2 rounded-2xl neu-pressed text-slate-500">
                <button onClick={() => navigate('/dashboard')} className="p-1.5 rounded-xl hover:text-emerald-600 hover:bg-slate-200/60 transition-colors" title="Dashboard">
                  <Home size={16} />
                </button>
                <button onClick={() => navigate('/analytics')} className="p-1.5 rounded-xl hover:text-emerald-600 hover:bg-slate-200/60 transition-colors" title="Analytics">
                  <BarChart3 size={16} />
                </button>
                <button onClick={() => navigate('/settings')} className="p-1.5 rounded-xl hover:text-emerald-600 hover:bg-slate-200/60 transition-colors" title="Settings">
                  <Sliders size={16} />
                </button>
                <button onClick={() => navigate('/reports')} className="p-1.5 rounded-xl hover:text-emerald-600 hover:bg-slate-200/60 transition-colors" title="Reports">
                  <Pin size={16} />
                </button>
                <button onClick={() => navigate('/profile')} className="p-1.5 rounded-xl hover:text-emerald-600 hover:bg-slate-200/60 transition-colors" title="Profile">
                  <User size={16} />
                </button>
              </div>
            </div>
          ) : (
            <div className="flex flex-col items-center gap-2">
              <button onClick={() => navigate('/settings')} className="w-10 h-10 rounded-2xl neu-pressed flex items-center justify-center text-slate-500 hover:text-emerald-600" title="Settings">
                <Sliders size={18} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Bottom Floating CTA Card */}
      <div className="p-3 border-t border-slate-200/50">
        {!isCollapsed ? (
          <div
            onClick={handleCreateTask}
            className="p-3 rounded-2xl neu-pressed hover:shadow-[5px_5px_12px_rgba(180,192,208,0.5),-5px_-5px_12px_#ffffff] transition-all cursor-pointer flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white flex items-center justify-center shadow-md group-hover:scale-105 transition-transform">
              <Plus size={18} />
            </div>
            <div className="overflow-hidden">
              <p className="text-xs font-extrabold text-slate-700">Create new task</p>
              <p className="text-[10px] text-emerald-600 font-semibold">AI Prediction Workspace</p>
            </div>
          </div>
        ) : (
          <button
            onClick={handleCreateTask}
            className="w-12 h-12 mx-auto rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 text-white flex items-center justify-center shadow-md hover:scale-105 transition-transform"
            title="Create new task"
          >
            <Plus size={20} />
          </button>
        )}

        {/* Logout Quick Button */}
        {!isCollapsed && (
          <button
            onClick={handleLogout}
            className="mt-2 w-full flex items-center justify-center gap-2 px-3 py-2 rounded-xl text-xs font-bold text-rose-500 hover:text-rose-600 hover:bg-rose-50/50 transition-colors"
          >
            <LogOut size={14} />
            <span>Sign Out</span>
          </button>
        )}
      </div>
    </aside>
  )
}
