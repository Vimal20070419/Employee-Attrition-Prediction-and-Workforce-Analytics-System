import { Link, useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { motion } from 'framer-motion'
import { Zap, Loader2 } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

const schema = z.object({
  email: z.string().email('Invalid email'),
  username: z.string().min(3, 'At least 3 chars'),
  full_name: z.string().min(2, 'Full name required'),
  password: z.string().min(8, 'At least 8 chars'),
})

type FormData = z.infer<typeof schema>

export default function RegisterPage() {
  const { register: registerAuth } = useAuthStore()
  const navigate = useNavigate()

  const { register, handleSubmit, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = async (data: FormData) => {
    try {
      await registerAuth(data)
      toast.success('Registration successful! Please check your email for verification link.')
      navigate('/login')
    } catch (err: any) {
      toast.error(err?.response?.data?.detail || 'Registration failed')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#e6ebf2] p-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="w-full max-w-md glass-card p-8 space-y-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center neu-pressed text-emerald-600">
            <Zap size={18} />
          </div>
          <span className="text-slate-700 font-bold text-lg">AttritionIQ</span>
        </div>

        <h1 className="text-2xl font-bold text-white">Create Account</h1>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Full Name</label>
            <input {...register('full_name')} className="input-field py-2 text-sm" placeholder="John Doe" />
            {errors.full_name && <p className="text-xs text-red-400 mt-1">{errors.full_name.message}</p>}
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Email</label>
            <input {...register('email')} className="input-field py-2 text-sm" placeholder="john@company.com" />
            {errors.email && <p className="text-xs text-red-400 mt-1">{errors.email.message}</p>}
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Username</label>
            <input {...register('username')} className="input-field py-2 text-sm" placeholder="johndoe" />
            {errors.username && <p className="text-xs text-red-400 mt-1">{errors.username.message}</p>}
          </div>

          <div>
            <label className="block text-xs font-medium text-gray-400 mb-1">Password</label>
            <input {...register('password')} type="password" className="input-field py-2 text-sm" placeholder="••••••••" />
            {errors.password && <p className="text-xs text-red-400 mt-1">{errors.password.message}</p>}
          </div>

          <button type="submit" disabled={isSubmitting} className="btn-primary w-full justify-center py-3">
            {isSubmitting ? <Loader2 size={18} className="animate-spin" /> : 'Register'}
          </button>
        </form>

        <p className="text-center text-gray-500 text-xs">
          Already have an account? <Link to="/login" className="text-brand-400 font-medium">Sign in</Link>
        </p>
      </motion.div>
    </div>
  )
}
