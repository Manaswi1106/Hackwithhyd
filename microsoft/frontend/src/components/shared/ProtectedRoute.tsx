import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/context/AuthContext'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  children?: React.ReactNode
  requireSetupCompleted?: boolean
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem('venturescope_auth_session')
    if (!raw) return null
    const parsed = JSON.parse(raw)
    return parsed.profile || parsed.user || null
  } catch {
    return null
  }
}

export default function ProtectedRoute({ children, requireSetupCompleted = false }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-2 text-xs text-muted-foreground">
          <Loader2 className="w-5 h-5 animate-spin text-primary" />
          <span>Restoring verified session...</span>
        </div>
      </div>
    )
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  // Routing requirement: setup_completed = false -> always open /setup
  if (requireSetupCompleted) {
    const setupCompleted = localStorage.getItem('venturescope_setup_completed') === 'true'
    if (!setupCompleted) {
      return <Navigate to="/setup" replace />
    }
  }

  return children ? <>{children}</> : null
}
