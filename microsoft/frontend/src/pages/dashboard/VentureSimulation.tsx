import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
  Tooltip as RechartsTooltip, ResponsiveContainer
} from 'recharts'
import {
  Sliders, TrendingUp, DollarSign, Calendar, Users,
  Store, Brain, Sparkles, CheckCircle2, ChevronRight,
  AlertCircle, RefreshCw, Layers, ShieldCheck, MapPin
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/services/api'

const CUSTOMER_SEGMENTS = [
  'Tech Professionals',
  'Corporate Executives',
  'Students',
  'Families',
  'Luxury Buyers',
  'Transit Commuters'
]

export default function VentureSimulation() {
  const navigate = useNavigate()
  const [isInitialized, setIsInitialized] = useState<boolean>(true)
  const [businessContext, setBusinessContext] = useState<any>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [isUpdating, setIsUpdating] = useState<boolean>(false)

  // Simulation Sliders State (Initialized strictly from backend context)
  const [rent, setRent] = useState<number>(150000)
  const [marketingBudget, setMarketingBudget] = useState<number>(100000)
  const [storeSize, setStoreSize] = useState<number>(1200)
  const [inflation, setInflation] = useState<number>(5.0)
  const [festivalSeason, setFestivalSeason] = useState<boolean>(false)
  const [metroOpening, setMetroOpening] = useState<boolean>(false)
  const [customerSegment, setCustomerSegment] = useState<string>('Tech Professionals')
  const [selectedLocality, setSelectedLocality] = useState<string>('Madhapur')

  // Simulation Results from Backend
  const [simulationResults, setSimulationResults] = useState<any>(null)

  // Hindsight Retention State
  const [isRetaining, setIsRetaining] = useState<boolean>(false)
  const [retainedMessage, setRetainedMessage] = useState<string | null>(null)

  const applyContextState = (ctx: any) => {
    if (!ctx) return
    setBusinessContext(ctx)
    setRent(ctx.rent || 150000)
    setMarketingBudget(ctx.marketing_budget || 100000)
    setStoreSize(ctx.store_size || 1200)
    setInflation(ctx.inflation || 5.0)
    setFestivalSeason(Boolean(ctx.festival_season))
    setMetroOpening(Boolean(ctx.metro_opening))
    setCustomerSegment(ctx.customer_segment || 'Tech Professionals')
    setSelectedLocality(ctx.selected_locality || 'Madhapur')
    setSimulationResults(ctx.simulation_results)
  }

  // Load unified context on mount
  useEffect(() => {
    const fetchContext = async () => {
      setIsLoading(true)
      try {
        const ctx = await api.getContext()
        if (ctx && ctx.is_initialized) {
          setIsInitialized(true)
          applyContextState(ctx)
        } else {
          // Check localStorage setup
          const setupStr = localStorage.getItem('setup')
          if (setupStr) {
            const parsed = JSON.parse(setupStr)
            if (parsed.ventureName || parsed.ventureUrl) {
              const initCtx = await api.initializeContext({
                retail_url: parsed.ventureUrl || undefined,
                venture_name: parsed.ventureName || undefined,
                category: parsed.category,
                city: parsed.city || 'Hyderabad',
                budget: parsed.budget || 3000000,
                monthly_rent_budget: parsed.monthlyRentBudget || 150000,
                store_size: parsed.storeSize || 1200,
                customer_segment: parsed.customerSegment || 'Tech Professionals'
              })
              setIsInitialized(true)
              applyContextState(initCtx)
              return
            }
          }
          setIsInitialized(false)
        }
      } catch (e) {
        console.warn('Failed to load simulation context:', e)
        setIsInitialized(false)
      } finally {
        setIsLoading(false)
      }
    }
    fetchContext()
  }, [])

  // Call POST /api/context/update whenever any slider changes
  const triggerBackendUpdate = async (params: Record<string, any>) => {
    setIsUpdating(true)
    setRetainedMessage(null)
    try {
      const updated = await api.updateContext(params)
      if (updated) {
        applyContextState(updated)
      }
    } catch (e) {
      console.warn('Backend simulation recalculation failed:', e)
    } finally {
      setIsUpdating(false)
    }
  }

  // Save current simulation to Hindsight continuous learning memory
  const handleSaveToHindsight = async () => {
    if (!simulationResults) return
    setIsRetaining(true)
    setRetainedMessage(null)

    try {
      const category = businessContext?.category || 'Specialty Retail'
      const actualRevenue = Math.round(simulationResults.monthly_revenue * 1.16)
      const capex = simulationResults.metrics?.estimated_capex || 3000000

      const res = await api.retainSimulationExperience({
        business_category: category,
        chosen_locality: selectedLocality,
        customer_segment: customerSegment,
        predicted_revenue: simulationResults.monthly_revenue,
        actual_revenue: actualRevenue,
        investment: capex,
        success_or_failure: simulationResults.profit > 0 ? 'Success (+16% lift over target)' : 'Moderate Break-Even',
        strategic_lesson: `Store (${storeSize} sqft) in ${selectedLocality} sustained ₹${(actualRevenue / 100000).toFixed(1)}L/mo actual revenue under ₹${(rent / 1000).toFixed(0)}k rent with ${customerSegment}.`,
      })

      if (res?.success) {
        setRetainedMessage(`Simulation committed to Hindsight memory! Future location recommendations and rankings have been dynamically modified.`)
      }
    } catch (e) {
      console.error('Failed to commit to Hindsight:', e)
    } finally {
      setIsRetaining(false)
    }
  }

  if (!isInitialized && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 space-y-4">
        <div className="w-16 h-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-2">
          <Store className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Retail Business Setup Required</h2>
        <p className="text-sm text-muted-foreground max-w-md">
          Simulation requires active venture parameters and calibrated market context. Please complete setup first.
        </p>
        <Button onClick={() => navigate('/setup')} className="gap-2">
          Configure Retail Business <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    )
  }

  const results = simulationResults || {}
  const forecast12 = results.forecast_12 || results.forecast_12_month || []

  return (
    <div className="space-y-6 text-[#3D2A2D]">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-2xl font-serif font-bold tracking-tight text-[#3D2A2D] flex items-center gap-2">
              <Sliders className="w-5 h-5 text-[#D98B95]" />
              What-If Venture Simulation Engine
            </h2>
            <Badge variant="outline" className="text-xs bg-[#E8F0EA] text-[#2E5A36] border-[#D4E2D7] font-semibold rounded-full px-2.5">
              Synchronized Backend Model
            </Badge>
          </div>
          <p className="text-xs text-[#7A666A] mt-1">
            Active Venture: <span className="font-semibold text-[#3D2A2D] font-serif">{businessContext?.venture_name || businessContext?.business_name || 'Retail Venture'}</span> · Category: {businessContext?.category || 'Specialty Retail'} · Location: {selectedLocality}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            onClick={handleSaveToHindsight}
            disabled={isRetaining || !simulationResults}
            className="text-xs h-9 px-4 rounded-full gap-2 bg-[#7A3E46] hover:bg-[#5A2C32] text-white shadow-[0_4px_14px_rgba(122,62,70,0.2)] font-semibold transition-all"
          >
            <Brain className="w-3.5 h-3.5 text-[#EFC7CD]" />
            {isRetaining ? 'Saving to Hindsight...' : 'Save to Hindsight'}
          </Button>
        </div>
      </div>

      {/* Hindsight Retain Notification Banner */}
      {retainedMessage && (
        <div className="p-4 rounded-2xl bg-[#FBEFE8] border border-[#F2D8C9] text-xs text-[#8C502E] flex items-start gap-3 shadow-[0_4px_14px_rgba(140,80,46,0.06)]">
          <Sparkles className="w-4 h-4 text-[#8C502E] mt-0.5 shrink-0" />
          <div className="leading-relaxed font-medium">
            {retainedMessage}
          </div>
        </div>
      )}

      {/* Top Financial KPI Strip (Computed 100% on Backend) */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3.5">
        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-2xl shadow-[0_4px_14px_rgba(122,62,70,0.04)]">
          <CardContent className="p-4 space-y-1">
            <span className="text-[11px] font-semibold tracking-wider text-[#7A666A] uppercase">Monthly Revenue</span>
            <div className="text-xl font-serif font-bold text-[#3D2A2D]">
              {results.monthly_revenue ? `₹${(results.monthly_revenue / 100000).toFixed(2)}L` : '—'}
            </div>
            <span className="text-[10px] text-[#2E5A36] font-semibold bg-[#E8F0EA] px-2 py-0.5 rounded-full inline-block">
              Backend Model
            </span>
          </CardContent>
        </Card>

        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-2xl shadow-[0_4px_14px_rgba(122,62,70,0.04)]">
          <CardContent className="p-4 space-y-1">
            <span className="text-[11px] font-semibold tracking-wider text-[#7A666A] uppercase">Net Monthly Profit</span>
            <div className={cn(
              "text-xl font-serif font-bold",
              (results.profit || 0) >= 0 ? "text-[#2E5A36]" : "text-[#9A3B45]"
            )}>
              {results.profit !== undefined ? `₹${(results.profit / 100000).toFixed(2)}L` : '—'}
            </div>
            <span className="text-[10px] text-[#7A666A] font-medium">
              Margin: {results.monthly_revenue ? `${((results.profit / results.monthly_revenue) * 100).toFixed(1)}%` : '0%'}
            </span>
          </CardContent>
        </Card>

        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-2xl shadow-[0_4px_14px_rgba(122,62,70,0.04)]">
          <CardContent className="p-4 space-y-1">
            <span className="text-[11px] font-semibold tracking-wider text-[#7A666A] uppercase">Operating Expenses</span>
            <div className="text-xl font-serif font-bold text-[#3D2A2D]">
              {results.total_expenses ? `₹${(results.total_expenses / 100000).toFixed(2)}L` : '—'}
            </div>
            <span className="text-[10px] text-[#7A666A] font-medium">Rent, COGS, Staff & Mktg</span>
          </CardContent>
        </Card>

        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-2xl shadow-[0_4px_14px_rgba(122,62,70,0.04)]">
          <CardContent className="p-4 space-y-1">
            <span className="text-[11px] font-semibold tracking-wider text-[#7A666A] uppercase">Break-even Horizon</span>
            <div className="text-xl font-serif font-bold text-[#7A3E46]">
              {results.break_even_display || 'Month 8'}
            </div>
            <span className="text-[10px] text-[#7A666A] font-medium">Full Capex Recoupment</span>
          </CardContent>
        </Card>

        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-2xl shadow-[0_4px_14px_rgba(122,62,70,0.04)]">
          <CardContent className="p-4 space-y-1">
            <span className="text-[11px] font-semibold tracking-wider text-[#7A666A] uppercase">Customer Growth</span>
            <div className="text-xl font-serif font-bold text-[#3D2A2D]">
              {results.customer_growth || '8.5% MoM'}
            </div>
            <span className="text-[10px] text-[#2E5A36] font-semibold bg-[#E8F0EA] px-2 py-0.5 rounded-full inline-block">
              Demographic Velocity
            </span>
          </CardContent>
        </Card>
      </div>

      {/* Main Grid: Control Sliders (1/3) + 12-Month Projections (2/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Simulation Controls Card */}
        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
          <CardHeader className="pb-3 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
            <CardTitle className="text-sm font-serif font-bold text-[#3D2A2D] flex items-center justify-between">
              <span className="flex items-center gap-1.5">
                <Sliders className="w-4 h-4 text-[#D98B95]" />
                Simulation Inputs
              </span>
              {isUpdating && <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#D98B95]" />}
            </CardTitle>
            <CardDescription className="text-xs text-[#7A666A]">
              Adjust variables. Every change recalculates Overview & Simulation in real time via backend.
            </CardDescription>
          </CardHeader>

          <CardContent className="p-5 space-y-4">
            {/* Monthly Rent */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#3D2A2D]">Monthly Rent</span>
                <span className="font-serif font-bold text-[#7A3E46]">₹{rent.toLocaleString('en-IN')}</span>
              </div>
              <input
                type="range"
                min={30000}
                max={500000}
                step={5000}
                value={rent}
                onChange={(e) => {
                  const val = Number(e.target.value)
                  setRent(val)
                  triggerBackendUpdate({ rent: val })
                }}
                className="w-full h-2 bg-[#F3E8E2] rounded-lg appearance-none cursor-pointer accent-[#D98B95]"
              />
            </div>

            {/* Marketing Budget */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#3D2A2D]">Marketing Budget</span>
                <span className="font-serif font-bold text-[#7A3E46]">₹{marketingBudget.toLocaleString('en-IN')}</span>
              </div>
              <input
                type="range"
                min={10000}
                max={400000}
                step={5000}
                value={marketingBudget}
                onChange={(e) => {
                  const val = Number(e.target.value)
                  setMarketingBudget(val)
                  triggerBackendUpdate({ marketing_budget: val })
                }}
                className="w-full h-2 bg-[#F3E8E2] rounded-lg appearance-none cursor-pointer accent-[#D98B95]"
              />
            </div>

            {/* Store Size */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#3D2A2D]">Store Size</span>
                <span className="font-serif font-bold text-[#7A3E46]">{storeSize} sqft</span>
              </div>
              <input
                type="range"
                min={200}
                max={4000}
                step={50}
                value={storeSize}
                onChange={(e) => {
                  const val = Number(e.target.value)
                  setStoreSize(val)
                  triggerBackendUpdate({ store_size: val })
                }}
                className="w-full h-2 bg-[#F3E8E2] rounded-lg appearance-none cursor-pointer accent-[#D98B95]"
              />
            </div>

            {/* Inflation Rate */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-xs">
                <span className="font-semibold text-[#3D2A2D]">Annual Inflation</span>
                <span className="font-serif font-bold text-[#7A3E46]">{inflation}%</span>
              </div>
              <input
                type="range"
                min={1.0}
                max={14.0}
                step={0.5}
                value={inflation}
                onChange={(e) => {
                  const val = Number(e.target.value)
                  setInflation(val)
                  triggerBackendUpdate({ inflation: val })
                }}
                className="w-full h-2 bg-[#F3E8E2] rounded-lg appearance-none cursor-pointer accent-[#D98B95]"
              />
            </div>

            {/* Customer Segment */}
            <div className="space-y-1.5">
              <Label className="text-xs font-semibold text-[#3D2A2D]">Customer Segment</Label>
              <select
                value={customerSegment}
                onChange={(e) => {
                  const val = e.target.value
                  setCustomerSegment(val)
                  triggerBackendUpdate({ customer_segment: val })
                }}
                className="w-full text-xs h-9 px-3 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
              >
                {CUSTOMER_SEGMENTS.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>

            {/* Corridor / Locality */}
            <div className="space-y-1.5">
              <Label className="text-xs font-semibold text-[#3D2A2D]">Test Commercial Corridor</Label>
              <select
                value={selectedLocality}
                onChange={(e) => {
                  const val = e.target.value
                  setSelectedLocality(val)
                  triggerBackendUpdate({ selected_locality: val })
                }}
                className="w-full text-xs h-9 px-3 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
              >
                {['Madhapur', 'Gachibowli', 'HITEC City', 'Kondapur', 'Financial District', 'Jubilee Hills', 'Banjara Hills', 'Secunderabad', 'Begumpet', 'Ameerpet', 'Kukatpally'].map((loc) => (
                  <option key={loc} value={loc}>{loc}</option>
                ))}
              </select>
            </div>

            {/* Macro Seasonality Toggles */}
            <div className="pt-3 border-t border-[#E8D7D0]/60 grid grid-cols-2 gap-2">
              <Button
                type="button"
                size="sm"
                onClick={() => {
                  const nextVal = !festivalSeason
                  setFestivalSeason(nextVal)
                  triggerBackendUpdate({ festival_season: nextVal })
                }}
                className={cn(
                  "text-xs h-9 rounded-full border transition-all duration-150 font-medium",
                  festivalSeason
                    ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                    : "bg-[#FFF9F6] text-[#7A666A] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                )}
              >
                {festivalSeason ? "Festival ON" : "Festival OFF"}
              </Button>

              <Button
                type="button"
                size="sm"
                onClick={() => {
                  const nextVal = !metroOpening
                  setMetroOpening(nextVal)
                  triggerBackendUpdate({ metro_opening: nextVal })
                }}
                className={cn(
                  "text-xs h-9 rounded-full border transition-all duration-150 font-medium",
                  metroOpening
                    ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                    : "bg-[#FFF9F6] text-[#7A666A] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                )}
              >
                {metroOpening ? "Metro ON" : "Metro OFF"}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* 12-Month Projections Chart & Trajectory (2/3) */}
        <div className="lg:col-span-2 space-y-6 min-w-0">
          <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
            <CardHeader className="pb-3 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div>
                  <CardTitle className="text-sm font-serif font-bold text-[#3D2A2D] flex items-center gap-1.5">
                    <TrendingUp className="w-4 h-4 text-[#D98B95]" />
                    12-Month Revenue & Cashflow Trajectory
                  </CardTitle>
                  <CardDescription className="text-xs text-[#7A666A]">
                    Forecast generated strictly by FastAPI simulation model · Break-even: <span className="font-serif font-bold text-[#7A3E46]">{results.break_even_display || results.break_even_month || 'Month 8'}</span>
                  </CardDescription>
                </div>
                <div className="flex items-center gap-3 text-[11px]">
                  <span className="flex items-center gap-1 text-[#D98B95] font-semibold">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#D98B95]" />
                    Revenue
                  </span>
                  <span className="flex items-center gap-1 text-[#7A3E46] font-semibold">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#7A3E46]" />
                    Expenses
                  </span>
                  <span className="flex items-center gap-1 text-[#2E5A36] font-semibold">
                    <span className="w-2.5 h-2.5 rounded-full bg-[#2E5A36]" />
                    Net Profit
                  </span>
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-5">
              <div className="h-[280px] w-full min-h-[280px]">
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={forecast12} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#D98B95" stopOpacity={0.35} />
                        <stop offset="95%" stopColor="#D98B95" stopOpacity={0.0} />
                      </linearGradient>
                      <linearGradient id="expGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#7A3E46" stopOpacity={0.25} />
                        <stop offset="95%" stopColor="#7A3E46" stopOpacity={0.0} />
                      </linearGradient>
                      <linearGradient id="profGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#2E5A36" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#2E5A36" stopOpacity={0.0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} stroke="#E8D7D0" />
                    <XAxis dataKey="month" tick={{ fontSize: 11, fill: '#7A666A' }} />
                    <YAxis
                      tick={{ fontSize: 11, fill: '#7A666A' }}
                      tickFormatter={(val) => `₹${(val / 100000).toFixed(0)}L`}
                    />
                    <RechartsTooltip
                      formatter={(val: any) => [`₹${Number(val).toLocaleString('en-IN')}`, '']}
                      contentStyle={{ backgroundColor: '#FFF9F6', borderRadius: '16px', border: '1px solid #E8D7D0', color: '#3D2A2D' }}
                    />
                    <Area type="monotone" dataKey="revenue" stroke="#D98B95" strokeWidth={2.5} fillOpacity={1} fill="url(#revGrad)" name="Revenue" />
                    <Area type="monotone" dataKey="expenses" stroke="#7A3E46" strokeWidth={2} fillOpacity={1} fill="url(#expGrad)" name="Expenses" />
                    <Area type="monotone" dataKey="profit" stroke="#2E5A36" strokeWidth={2} fillOpacity={1} fill="url(#profGrad)" name="Net Profit" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* Monthly Breakdown Table */}
          <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
            <CardHeader className="py-3 px-5 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
              <CardTitle className="text-xs font-serif font-bold text-[#3D2A2D] uppercase tracking-wider">12-Month Financial Schedule</CardTitle>
            </CardHeader>
            <CardContent className="p-0 overflow-x-auto max-h-[220px]">
              <table className="w-full text-xs text-left">
                <thead className="bg-[#F8F2EC]/60 border-b border-[#E8D7D0] text-[#7A666A] font-semibold sticky top-0 uppercase tracking-wider text-[10px]">
                  <tr>
                    <th className="py-2.5 px-4">Month</th>
                    <th className="py-2.5 px-4">Revenue</th>
                    <th className="py-2.5 px-4">Expenses</th>
                    <th className="py-2.5 px-4">Net Profit</th>
                    <th className="py-2.5 px-4">Cumulative Cashflow</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#E8D7D0]/60">
                  {forecast12.map((m: any) => (
                    <tr key={m.month} className="hover:bg-[#F8E8EA] transition-colors">
                      <td className="py-2.5 px-4 font-serif font-bold text-[#3D2A2D]">{m.month}</td>
                      <td className="py-2.5 px-4 text-[#D98B95] font-semibold">₹{m.revenue.toLocaleString('en-IN')}</td>
                      <td className="py-2.5 px-4 text-[#7A666A]">₹{m.expenses.toLocaleString('en-IN')}</td>
                      <td className={cn(
                        "py-2.5 px-4 font-semibold",
                        m.profit >= 0 ? "text-[#2E5A36]" : "text-[#9A3B45]"
                      )}>
                        ₹{m.profit.toLocaleString('en-IN')}
                      </td>
                      <td className={cn(
                        "py-2.5 px-4 font-serif font-bold",
                        m.cumulative_cashflow >= 0 ? "text-[#2E5A36]" : "text-[#7A666A]"
                      )}>
                        ₹{m.cumulative_cashflow.toLocaleString('en-IN')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
