import React from 'react'

interface DataTableProps {
  headers: string[]
  children: React.ReactNode
}

export const DataTable: React.FC<DataTableProps> = ({ headers, children }) => (
  <div className="glass-card overflow-hidden">
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/5">
            {headers.map((h) => (
              <th key={h} className="text-left px-5 py-4 text-xs text-gray-500 font-semibold uppercase tracking-wide">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>{children}</tbody>
      </table>
    </div>
  </div>
)
