import { motion } from 'framer-motion'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Shield } from 'lucide-react'
import { apiGet, apiPatch } from '@/lib/api'
import toast from 'react-hot-toast'

export default function AdminPanelPage() {
  const qc = useQueryClient()

  const { data: usersData, isLoading } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: () => apiGet<any>('/admin/users'),
  })

  const users = usersData?.items || []

  const updateRoleMutation = useMutation({
    mutationFn: ({ userId, role }: { userId: string; role: string }) =>
      apiPatch(`/admin/users/${userId}/role?role=${role}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['admin', 'users'] })
      toast.success('User role updated')
    },
    onError: (err: any) => toast.error(err?.response?.data?.detail || 'Failed to update role'),
  })

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-brand-500/20 text-brand-400">
          <Shield size={22} />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Admin Panel</h1>
          <p className="text-gray-500 text-sm mt-1">User role management and system security audit logs</p>
        </div>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="p-5 border-b border-white/5">
          <h3 className="text-sm font-bold text-white">System Users</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/5">
                {['User', 'Email', 'Role', 'Status', 'Joined'].map((h) => (
                  <th key={h} className="text-left px-5 py-4 text-xs text-gray-500 font-semibold uppercase tracking-wide">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                Array(3).fill(0).map((_, i) => (
                  <tr key={i} className="border-b border-white/[0.03]">
                    {Array(5).fill(0).map((_, j) => (
                      <td key={j} className="px-5 py-4"><div className="skeleton h-4 rounded w-24" /></td>
                    ))}
                  </tr>
                ))
              ) : (
                users.map((u: any) => (
                <tr key={u.id} className="border-b border-white/[0.03]">
                  <td className="px-5 py-4 font-semibold text-white">{u.full_name}</td>
                  <td className="px-5 py-4 text-gray-400">{u.email}</td>
                  <td className="px-5 py-4">
                    <select
                      value={u.role}
                      onChange={(e) => updateRoleMutation.mutate({ userId: u.id, role: e.target.value })}
                      className="input-field py-1 text-xs w-32"
                    >
                      <option value="admin">Admin</option>
                      <option value="hr_manager">HR Manager</option>
                      <option value="hr_analyst">HR Analyst</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </td>
                  <td className="px-5 py-4"><span className="badge-low">{u.status}</span></td>
                  <td className="px-5 py-4 text-gray-500 text-xs">{new Date(u.created_at).toLocaleDateString()}</td>
                </tr>
              )))
              }
            </tbody>
          </table>
        </div>
      </div>
    </motion.div>
  )
}
