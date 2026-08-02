import React from 'react'
import { Loader2 } from 'lucide-react'

export const LoadingSpinner: React.FC<{ size?: number }> = ({ size = 24 }) => (
  <div className="flex items-center justify-center p-8">
    <Loader2 size={size} className="animate-spin text-brand-500" />
  </div>
)
