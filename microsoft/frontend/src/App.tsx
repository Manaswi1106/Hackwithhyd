import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { TooltipProvider } from '@/components/ui/tooltip'
import { AuthProvider, useAuth } from '@/context/AuthContext'
import Login from '@/pages/Login'
import Setup from '@/pages/Setup'
import DashboardLayout from '@/pages/DashboardLayout'
import MarketOverview from '@/pages/dashboard/MarketOverview'
import VentureSimulation from '@/pages/dashboard/VentureSimulation'
import MemoryTimeline from '@/pages/dashboard/MemoryTimeline'
import CompetitorIntelligence from '@/pages/dashboard/CompetitorIntelligence'
import Settings from '@/pages/dashboard/Settings'
import ProtectedRoute from '@/components/shared/ProtectedRoute'
import { Loader2 } from 'lucide-react'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5 * 60 * 1000, retry: 1 },
  },
})

// Root gateway directing to Login, Setup or Dashboard based on session & setup_completed
function RootGateway() {
  const { user, isLoading } = useAuth()
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-5 h-5 animate-spin text-primary" />
      </div>
    )
  }
  if (!user) {
    return <Navigate to="/login" replace />
  }
  const setupCompleted = localStorage.getItem('venturescope_setup_completed') === 'true'
  if (!setupCompleted) {
    return <Navigate to="/setup" replace />
  }
  return <Navigate to="/dashboard/overview" replace />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              {/* Mandatory Sign In First */}
              <Route path="/" element={<RootGateway />} />
              <Route path="/login" element={<Login />} />

              {/* Protected Setup Flow */}
              <Route
                path="/setup"
                element={
                  <ProtectedRoute requireSetupCompleted={false}>
                    <Setup />
                  </ProtectedRoute>
                }
              />

              {/* Protected Dashboard Pages: Overview, Simulation, Competitors, Memory, Settings */}
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute requireSetupCompleted={true}>
                    <DashboardLayout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Navigate to="overview" replace />} />
                <Route path="overview" element={<MarketOverview />} />
                <Route path="simulation" element={<VentureSimulation />} />
                <Route path="competitors" element={<CompetitorIntelligence />} />
                <Route path="memory" element={<MemoryTimeline />} />
                <Route path="settings" element={<Settings />} />
              </Route>

              {/* Catch-all redirect */}
              <Route path="*" element={<Navigate to="/login" replace />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </TooltipProvider>
    </QueryClientProvider>
  )
}
