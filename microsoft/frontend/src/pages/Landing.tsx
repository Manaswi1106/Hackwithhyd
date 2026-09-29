import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { ArrowRight } from 'lucide-react'

export default function Landing() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="h-14 flex items-center justify-between px-6 md:px-12 border-b border-border">
        <span className="text-[15px] font-semibold tracking-tight">VentureScope</span>
        <Button variant="ghost" size="sm" onClick={() => navigate('/login')}>
          Sign in
        </Button>
      </header>

      <main className="flex-1 flex items-center justify-center px-6">
        <div className="max-w-2xl text-center space-y-6">
          <h1 className="text-4xl md:text-5xl font-semibold tracking-tight leading-[1.1] text-foreground">
            Understand the market.
            <br />
            Then simulate entering it.
          </h1>
          <p className="text-lg text-muted-foreground max-w-lg mx-auto leading-relaxed">
            Evidence-grounded market intelligence and venture simulation
            for investors, founders, and strategy teams.
          </p>
          <div className="pt-2">
            <Button size="lg" className="h-11 px-6" onClick={() => navigate('/setup')}>
              Get started
              <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </div>
        </div>
      </main>

      <footer className="h-14 flex items-center justify-center border-t border-border">
        <p className="text-xs text-muted-foreground">
          VentureScope · Venture Intelligence Platform
        </p>
      </footer>
    </div>
  )
}
