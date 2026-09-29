import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Compass, ShieldCheck, Loader2, AlertCircle, User, PlusCircle, X } from 'lucide-react'
import { useAuth } from '@/context/AuthContext'
import { isSupabaseConfigured } from '@/lib/supabase'

export default function Login() {
  const navigate = useNavigate()
  const { user, signInWithGoogle, signInWithAccount, isLoading: authLoading } = useAuth()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Interactive Google Account Chooser state
  const [showAccountChooser, setShowAccountChooser] = useState(false)
  const [customEmail, setCustomEmail] = useState('')
  const [showCustomInput, setShowCustomInput] = useState(false)

  // Once authenticated via OAuth redirect callback, always navigate to /setup (never skip onboarding)
  useEffect(() => {
    const isOAuthCallback = window.location.hash.includes('access_token') || window.location.search.includes('code')
    if (user && !authLoading && isOAuthCallback) {
      // Clear setup_completed so fresh sign in always opens /setup first
      localStorage.removeItem('venturescope_setup_completed')
      navigate('/setup', { replace: true })
    }
  }, [user, authLoading, navigate])

  const handleContinueWithGoogleClick = async () => {
    setErrorMessage(null)
    if (isSupabaseConfigured) {
      setIsSubmitting(true)
      try {
        await signInWithGoogle()
      } catch (err: any) {
        console.error('Google Sign In error:', err)
        setErrorMessage(err.message || 'Google Sign In failed. Please try again.')
        setIsSubmitting(false)
      }
    } else {
      // Always show Google Account Chooser modal
      setShowAccountChooser(true)
    }
  }

  const handleSelectAccount = async (email: string, name?: string) => {
    setIsSubmitting(true)
    setErrorMessage(null)
    try {
      await signInWithAccount(email, name)
      setShowAccountChooser(false)
      // Routing requirement: Login -> Setup -> Overview
      localStorage.removeItem('venturescope_setup_completed')
      navigate('/setup', { replace: true })
    } catch (err: any) {
      console.error('Account selection error:', err)
      setErrorMessage(err.message || 'Failed to sign in with account.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleCustomEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!customEmail.trim() || !customEmail.includes('@')) {
      setErrorMessage('Please enter a valid Gmail or email address.')
      return
    }
    const derivedName = customEmail.split('@')[0].replace(/[._-]/g, ' ')
    handleSelectAccount(customEmail.trim(), derivedName)
  }

  return (
    <div className="min-h-screen bg-[#F8F2EC] text-[#3D2A2D] flex flex-col justify-between relative overflow-hidden selection:bg-[#EFC7CD] selection:text-[#7A3E46]">
      {/* Decorative luxury blush ambient background orbs */}
      <div className="absolute -top-24 -left-24 w-96 h-96 rounded-full bg-[#EFC7CD]/35 blur-3xl pointer-events-none" />
      <div className="absolute top-1/3 -right-28 w-80 h-80 rounded-full bg-[#D98B95]/20 blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 left-1/4 w-96 h-96 rounded-full bg-[#E8D7D0]/50 blur-3xl pointer-events-none" />

      {/* Header */}
      <header className="h-16 flex items-center justify-between px-6 md:px-12 border-b border-[#E8D7D0] bg-[#FFF9F6]/80 backdrop-blur-md relative z-10">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-2xl bg-[#EFC7CD]/40 border border-[#D98B95]/30 flex items-center justify-center text-[#7A3E46] shadow-[0_4px_12px_rgba(122,62,70,0.08)]">
            <Compass className="w-5 h-5 text-[#7A3E46]" />
          </div>
          <div className="flex flex-col">
            <span className="text-base font-serif font-bold tracking-tight text-[#3D2A2D]">
              VentureScope
            </span>
            <span className="text-[10px] tracking-widest uppercase font-medium text-[#7A666A]">
              Location Intelligence
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#E8F0EA] border border-[#D4E2D7] text-xs text-[#2E5A36] font-medium">
          <ShieldCheck className="w-3.5 h-3.5 text-[#2E5A36]" />
          <span className="text-[11px]">Google OAuth Protected</span>
        </div>
      </header>

      {/* Main Login Card */}
      <main className="flex-1 flex items-center justify-center px-4 py-12 relative z-10">
        <div className="w-full max-w-md space-y-6">
          <div className="text-center space-y-2 mb-2">
            <span className="inline-block px-3 py-1 rounded-full bg-[#F5E8F8] border border-[#E8D1ED] text-[11px] font-semibold tracking-wider text-[#7A3E8C] uppercase">
              Curated Retail Architecture
            </span>
            <h1 className="text-3xl font-serif font-bold text-[#3D2A2D] tracking-tight">
              Welcome to VentureScope
            </h1>
            <p className="text-xs text-[#7A666A] max-w-xs mx-auto leading-relaxed">
              Empirical AI location intelligence, footfall modeling, and what-if simulation for ambitious retail founders.
            </p>
          </div>

          <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_16px_40px_rgba(122,62,70,0.07)] overflow-hidden">
            <CardHeader className="text-center space-y-2 pb-4 pt-8">
              <div className="mx-auto w-14 h-14 rounded-2xl bg-gradient-to-tr from-[#EFC7CD] to-[#FFF9F6] border border-[#D98B95]/40 flex items-center justify-center text-[#7A3E46] shadow-[0_8px_20px_rgba(217,139,149,0.2)] mb-1">
                <Compass className="w-7 h-7 text-[#7A3E46]" />
              </div>
              <CardTitle className="text-xl font-serif font-bold text-[#3D2A2D]">
                Founder Sign In
              </CardTitle>
              <CardDescription className="text-xs text-[#7A666A]">
                Sign in with your verified Google account to enter your venture workspace
              </CardDescription>
            </CardHeader>

            <CardContent className="space-y-4 px-6 pb-8">
              {errorMessage && (
                <div className="p-3.5 rounded-2xl bg-[#FDF0F2] border border-[#F5C2C7] text-[#9A3B45] text-xs flex items-center gap-2.5">
                  <AlertCircle className="w-4 h-4 shrink-0 text-[#9A3B45]" />
                  <span className="font-medium">{errorMessage}</span>
                </div>
              )}

              {/* Google Sign In button */}
              <Button
                type="button"
                onClick={handleContinueWithGoogleClick}
                disabled={isSubmitting || authLoading}
                className="w-full h-12 rounded-[18px] border border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#3D2A2D] font-medium text-xs flex items-center justify-center gap-3 transition-all duration-200 shadow-[0_4px_14px_rgba(122,62,70,0.05)] hover:border-[#D98B95] active:scale-[0.99]"
              >
                {isSubmitting || authLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin text-[#7A3E46]" />
                ) : (
                  <svg className="w-4 h-4 shrink-0" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                    />
                  </svg>
                )}
                <span className="font-semibold tracking-wide">Continue with Google</span>
              </Button>

              <div className="pt-2 text-center">
                <span className="text-[11px] text-[#7A666A] leading-relaxed">
                  Interactive Google Account Chooser is enabled. Always presents account selection before navigating to onboarding.
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Google Account Chooser Modal Dialog */}
      {showAccountChooser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#3D2A2D]/40 backdrop-blur-sm p-4">
          <div className="bg-[#FFF9F6] border border-[#E8D7D0] w-full max-w-sm rounded-[24px] shadow-[0_24px_50px_rgba(122,62,70,0.15)] overflow-hidden animate-in fade-in zoom-in-95 duration-150">
            {/* Google Header */}
            <div className="p-5 pb-3 border-b border-[#E8D7D0] flex items-start justify-between bg-[#F8F2EC]/50">
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24">
                    <path
                      fill="#4285F4"
                      d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    />
                    <path
                      fill="#34A853"
                      d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    />
                    <path
                      fill="#FBBC05"
                      d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                    />
                    <path
                      fill="#EA4335"
                      d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                    />
                  </svg>
                  <span className="font-semibold text-xs text-[#3D2A2D]">Sign in with Google</span>
                </div>
                <h3 className="text-base font-serif font-bold text-[#3D2A2D]">Choose an account</h3>
                <p className="text-xs text-[#7A666A]">to continue to VentureScope</p>
              </div>
              <button
                type="button"
                onClick={() => setShowAccountChooser(false)}
                className="text-[#7A666A] hover:text-[#3D2A2D] p-1.5 rounded-full hover:bg-[#EFC7CD]/30 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Account Options List */}
            <div className="p-3 space-y-1.5 divide-y divide-[#E8D7D0]/60">
              {/* Account 1 */}
              <button
                type="button"
                onClick={() => handleSelectAccount('gvnse@gmail.com', 'GVN Sekhar')}
                className="w-full p-3 rounded-2xl hover:bg-[#F8E8EA] transition-all flex items-center gap-3 text-left"
              >
                <div className="w-9 h-9 rounded-full bg-[#EFC7CD] text-[#7A3E46] font-serif font-bold flex items-center justify-center text-sm border border-[#D98B95]/40 shrink-0">
                  G
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold text-[#3D2A2D] truncate">GVN Sekhar</div>
                  <div className="text-[11px] text-[#7A666A] truncate">gvnse@gmail.com</div>
                </div>
              </button>

              {/* Account 2 */}
              <button
                type="button"
                onClick={() => handleSelectAccount('founder@venturescope.ai', 'Venture Founder')}
                className="w-full p-3 rounded-2xl hover:bg-[#F8E8EA] transition-all flex items-center gap-3 text-left pt-3"
              >
                <div className="w-9 h-9 rounded-full bg-[#F5E8F8] text-[#7A3E8C] font-serif font-bold flex items-center justify-center text-sm border border-[#E8D1ED] shrink-0">
                  V
                </div>
                <div className="min-w-0 flex-1">
                  <div className="text-xs font-semibold text-[#3D2A2D] truncate">Venture Founder</div>
                  <div className="text-[11px] text-[#7A666A] truncate">founder@venturescope.ai</div>
                </div>
              </button>

              {/* Use Another Account */}
              {!showCustomInput ? (
                <button
                  type="button"
                  onClick={() => setShowCustomInput(true)}
                  className="w-full p-3 rounded-2xl hover:bg-[#F8E8EA] transition-all flex items-center gap-3 text-left pt-3 text-[#7A3E46] text-xs font-semibold"
                >
                  <PlusCircle className="w-4 h-4 shrink-0 text-[#D98B95]" />
                  <span>Use another account</span>
                </button>
              ) : (
                <form onSubmit={handleCustomEmailSubmit} className="p-3 space-y-2 pt-3">
                  <label htmlFor="gmailInput" className="text-[11px] font-semibold text-[#7A666A] block">
                    Enter your Gmail address:
                  </label>
                  <div className="flex gap-2">
                    <Input
                      id="gmailInput"
                      type="email"
                      value={customEmail}
                      onChange={(e) => setCustomEmail(e.target.value)}
                      placeholder="yourname@gmail.com"
                      className="text-xs h-9 rounded-xl border-[#E8D7D0] bg-[#FFF9F6] flex-1 text-[#3D2A2D]"
                      autoFocus
                    />
                    <Button type="submit" size="sm" className="text-xs h-9 px-4 rounded-xl bg-[#D98B95] hover:bg-[#7A3E46] text-white">
                      Sign in
                    </Button>
                  </div>
                </form>
              )}
            </div>

            <div className="p-3.5 bg-[#F8F2EC]/60 border-t border-[#E8D7D0] text-center">
              <span className="text-[10px] text-[#7A666A]">
                To continue, Google will share your name, email address, and profile picture with VentureScope.
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="py-4 border-t border-[#E8D7D0] text-center text-xs text-[#7A666A] bg-[#FFF9F6]/50">
        © 2026 VentureScope · AI-Powered Retail Location Intelligence.
      </footer>
    </div>
  )
}
