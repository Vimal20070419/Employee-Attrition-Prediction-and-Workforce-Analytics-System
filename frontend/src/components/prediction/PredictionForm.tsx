import React from 'react'
import { Brain, Loader2 } from 'lucide-react'

interface PredictionFormProps {
  onSubmit: (e: React.FormEvent) => void
  isLoading: boolean
  children: React.ReactNode
}

export const PredictionForm: React.FC<PredictionFormProps> = ({ onSubmit, isLoading, children }) => (
  <form onSubmit={onSubmit} className="space-y-6">
    {children}
    <button type="submit" disabled={isLoading} className="btn-primary w-full justify-center py-4 text-base">
      {isLoading ? (
        <><Loader2 size={20} className="animate-spin" /> Analyzing with AI...</>
      ) : (
        <><Brain size={20} /> Predict Attrition Risk</>
      )}
    </button>
  </form>
)
