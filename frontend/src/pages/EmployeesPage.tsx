import { useState } from 'react'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { Users, Plus, Search, Filter, X } from 'lucide-react'
import { apiGet } from '@/lib/api'
import toast from 'react-hot-toast'

interface EmployeeListResponse {
  items: any[]
  total: number
  page: number
  page_size: number
  pages: number
}

const MOCK_EMPLOYEES = [
  { id: '1001', employee_number: 'EMP-1001', job_role: 'Sales Representative', department: 'Sales', age: 29, monthly_income: 2850, over_time: true, years_at_company: 2, attrition: 'Yes' },
  { id: '1002', employee_number: 'EMP-1002', job_role: 'Research Scientist', department: 'Research & Development', age: 34, monthly_income: 6200, over_time: false, years_at_company: 6, attrition: 'No' },
  { id: '1003', employee_number: 'EMP-1003', job_role: 'Laboratory Technician', department: 'Research & Development', age: 26, monthly_income: 3100, over_time: true, years_at_company: 1, attrition: 'Yes' },
  { id: '1004', employee_number: 'EMP-1004', job_role: 'Manufacturing Director', department: 'Research & Development', age: 48, monthly_income: 14200, over_time: false, years_at_company: 15, attrition: 'No' },
  { id: '1005', employee_number: 'EMP-1005', job_role: 'Healthcare Representative', department: 'Research & Development', age: 39, monthly_income: 8500, over_time: false, years_at_company: 9, attrition: 'No' },
  { id: '1006', employee_number: 'EMP-1006', job_role: 'Human Resources Exec', department: 'Human Resources', age: 31, monthly_income: 4200, over_time: true, years_at_company: 3, attrition: 'Yes' },
  { id: '1007', employee_number: 'EMP-1007', job_role: 'Sales Executive', department: 'Sales', age: 41, monthly_income: 9800, over_time: false, years_at_company: 11, attrition: 'No' },
  { id: '1008', employee_number: 'EMP-1008', job_role: 'Manager', department: 'Research & Development', age: 52, monthly_income: 17500, over_time: false, years_at_company: 18, attrition: 'No' },
  { id: '1009', employee_number: 'EMP-1009', job_role: 'Research Director', department: 'Research & Development', age: 45, monthly_income: 16200, over_time: false, years_at_company: 14, attrition: 'No' },
  { id: '1010', employee_number: 'EMP-1010', job_role: 'Sales Representative', department: 'Sales', age: 24, monthly_income: 2400, over_time: true, years_at_company: 1, attrition: 'Yes' },
]

