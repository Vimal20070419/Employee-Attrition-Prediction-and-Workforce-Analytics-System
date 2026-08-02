import React from 'react'

interface ConfirmDialogProps {
  isOpen: boolean
  title: string
  message: string
  onConfirm: () => void
  onCancel: () => void
}

export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({ isOpen, title, message, onConfirm, onCancel }) => {
  if (!isOpen) return null
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="glass-card max-w-md w-full p-6 space-y-4">
        <h3 className="text-lg font-bold text-white">{title}</h3>
        <p className="text-sm text-gray-400">{message}</p>
        <div className="flex justify-end gap-3 pt-2">
          <button onClick={onCancel} className="btn-secondary py-2 px-4 text-xs">Cancel</button>
          <button onClick={onConfirm} className="btn-danger py-2 px-4 text-xs">Confirm</button>
        </div>
      </div>
    </div>
  )
}
