import { Outlet, NavLink, useLocation, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Separator } from '@/components/ui/separator'
import { BarChart3, Crosshair, Settings, MapPin, Menu, X, Brain, Store, LogOut, ShieldCheck, Compass } from 'lucide-react'
import { api } from '@/services/api'
import { useAuth } from '@/context/AuthContext'

export default function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const location = useLocation()
  const navigate = useNavigate()
  const [contextData, setContextData] = useState<any>({})
  const { profile, user, signOut } = useAuth()

  useEffect(() => {
    const fetchContext = async () => {
      try {
        const ctx = await api.getContext()
        if (ctx) setContextData(ctx)
      } catch {}
    }
    fetchContext()
  }, [location.pathname])

  const navItems = [
    { name: 'Overview', path: '/dashboard/overview', icon: BarChart3 },
    { name: 'Simulation', path: '/dashboard/simulation', icon: Crosshair },
    { name: 'Competitors', path: '/dashboard/competitors', icon: Store },
    { name: 'Memory Timeline', path: '/dashboard/memory', icon: Brain },
    { name: 'Settings', path: '/dashboard/settings', icon: Settings },
  ]

  const pageTitle = navItems.find(item => location.pathname.startsWith(item.path))?.name || 'Dashboard'

  const handleSignOut = () => {
    localStorage.removeItem('venturescope_user')
    navigate('/login', { replace: true })
  }

  const SidebarContent = () => (
    <div className="flex flex-col h-full bg-[#F8F2EC] text-[#3D2A2D]">
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-5 border-b border-[#E8D7D0] bg-[#FFF9F6]/60 backdrop-blur-sm">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-xl bg-[#EFC7CD]/50 border border-[#D98B95]/30 flex items-center justify-center text-[#7A3E46] shadow-xs">
            <Compass className="w-4 h-4 text-[#7A3E46]" />
          </div>
          <span className="text-base font-serif font-bold tracking-tight text-[#3D2A2D]">
            VentureScope
          </span>
        </div>
        <div className="flex items-center gap-1 text-[10px] text-[#2E5A36] font-semibold bg-[#E8F0EA] border border-[#D4E2D7] px-2 py-0.5 rounded-full">
          <ShieldCheck className="w-3 h-3" />
          Live
        </div>
      </div>

      {/* Nav links */}
      <nav className="flex-1 px-3 py-5 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            onClick={() => setMobileOpen(false)}
            className={({ isActive }) => cn(
              'flex items-center gap-3 px-3.5 py-2.5 rounded-2xl text-xs font-medium transition-all duration-150',
              isActive
                ? 'bg-[#EFC7CD]/40 text-[#7A3E46] font-semibold shadow-[0_2px_10px_rgba(217,139,149,0.2)] border border-[#D98B95]/40'
                : 'text-[#7A666A] hover:text-[#3D2A2D] hover:bg-[#F8E8EA]'
            )}
          >
            <item.icon className="w-4 h-4" />
            <span className="tracking-wide">{item.name}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom Profile and Context */}
      <div className="mt-auto px-3 pb-4 space-y-2.5">
        {/* Active Venture Summary Card */}
        <div className="p-3 rounded-2xl bg-[#FFF9F6] border border-[#E8D7D0] space-y-1 shadow-[0_4px_14px_rgba(122,62,70,0.04)]">
          <div className="flex items-center justify-between text-xs">
            <span className="font-serif font-bold text-[#3D2A2D] truncate max-w-[120px]">
              {contextData.venture_name || contextData.business_name || 'Active Venture'}
            </span>
            <span className="text-[10px] font-medium text-[#7A666A] px-2 py-0.5 rounded-full bg-[#F8F2EC] border border-[#E8D7D0]">
              {contextData.selected_locality || 'Hyderabad'}
            </span>
          </div>
          <p className="text-[11px] text-[#7A666A] truncate">
            {contextData.category || 'Specialty Retail'}
          </p>
        </div>

        {/* User Profile & Sign Out */}
        <div className="flex items-center justify-between p-2.5 rounded-2xl bg-[#FFF9F6] border border-[#E8D7D0] shadow-[0_4px_14px_rgba(122,62,70,0.04)]">
          <div className="flex items-center gap-2.5 truncate mr-2">
            <img
              src={profile?.avatar_url || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(profile?.name || 'Venture')}`}
              alt="Profile"
              className="w-8 h-8 rounded-full bg-[#EFC7CD]/40 object-cover border border-[#D98B95] shrink-0"
            />
            <div className="truncate">
              <p className="text-xs font-semibold text-[#3D2A2D] truncate font-serif">
                {profile?.name || user?.email?.split('@')[0] || 'Entrepreneur'}
              </p>
              <p className="text-[10px] text-[#7A666A] truncate">
                {profile?.email || user?.email || 'founder@venturescope.ai'}
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={signOut}
            title="Sign Out"
            className="p-2 rounded-xl text-[#7A666A] hover:text-[#9A3B45] hover:bg-[#FDF0F2] transition-colors shrink-0"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen bg-[#F8F2EC] text-[#3D2A2D] overflow-hidden selection:bg-[#EFC7CD] selection:text-[#7A3E46]">
      {/* Sidebar Desktop */}
      <aside className="hidden md:flex w-[230px] flex-col border-r border-[#E8D7D0] bg-[#F8F2EC]">
        <SidebarContent />
      </aside>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="fixed inset-0 z-50 flex md:hidden">
          <div className="fixed inset-0 bg-[#3D2A2D]/30 backdrop-blur-xs" onClick={() => setMobileOpen(false)} />
          <div className="relative w-[240px] bg-[#F8F2EC] border-r border-[#E8D7D0] shadow-xl">
            <button
              className="absolute top-4 right-3 p-1.5 rounded-full hover:bg-[#EFC7CD]/30 text-[#7A666A]"
              onClick={() => setMobileOpen(false)}
            >
              <X className="w-4 h-4" />
            </button>
            <SidebarContent />
          </div>
        </div>
      )}

      {/* Main App Container */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden bg-[#F8F2EC]">
        <header className="h-16 flex items-center justify-between px-6 border-b border-[#E8D7D0] bg-[#FFF9F6]/80 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <button
              className="md:hidden p-2 rounded-xl border border-[#E8D7D0] hover:bg-[#F8E8EA] text-[#3D2A2D]"
              onClick={() => setMobileOpen(true)}
            >
              <Menu className="w-4 h-4" />
            </button>
            <h1 className="text-base font-serif font-bold text-[#3D2A2D] tracking-tight">{pageTitle}</h1>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              type="button"
              onClick={() => navigate('/setup?edit=true')}
              className="px-3.5 py-1.5 text-xs font-semibold rounded-full border border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#7A3E46] flex items-center gap-1.5 transition-all shadow-xs"
            >
              <Store className="w-3.5 h-3.5 text-[#D98B95]" />
              <span>Edit Setup</span>
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-auto bg-[#F8F2EC]">
          <div className="max-w-6xl mx-auto px-6 py-6">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  )
}
