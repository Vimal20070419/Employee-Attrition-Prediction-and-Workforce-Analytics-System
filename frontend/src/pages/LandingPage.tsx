import { motion } from 'framer-motion'
import { Link } from 'react-router-dom'
import { Zap, Brain, BarChart3, Shield, ArrowRight } from 'lucide-react'

const features = [
  { icon: Brain, title: 'AI-Powered Predictions', desc: '13 ML algorithms trained on IBM HR data with 88%+ accuracy' },
  { icon: BarChart3, title: 'Explainable AI (SHAP)', desc: 'Understand exactly why each employee may leave' },
  { icon: Shield, title: 'Enterprise Security', desc: 'JWT auth, RBAC, bcrypt encryption, audit logs' },
  { icon: Zap, title: 'Real-time Analytics', desc: 'Live dashboards with 20+ interactive visualizations' },
]

const stats = [
  { label: 'Prediction Accuracy', value: '88.4%' },
  { label: 'Models Trained', value: '13' },
  { label: 'Algorithms Used', value: 'XGBoost, LightGBM, CatBoost' },
  { label: 'SHAP Features', value: '30+' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#e6ebf2] overflow-x-hidden text-slate-700">
      {/* Navbar */}
      <nav className="fixed top-0 inset-x-0 z-50 px-8 py-4 flex items-center justify-between backdrop-blur-md border-b border-slate-200/60 bg-[#e6ebf2]/90">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg flex items-center justify-center"
               style={{ background: 'linear-gradient(135deg, #6366f1, #22d3ee)' }}>
            <Zap size={16} className="text-white" />
          </div>
          <span className="font-bold text-white">AttritionIQ</span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/login" className="text-sm text-gray-400 hover:text-white transition-colors">Sign In</Link>
          <Link to="/register" className="btn-primary py-2 px-4 text-xs">Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="pt-32 pb-20 px-8 text-center relative">
        {/* Glow background */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[800px] rounded-full opacity-10"
               style={{ background: 'radial-gradient(circle, #6366f1 0%, transparent 70%)' }} />
        </div>

        <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.7 }}>
          <span className="inline-block px-4 py-1.5 rounded-full text-xs font-semibold mb-6 border"
                style={{ background: 'rgba(99,102,241,0.1)', borderColor: 'rgba(99,102,241,0.3)', color: '#818cf8' }}>
            🚀 Enterprise HR Analytics — Powered by Explainable AI
          </span>

          <h1 className="text-6xl md:text-7xl font-black text-white mb-6 leading-tight">
            Predict Attrition
            <br />
            <span className="gradient-text">Before It Happens</span>
          </h1>

          <p className="text-xl text-gray-400 max-w-2xl mx-auto mb-10 leading-relaxed">
            AttritionIQ uses 13 ML algorithms with SHAP explainability to identify at-risk employees,
            understand why they might leave, and generate actionable retention recommendations.
          </p>

          <div className="flex items-center justify-center gap-4 flex-wrap">
            <Link to="/register" className="btn-primary text-base py-3.5 px-8">
              Start Free Trial <ArrowRight size={18} />
            </Link>
            <Link to="/login" className="btn-secondary text-base py-3.5 px-8">
              View Demo
            </Link>
          </div>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="px-8 py-12">
        <div className="max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="glass-card p-6 text-center"
            >
              <p className="text-2xl font-black gradient-text mb-1">{stat.value}</p>
              <p className="text-sm text-gray-500">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="px-8 py-20">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-4xl font-bold text-white text-center mb-4">
            Everything your HR team needs
          </h2>
          <p className="text-gray-500 text-center mb-12 text-lg">Enterprise-grade features built for data-driven HR decisions</p>

          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, i) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="glass-card-hover p-8 flex gap-5"
              >
                <div className="w-12 h-12 rounded-xl flex-shrink-0 flex items-center justify-center"
                     style={{ background: 'rgba(99,102,241,0.15)', border: '1px solid rgba(99,102,241,0.2)' }}>
                  <feature.icon size={22} className="text-brand-400" />
                </div>
                <div>
                  <h3 className="font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-500 text-sm leading-relaxed">{feature.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-8 py-20 text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          className="max-w-3xl mx-auto glass-card p-16 relative overflow-hidden"
        >
          <div className="absolute inset-0 opacity-5"
               style={{ background: 'linear-gradient(135deg, #6366f1, #22d3ee)' }} />
          <h2 className="text-4xl font-black text-white mb-4">Ready to reduce attrition?</h2>
          <p className="text-gray-400 mb-8 text-lg">Join HR teams using AI to retain their best talent</p>
          <Link to="/register" className="btn-primary text-base py-4 px-10 inline-flex">
            Get Started Free <ArrowRight size={18} />
          </Link>
        </motion.div>
      </section>

      {/* Footer */}
      <footer className="px-8 py-8 border-t border-white/5 text-center text-gray-600 text-sm">
        <p>© 2026 AttritionIQ Platform. Built with FastAPI + React + XGBoost + SHAP.</p>
      </footer>
    </div>
  )
}