export default function EmployeesPage() {
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [attritionFilter, setAttritionFilter] = useState<string>('')
  const [showAddModal, setShowAddModal] = useState(false)

  // Local employee list state for offline additions
  const [localEmployees, setLocalEmployees] = useState(MOCK_EMPLOYEES)
  const [newEmp, setNewEmp] = useState({
    job_role: 'Sales Representative',
    department: 'Sales',
    age: 30,
    monthly_income: 5000,
    over_time: false,
    years_at_company: 2,
    attrition: 'No',
  })

  const { data } = useQuery<EmployeeListResponse>({
    queryKey: ['employees', page, search, attritionFilter],
    queryFn: () =>
      apiGet<EmployeeListResponse>('/employees', {
        page,
        page_size: 20,
        search: search || undefined,
        attrition: attritionFilter || undefined,
      }).catch(() => ({
        items: localEmployees,
        total: localEmployees.length,
        page: 1,
        page_size: 20,
        pages: 1,
      })),
    placeholderData: { items: localEmployees, total: localEmployees.length, page: 1, page_size: 20, pages: 1 },
  })

  const rawEmployees = data?.items?.length ? data.items : localEmployees

  // Filter local items by search & attrition filter
  const filteredEmployees = rawEmployees.filter((emp: any) => {
    const matchesSearch = search ? (
      emp.job_role?.toLowerCase().includes(search.toLowerCase()) ||
      emp.employee_number?.toLowerCase().includes(search.toLowerCase()) ||
      emp.department?.toLowerCase().includes(search.toLowerCase())
    ) : true
    const matchesAttrition = attritionFilter ? emp.attrition === attritionFilter : true
    return matchesSearch && matchesAttrition
  })

  const handleAddSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const created = {
      id: String(Date.now()),
      employee_number: `EMP-${Math.floor(1000 + Math.random() * 9000)}`,
      ...newEmp,
    }
    setLocalEmployees([created, ...localEmployees])
    setShowAddModal(false)
    toast.success(`Employee ${created.employee_number} added successfully!`)
  }

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Employees Directory</h1>
          <p className="text-gray-400 text-sm mt-1">{filteredEmployees.length} employee records</p>
        </div>
        <button onClick={() => setShowAddModal(true)} className="btn-primary">
          <Plus size={16} /> Add Employee
        </button>
      </div>

      {/* Filters */}
      <div className="glass-card p-4 flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[220px]">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            className="input-field pl-9 py-2.5 text-sm"
            placeholder="Search role, employee number, department..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
          />
        </div>
        <select
          className="input-field py-2.5 w-44 text-sm"
          value={attritionFilter}
          onChange={(e) => { setAttritionFilter(e.target.value); setPage(1) }}
        >
          <option value="">All Statuses</option>
          <option value="Yes">Attrited (Left)</option>
          <option value="No">Active</option>
        </select>
        <div className="flex items-center gap-2 text-xs text-gray-400">
          <Filter size={14} />
          <span>Showing {filteredEmployees.length} items</span>
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-white/10 bg-white/[0.02]">
                {['Employee ID', 'Job Role', 'Department', 'Age', 'Monthly Income', 'Overtime', 'Tenure', 'Status'].map((h) => (
                  <th key={h} className="text-left px-5 py-4 text-xs text-gray-400 font-bold uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filteredEmployees.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-center py-16 text-gray-500">
                    <Users size={36} className="mx-auto mb-3 opacity-30" />
                    <p>No employees match your search criteria</p>
                  </td>
                </tr>
              ) : (
                filteredEmployees.map((emp: any) => (
                  <tr key={emp.id} className="border-b border-white/[0.03] hover:bg-white/[0.03] transition-colors cursor-pointer">
                    <td className="px-5 py-4 font-mono text-xs text-brand-300 font-bold">
                      {emp.employee_number || emp.id}
                    </td>
                    <td className="px-5 py-4 text-white font-medium">{emp.job_role}</td>
                    <td className="px-5 py-4 text-gray-300">{emp.department}</td>
                    <td className="px-5 py-4 text-gray-300">{emp.age} yrs</td>
                    <td className="px-5 py-4 text-emerald-400 font-bold">${emp.monthly_income?.toLocaleString()}</td>
                    <td className="px-5 py-4">
                      <span className={emp.over_time ? 'badge-high' : 'badge-low'}>
                        {emp.over_time ? 'Yes' : 'No'}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-gray-300">{emp.years_at_company} yrs</td>
                    <td className="px-5 py-4">
                      <span className={emp.attrition === 'Yes' ? 'badge-critical' : 'badge-low'}>
                        {emp.attrition === 'Yes' ? 'Attrited' : 'Active'}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Employee Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/70 backdrop-blur-md z-50 flex items-center justify-center p-4">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="glass-card p-6 max-w-lg w-full space-y-4">
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="text-lg font-bold text-white">Add New Employee</h3>
              <button onClick={() => setShowAddModal(false)} className="text-gray-400 hover:text-white">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleAddSubmit} className="space-y-4 text-sm">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Job Role</label>
                  <input
                    className="input-field py-2 text-sm"
                    value={newEmp.job_role}
                    onChange={(e) => setNewEmp({ ...newEmp, job_role: e.target.value })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Department</label>
                  <select
                    className="input-field py-2 text-sm"
                    value={newEmp.department}
                    onChange={(e) => setNewEmp({ ...newEmp, department: e.target.value })}
                  >
                    <option value="Sales">Sales</option>
                    <option value="Research & Development">Research & Development</option>
                    <option value="Human Resources">Human Resources</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Age</label>
                  <input
                    type="number"
                    className="input-field py-2 text-sm"
                    value={newEmp.age}
                    onChange={(e) => setNewEmp({ ...newEmp, age: Number(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Monthly Salary ($)</label>
                  <input
                    type="number"
                    className="input-field py-2 text-sm"
                    value={newEmp.monthly_income}
                    onChange={(e) => setNewEmp({ ...newEmp, monthly_income: Number(e.target.value) })}
                    required
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-400 mb-1">Tenure (Years)</label>
                  <input
                    type="number"
                    className="input-field py-2 text-sm"
                    value={newEmp.years_at_company}
                    onChange={(e) => setNewEmp({ ...newEmp, years_at_company: Number(e.target.value) })}
                    required
                  />
                </div>
              </div>

              <div className="flex items-center gap-6 pt-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={newEmp.over_time}
                    onChange={(e) => setNewEmp({ ...newEmp, over_time: e.target.checked })}
                    className="accent-brand-500 w-4 h-4"
                  />
                  <span className="text-gray-300">Works Overtime</span>
                </label>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-white/10">
                <button type="button" onClick={() => setShowAddModal(false)} className="btn-secondary py-2 px-4 text-xs">
                  Cancel
                </button>
                <button type="submit" className="btn-primary py-2 px-4 text-xs">
                  Save Employee
                </button>
              </div>
            </form>
          </motion.div>
        </div>
      )}
    </motion.div>
  )
}
