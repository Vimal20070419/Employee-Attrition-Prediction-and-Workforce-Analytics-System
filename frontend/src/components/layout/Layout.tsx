import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { useSidebarStore } from '@/store/sidebarStore'

export default function Layout() {
  const { isCollapsed } = useSidebarStore()

  return (
    <div className="flex h-screen overflow-hidden bg-[#e6ebf2]">
      <Sidebar />
      <div className={`flex-1 flex flex-col overflow-hidden transition-all duration-300 ${isCollapsed ? 'ml-[84px]' : 'ml-[280px]'}`}>
        <Header />
        <main className="flex-1 overflow-y-auto p-6 bg-[#e6ebf2]">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
