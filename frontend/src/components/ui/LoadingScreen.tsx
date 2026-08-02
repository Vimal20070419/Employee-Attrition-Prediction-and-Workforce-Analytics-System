import { motion } from 'framer-motion'
import { Zap } from 'lucide-react'

export default function LoadingScreen() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-[#e6ebf2] z-50">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        className="flex flex-col items-center gap-6"
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
          className="w-16 h-16 rounded-2xl flex items-center justify-center shadow-[4px_4px_10px_rgba(180,192,208,0.5),-4px_-4px_10px_#ffffff]"
          style={{ background: 'linear-gradient(145deg, #10b981, #059669)' }}
        >
          <Zap size={28} className="text-white drop-shadow-sm" />
        </motion.div>
        <div className="text-center">
          <p className="text-xl font-bold gradient-text">AttritionIQ</p>
          <p className="text-sm text-slate-500 font-medium mt-1">Loading platform...</p>
        </div>
        <div className="w-48 h-1.5 neu-pressed rounded-full overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: 'linear-gradient(90deg, #10b981, #00e676)' }}
            initial={{ x: '-100%' }}
            animate={{ x: '100%' }}
            transition={{ duration: 1.5, repeat: Infinity, ease: 'easeInOut' }}
          />
        </div>
      </motion.div>
    </div>
  )
}
