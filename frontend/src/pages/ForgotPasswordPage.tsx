import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Zap } from 'lucide-react'

export default function ForgotPasswordPage() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#e6ebf2] p-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md glass-card p-8 text-center space-y-6">
        <div className="w-12 h-12 rounded-2xl mx-auto flex items-center justify-center neu-pressed text-emerald-600">
          <Zap size={24} />
        </div>
        <h1 className="text-2xl font-bold text-slate-700">Reset Password</h1>
        <p className="text-slate-500 text-sm font-medium">Enter your registered email address to receive password reset instructions</p>
        <input className="input-field" placeholder="you@company.com" />
        <button className="btn-primary w-full justify-center">Send Reset Email</button>
        <p className="text-xs text-slate-500">
          Remember password? <Link to="/login" className="text-emerald-600 font-semibold">Back to Login</Link>
        </p>
      </motion.div>
    </div>
  )
}
