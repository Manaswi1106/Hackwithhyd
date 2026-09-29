import React, { createContext, useContext, useEffect, useState } from 'react'
import { supabase, isSupabaseConfigured } from '@/lib/supabase'
import type { Session, User } from '@supabase/supabase-js'

export interface UserProfile {
  id: string
  name: string
  email: string
  avatar_url?: string
}

interface AuthContextType {
  user: User | null
  profile: UserProfile | null
  session: Session | null
  isLoading: boolean
  signInWithGoogle: () => Promise<void>
  signInWithAccount: (email: string, name?: string) => Promise<void>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const LOCAL_STORAGE_SESSION_KEY = 'venturescope_auth_session'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [session, setSession] = useState<Session | null>(null)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  const extractProfile = (u: User | null): UserProfile | null => {
    if (!u) return null
    const meta = u.user_metadata || {}
    const name = meta.full_name || meta.name || u.email?.split('@')[0] || 'Venture Founder'
    const email = u.email || ''
    const avatar = meta.avatar_url || meta.picture || `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(name)}`
    return {
      id: u.id,
      name,
      email,
      avatar_url: avatar
    }
  }

  useEffect(() => {
    let mounted = true

    const initAuth = async () => {
      try {
        const isOAuthCallback = window.location.hash.includes('access_token') || window.location.search.includes('code')
        const isOnLoginPage = window.location.pathname === '/login'

        if (isSupabaseConfigured) {
          // 1. Check active Supabase session
          const { data: { session: currentSession } } = await supabase.auth.getSession()
          if (mounted && currentSession) {
            // If on /login without an active OAuth callback, do not auto-login with existing session
            if (isOnLoginPage && !isOAuthCallback) {
              setIsLoading(false)
              return
            }
            setSession(currentSession)
            setUser(currentSession.user)
            setProfile(extractProfile(currentSession.user))
            setIsLoading(false)
            return
          }
        }

        // 2. Check local fallback session (only if NOT on login page)
        if (!isOnLoginPage || isOAuthCallback) {
          const rawLocal = localStorage.getItem(LOCAL_STORAGE_SESSION_KEY)
          if (rawLocal) {
            try {
              const parsed = JSON.parse(rawLocal)
              if (mounted && parsed.user) {
                setUser(parsed.user as User)
                setProfile(parsed.profile)
                setSession(parsed.session || null)
                setIsLoading(false)
                return
              }
            } catch {}
          }
        }
      } catch (err) {
        console.warn('Auth restoration error:', err)
      } finally {
        if (mounted) setIsLoading(false)
      }
    }

    initAuth()

    // Listen to Supabase auth state transitions
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, newSession) => {
      if (!mounted) return
      if (newSession?.user) {
        setSession(newSession)
        setUser(newSession.user)
        const prof = extractProfile(newSession.user)
        setProfile(prof)
        localStorage.setItem(LOCAL_STORAGE_SESSION_KEY, JSON.stringify({
          user: newSession.user,
          profile: prof,
          session: newSession
        }))
      } else if (event === 'SIGNED_OUT') {
        setUser(null)
        setSession(null)
        setProfile(null)
        localStorage.removeItem(LOCAL_STORAGE_SESSION_KEY)
      }
      setIsLoading(false)
    })

    return () => {
      mounted = false
      subscription.unsubscribe()
    }
  }, [])

  const signInWithGoogle = async () => {
    setIsLoading(true)
    try {
      if (isSupabaseConfigured) {
        const { error } = await supabase.auth.signInWithOAuth({
          provider: 'google',
          options: {
            redirectTo: `${window.location.origin}/setup`,
            queryParams: {
              prompt: 'select_account',
              access_type: 'offline',
            },
          },
        })
        if (error) throw error
      }
    } finally {
      setIsLoading(false)
    }
  }

  const signInWithAccount = async (email: string, name?: string) => {
    setIsLoading(true)
    try {
      const safeName = name || email.split('@')[0] || 'Venture Founder'
      const simulatedUser: any = {
        id: `usr_${email.replace(/[^a-zA-Z0-9]/g, '_')}`,
        email,
        app_metadata: { provider: 'google' },
        user_metadata: {
          full_name: safeName,
          name: safeName,
          avatar_url: `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(safeName)}`
        },
        created_at: new Date().toISOString()
      }
      const prof = extractProfile(simulatedUser)
      setUser(simulatedUser)
      setProfile(prof)
      localStorage.setItem(LOCAL_STORAGE_SESSION_KEY, JSON.stringify({
        user: simulatedUser,
        profile: prof,
        session: null
      }))
      // Force setup completion flag to false for fresh login
      localStorage.removeItem('venturescope_setup_completed')
    } finally {
      setIsLoading(false)
    }
  }

  const signOut = async () => {
    try {
      if (isSupabaseConfigured) {
        await supabase.auth.signOut({ scope: 'global' })
      }
    } catch (e) {
      console.warn('SignOut error:', e)
    } finally {
      setUser(null)
      setSession(null)
      setProfile(null)
      localStorage.removeItem(LOCAL_STORAGE_SESSION_KEY)
      localStorage.removeItem('venturescope_user')
      sessionStorage.clear()
      // Clear cached context
      try {
        await fetch('/api/context/reset', { method: 'POST' })
      } catch {}
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        session,
        isLoading,
        signInWithGoogle,
        signInWithAccount,
        signOut,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
