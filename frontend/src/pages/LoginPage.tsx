import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Eye, EyeOff, Zap, Loader2, ShieldCheck, Sparkles } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

const schema = z.object({
  username: z.string().min(1, 'Required'),
  password: z.string().min(1, 'Required'),
  remember: z.boolean().optional(),
})

type FormData = z.infer<typeof schema>

export default function LoginPage() {
  const [showPass, setShowPass] = useState(false)
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await login({ username: data.username, password: data.password })
      toast.success('Welcome back! 👋')
      navigate('/dashboard')
    } catch (err: any) {
      const msg = err?.response?.data?.detail || 'Login failed. Please try again.'
      toast.error(msg)
    }
  }

  return (
    <div className="min-h-screen flex bg-[#e6ebf2] text-slate-700 relative overflow-hidden">
      {/* Left panel — branding hero */}
      <div className="hidden md:flex md:w-1/2 relative overflow-hidden border-r border-slate-200/60 bg-[#e6ebf2]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(99,102,241,0.15),transparent_60%)] pointer-events-none" />

        <div className="relative z-10 p-12 lg:p-16 flex flex-col justify-between h-full w-full">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl flex items-center justify-center shadow-lg shadow-brand-500/30"
                 style={{ background: 'linear-gradient(135deg, #6366f1, #22d3ee)' }}>
              <Zap size={22} className="text-white" />
            </div>
            <div>
              <span className="text-white font-black text-xl tracking-tight">AttritionIQ</span>
              <span className="text-[10px] block text-brand-400 font-semibold uppercase tracking-widest">Enterprise Platform</span>
            </div>
          </div>

          <div className="space-y-6 max-w-lg">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold border border-brand-500/30 bg-brand-500/10 text-brand-300">
              <Sparkles size={14} /> Explainable AI HR Analytics
            </div>
            <h2 className="text-4xl lg:text-5xl font-black text-white leading-tight tracking-tight">
              Predict Attrition <br />
              <span className="gradient-text">Before It Happens</span>
            </h2>
            <p className="text-gray-400 text-base leading-relaxed">
              Empower your HR leadership with 13 machine learning algorithms, SHAP explainability, and automated retention action plans.
            </p>

            <div className="space-y-3 pt-2">
              {[
                '88.4% Champion Model Accuracy',
                '13 ML Algorithms (XGBoost, CatBoost)',
                'SHAP Force & Feature Explanations',
                'Automated PDF & Excel Report Generation'
              ].map((feat) => (
                <div key={feat} className="flex items-center gap-3">
                  <div className="w-5 h-5 rounded-full flex items-center justify-center bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-xs font-bold">
                    ✓
                  </div>
                  <span className="text-gray-300 text-sm font-medium">{feat}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2 text-xs text-gray-500">
            <ShieldCheck size={16} className="text-emerald-400" />
            <span>Bank-grade JWT Auth & Security Audit Logs</span>
          </div>
        </div>
      </div>

      {/* Right panel — Form Card */}
      <div className="flex-1 flex items-center justify-center p-6 lg:p-12 relative z-10">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
          className="w-full max-w-md glass-card p-8 lg:p-10 border border-white/10 shadow-2xl relative overflow-hidden"
        >
          {/* Top accent bar */}
          <div className="absolute top-0 left-0 right-0 h-1.5 bg-gradient-to-r from-brand-500 via-brand-secondary to-accent-cyan" />

          {/* Mobile Logo */}
          <div className="flex md:hidden items-center gap-3 mb-6">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center shadow-md shadow-brand-500/30"
                 style={{ background: 'linear-gradient(135deg, #6366f1, #22d3ee)' }}>
              <Zap size={18} className="text-white" />
            </div>
            <span className="text-white font-bold text-lg">AttritionIQ</span>
          </div>

          <h1 className="text-2xl lg:text-3xl font-black text-white tracking-tight mb-2">Welcome Back</h1>
          <p className="text-gray-400 text-sm mb-8">Sign in to your enterprise account</p>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
            <div>
              <label className="block text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2">Email or Username</label>
              <input
                {...register('username')}
                className="input-field py-3 text-sm"
                placeholder="admin@attritioniq.com"
                autoComplete="username"
              />
              {errors.username && <p className="mt-1.5 text-xs text-rose-400">{errors.username.message}</p>}
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-semibold text-gray-300 uppercase tracking-wider">Password</label>
                <Link to="/forgot-password" className="text-xs text-brand-400 hover:text-brand-300 font-medium transition-colors">Forgot password?</Link>
              </div>
              <div className="relative">
                <input
                  {...register('password')}
                  type={showPass ? 'text' : 'password'}
                  className="input-field py-3 pr-11 text-sm"
                  placeholder="••••••••"
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(!showPass)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors"
                >
                  {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
              {errors.password && <p className="mt-1.5 text-xs text-rose-400">{errors.password.message}</p>}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="btn-primary w-full justify-center py-3.5 text-sm font-bold tracking-wide shadow-lg shadow-brand-500/30"
            >
              {isSubmitting ? (
                <><Loader2 size={18} className="animate-spin" /> Authenticating...</>
              ) : (
                'Sign In to Platform'
              )}
            </button>
          </form>

          {/* Demo credentials helper card */}
          <div className="mt-8 p-4 rounded-xl border border-brand-500/20 bg-brand-500/10 text-xs space-y-1 text-gray-300">
            <p className="font-bold text-brand-300 flex items-center gap-1.5 mb-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
              Demo Credentials:
            </p>
            <p>Username: <code className="text-brand-300 font-mono font-bold">admin@attritioniq.com</code></p>
            <p>Password: <code className="text-brand-300 font-mono font-bold">Admin@123</code></p>
          </div>

          <p className="text-center text-gray-500 mt-6 text-xs">
            Don't have an account?{' '}
            <Link to="/register" className="text-brand-400 hover:text-brand-300 font-bold underline underline-offset-4">Create account</Link>
          </p>
        </motion.div>
      </div>
    </div>
  )
}
