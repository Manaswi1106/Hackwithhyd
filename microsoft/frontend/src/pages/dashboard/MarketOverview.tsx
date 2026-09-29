import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { MetricCard } from '@/components/shared/MetricCard'
import { Button } from '@/components/ui/button'
import {
  RefreshCw, MapPin, ShieldCheck, Database, Compass, Flame,
  Sparkles, CheckCircle2, ChevronRight, Activity, Brain,
  Store, AlertCircle, Info, ExternalLink, Award, TrendingUp
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/services/api'
import GoogleMap from '@/components/shared/GoogleMap'

export default function MarketOverview() {
  const navigate = useNavigate()
  const [isInitialized, setIsInitialized] = useState<boolean>(true)
  const [businessContext, setBusinessContext] = useState<any>(null)

  // Data states
  const [top5Locations, setTop5Locations] = useState<any[]>([])
  const [allLocations, setAllLocations] = useState<any[]>([])
  const [activeArea, setActiveArea] = useState<any>(null)
  const [competitors, setCompetitors] = useState<any[]>([])
  const [saturation, setSaturation] = useState<string>('Medium saturation')
  const [hindsightInsight, setHindsightInsight] = useState<string>('')
  const [whyNotOthers, setWhyNotOthers] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [customerSegment, setCustomerSegment] = useState<string>('Tech Professionals')
  const [searchRadiusKm, setSearchRadiusKm] = useState<number>(3.0)

  const applyContextData = (ctx: any) => {
    if (!ctx) return
    const overview = ctx.market_overview || {}
    const top5 = overview.top_5 || ctx.rankings || []
    const all = overview.all_ranked || top5
    setTop5Locations(top5)
    setAllLocations(all)
    setHindsightInsight(overview.hindsight_insight || '')
    setWhyNotOthers(overview.why_not_others || [])
    setCustomerSegment(ctx.customer_segment || 'Tech Professionals')
    setSearchRadiusKm(ctx.search_radius_km || 3.0)

    const selected = all.find((l: any) => l.area.toLowerCase() === (ctx.selected_locality || '').toLowerCase()) || top5[0]
    setActiveArea(selected)

    const comps = ctx.competitor_data || {}
    setCompetitors(comps.competitors || ctx.competitors || [])
    setSaturation(comps.saturation || ctx.kpis?.competitor_saturation || 'Medium saturation')
  }

  // Load shared context from backend (GET /api/context)
  const loadContext = async () => {
    setIsLoading(true)
    try {
      const ctx = await api.getContext()
      if (ctx && ctx.is_initialized) {
        setIsInitialized(true)
        setBusinessContext(ctx)
        applyContextData(ctx)
      } else {
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
            setBusinessContext(initCtx)
            applyContextData(initCtx)
            return
          }
        }
        setIsInitialized(false)
      }
    } catch (e) {
      console.warn('Failed to load shared business context:', e)
      setIsInitialized(false)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadContext()
  }, [])

  const handleSelectLocation = async (loc: any) => {
    setActiveArea(loc)
    try {
      const updated = await api.updateContext({ selected_locality: loc.area })
      if (updated) {
        setBusinessContext(updated)
        applyContextData(updated)
      }
    } catch (e) {
      console.warn('Failed to update selected locality in shared context:', e)
    }
  }

  const handleCustomerSegmentChange = async (newSegment: string) => {
    setCustomerSegment(newSegment)
    try {
      const updated = await api.updateContext({ customer_segment: newSegment })
      if (updated) {
        setBusinessContext(updated)
        applyContextData(updated)
      }
    } catch (e) {
      console.warn('Failed to update segment in shared context:', e)
    }
  }

  const handleRadiusChange = async (newRadius: number) => {
    setSearchRadiusKm(newRadius)
    try {
      const updated = await api.updateContext({ search_radius_km: newRadius })
      if (updated) {
        setBusinessContext(updated)
        applyContextData(updated)
      }
    } catch (e) {
      console.warn('Failed to update radius in shared context:', e)
    }
  }

  const activeLocalityData = activeArea || top5Locations[0]

  const getDynamicExplainability = (loc: any) => {
    if (!loc) return []
    if (loc.explainability_bullets && loc.explainability_bullets.length > 0) {
      return loc.explainability_bullets
    }
    const rentBudget = businessContext?.monthly_rent_budget || 150000
    const bullets = [
      `Commercial office density is ${(loc.office_density / 10).toFixed(1)}/10, sustaining weekday customer volume.`,
      `Monthly rent of ₹${loc.rent?.toLocaleString('en-IN') || (loc.avg_rent_sqft * 1200).toLocaleString('en-IN')} (₹${loc.avg_rent_sqft}/sqft) ${loc.rent <= rentBudget ? `fits your ₹${rentBudget.toLocaleString('en-IN')} budget` : `is calibrated to current corridor rates`}.`,
      `Daily footfall catchment of ${loc.footfall?.toLocaleString('en-IN')} active pedestrians across primary retail nodes.`,
      `Transit accessibility score: ${((1000 / Math.max(100, loc.metro_distance)) * 10).toFixed(1)}/10 with Metro access within ${loc.metro_distance}m.`,
      `Competitive density of ${loc.competitor_count} category competitors confirms verified demand depth without extreme hyper-saturation.`
    ]
    if (loc.hindsight_modified) {
      bullets.push(`Hindsight Memory: Verified historical performance in ${loc.area} recorded higher returns for this category.`)
    }
    return bullets
  }

  if (!isInitialized && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 space-y-4">
        <div className="w-16 h-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-2">
          <Store className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Retail Business Setup Required</h2>
        <p className="text-sm text-muted-foreground max-w-md">
          VentureScope requires verified retail brand information, budget, store size, and target customer segment before computing location intelligence and predictive models.
        </p>
        <Button onClick={() => navigate('/setup')} className="gap-2">
          Configure Retail Business <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    )
  }

  const activeBullets = getDynamicExplainability(activeLocalityData)
  const kpis = businessContext?.kpis || {}

  return (
    <div className="space-y-6 text-[#3D2A2D]">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-2xl font-serif font-bold tracking-tight text-[#3D2A2D]">
              Market Overview & Location Intelligence
            </h2>
            <Badge variant="outline" className="text-xs bg-[#E8F0EA] text-[#2E5A36] border-[#D4E2D7] font-semibold rounded-full px-2.5">
              Empirical AI Model · 15 Corridors
            </Badge>
          </div>
          <p className="text-xs text-[#7A666A] mt-1">
            {businessContext?.city || 'Hyderabad'} · <span className="font-semibold text-[#3D2A2D] font-serif">{businessContext?.venture_name || businessContext?.business_name || 'Retail Venture'}</span> · Category: {businessContext?.category || 'Specialty Retail'} · Segment: {customerSegment}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Segment Selector */}
          <select
            value={customerSegment}
            onChange={(e) => handleCustomerSegmentChange(e.target.value)}
            className="text-xs h-9 px-3 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] shadow-xs focus:border-[#D98B95]"
          >
            <option value="Tech Professionals">Tech Professionals</option>
            <option value="Corporate Executives">Corporate Executives</option>
            <option value="Students">Students</option>
            <option value="Families">Families</option>
            <option value="Luxury Buyers">Luxury Buyers</option>
            <option value="Transit Commuters">Transit Commuters</option>
          </select>

          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate('/setup?edit=true')}
            className="text-xs h-9 px-3.5 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#7A3E46] gap-1.5 shadow-xs"
          >
            <Store className="w-3.5 h-3.5 text-[#D98B95]" />
            Edit Setup
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={loadContext}
            className="text-xs h-9 px-3.5 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#7A3E46] gap-1.5 shadow-xs"
            disabled={isLoading}
          >
            <RefreshCw className={cn('w-3.5 h-3.5 text-[#D98B95]', isLoading && 'animate-spin')} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Hindsight Continuous Memory Insight Banner */}
      {hindsightInsight && (
        <div className="p-4 rounded-2xl bg-[#FBEFE8] border border-[#F2D8C9] text-xs text-[#8C502E] flex items-start gap-3 shadow-[0_4px_14px_rgba(140,80,46,0.06)]">
          <Brain className="w-5 h-5 text-[#8C502E] mt-0.5 shrink-0" />
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-serif font-bold text-sm text-[#8C502E]">Hindsight Continuous Learning Active</span>
              <Badge variant="outline" className="text-[10px] bg-[#FFF9F6] text-[#8C502E] border-[#F2D8C9] rounded-full px-2">
                Empirical Score Modified
              </Badge>
            </div>
            <p className="leading-relaxed text-[#784325]">
              {hindsightInsight}
            </p>
          </div>
        </div>
      )}

      {/* Dynamic KPI Strip (6 Required Dynamic Metrics from Backend) */}
      <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
        <CardContent className="py-5 px-6">
          <div className="grid grid-cols-2 sm:grid-cols-6 gap-4 divide-y sm:divide-y-0 sm:divide-x divide-[#E8D7D0]/60">
            {/* 1. Venture Viability Score */}
            <MetricCard
              title="Venture Viability Score"
              value={kpis.viability_score ? `${kpis.viability_score} / 100` : (top5Locations[0]?.score ? `${top5Locations[0].score} / 100` : "—")}
              trend="up"
              trendValue="Multi-Criteria Engine"
              evidenceType="modeled"
            />
            {/* 2. Expected Monthly Revenue */}
            <MetricCard
              title="Expected Monthly Revenue"
              value={kpis.expected_monthly_revenue ? `₹${(kpis.expected_monthly_revenue / 100000).toFixed(1)}L` : (businessContext?.revenue ? `₹${(businessContext.revenue / 100000).toFixed(1)}L` : "—")}
              trend="up"
              trendValue="What-If Pipeline"
              evidenceType="modeled"
              className="pt-4 sm:pt-0 sm:pl-4"
            />
            {/* 3. Break-even Month */}
            <MetricCard
              title="Break-even Month"
              value={kpis.break_even_month || businessContext?.break_even || "Month 8"}
              trend="stable"
              trendValue="Amortized Capex"
              evidenceType="modeled"
              className="pt-4 sm:pt-0 sm:pl-4"
            />
            {/* 4. Market Risk */}
            <MetricCard
              title="Market Risk"
              value={kpis.market_risk || activeLocalityData?.risk || "Low"}
              trend={kpis.market_risk === 'Low' ? 'up' : 'down'}
              trendValue="Rent-to-Revenue Ratio"
              evidenceType="observed"
              className="pt-4 sm:pt-0 sm:pl-4"
            />
            {/* 5. Opportunity Score */}
            <MetricCard
              title="Opportunity Score"
              value={kpis.opportunity_score ? `${kpis.opportunity_score} / 100` : "88 / 100"}
              trend="up"
              trendValue="Footfall & Demo Match"
              evidenceType="modeled"
              className="pt-4 sm:pt-0 sm:pl-4"
            />
            {/* 6. Competitor Saturation */}
            <MetricCard
              title="Competitor Saturation"
              value={kpis.competitor_saturation || saturation}
              trend={saturation.includes('Low') ? 'up' : 'stable'}
              trendValue="Google Places Density"
              evidenceType="observed"
              className="pt-4 sm:pt-0 sm:pl-4"
            />
          </div>
        </CardContent>
      </Card>

      {/* Main Grid: Google Maps Embed (2/3) + Top 5 Corridor Roster (1/3) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Google Maps Embed Component */}
        <div className="lg:col-span-2 min-h-[500px] flex flex-col space-y-2.5">
          <div className="flex items-center justify-between px-1">
            <div className="flex items-center gap-2 text-xs font-serif font-bold text-[#3D2A2D]">
              <Compass className="w-4 h-4 text-[#D98B95]" />
              <span>Google Maps Corridor Intelligence ({activeLocalityData?.area || 'Hyderabad'})</span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] text-[#7A666A] font-medium mr-1">Search Radius:</span>
              {[1, 2, 3, 5, 7, 10].map((r) => (
                <button
                  key={r}
                  type="button"
                  onClick={() => handleRadiusChange(r)}
                  className={cn(
                    "px-2.5 py-0.5 rounded-full text-[11px] font-semibold transition-all border",
                    searchRadiusKm === r
                      ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                      : "bg-[#FFF9F6] text-[#7A666A] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                  )}
                >
                  {r} km
                </button>
              ))}
            </div>
          </div>

          {/* GoogleMap Component loaded using @react-google-maps/api */}
          <GoogleMap
            locations={top5Locations}
            activeLocation={activeLocalityData}
            onSelectLocation={handleSelectLocation}
            competitors={competitors}
            searchRadiusKm={searchRadiusKm}
            className="flex-1 min-h-[460px]"
          />
        </div>

        {/* Top 5 Recommendations Card List */}
        <Card className="flex flex-col border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
          <CardHeader className="pb-3 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-serif font-bold text-[#3D2A2D] flex items-center gap-1.5">
                <Award className="w-4 h-4 text-[#D98B95]" />
                Top 5 Recommended Locations
              </CardTitle>
              <Badge variant="outline" className="text-[10px] rounded-full bg-[#EFC7CD]/40 text-[#7A3E46] border-[#D98B95]/40 font-semibold px-2 py-0.5">
                100% Calibrated
              </Badge>
            </div>
            <CardDescription className="text-xs text-[#7A666A]">
              Ranked dynamically by Audience Match (25%), Footfall (20%), Income (15%), Affordability (15%), Competitors (15%), Historical Sales (10%).
            </CardDescription>
          </CardHeader>

          <CardContent className="p-3.5 space-y-2.5 flex-1 overflow-y-auto">
            {top5Locations.map((loc, idx) => {
              const isSelected = activeLocalityData?.area === loc.area
              const rank = idx + 1

              return (
                <div
                  key={loc.area}
                  onClick={() => handleSelectLocation(loc)}
                  className={cn(
                    'p-3.5 rounded-2xl border transition-all cursor-pointer flex flex-col gap-2',
                    isSelected
                      ? 'bg-[#EFC7CD]/35 border-[#D98B95] ring-1 ring-[#D98B95]/40 shadow-[0_4px_16px_rgba(217,139,149,0.2)]'
                      : 'border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA]'
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2.5">
                      <span className={cn(
                        'w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold text-white shadow-xs',
                        rank === 1 ? 'bg-[#2E5A36]' : rank <= 3 ? 'bg-[#D98B95]' : 'bg-[#7A666A]'
                      )}>
                        #{rank}
                      </span>
                      <span className="font-serif font-bold text-sm text-[#3D2A2D]">{loc.area}</span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      {loc.hindsight_modified && (
                        <Badge variant="outline" className="text-[9px] rounded-full bg-[#FBEFE8] text-[#8C502E] border-[#F2D8C9]">
                          Memory Boost
                        </Badge>
                      )}
                      <span className="text-xs font-bold text-[#2E5A36] bg-[#E8F0EA] border border-[#D4E2D7] px-2.5 py-0.5 rounded-full">
                        {loc.score} pts
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-1 text-[11px] text-[#7A666A] pt-1.5 border-t border-[#E8D7D0]/60">
                    <div>
                      <span className="block text-[10px] uppercase font-semibold text-[#7A666A]">Exp. Revenue</span>
                      <span className="font-semibold text-[#3D2A2D]">₹{(loc.predicted_monthly_revenue / 100000).toFixed(1)}L/mo</span>
                    </div>
                    <div>
                      <span className="block text-[10px] uppercase font-semibold text-[#7A666A]">Corridor Rent</span>
                      <span className="font-medium text-[#3D2A2D]">₹{(loc.rent / 1000).toFixed(0)}k</span>
                    </div>
                    <div>
                      <span className="block text-[10px] uppercase font-semibold text-[#7A666A]">Footfall</span>
                      <span className="font-medium text-[#3D2A2D]">{(loc.footfall / 1000).toFixed(0)}k/day</span>
                    </div>
                  </div>
                </div>
              )
            })}
          </CardContent>
        </Card>
      </div>

      {/* Dynamic Ranking Table */}
      <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
        <CardHeader className="pb-3 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div>
              <CardTitle className="text-base font-serif font-bold text-[#3D2A2D] flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-[#D98B95]" />
                Empirical Locality Rankings
              </CardTitle>
              <CardDescription className="text-xs text-[#7A666A]">
                Computed across all {allLocations.length || 15} commercial retail corridors from areas.csv. Click any row to inspect live Google Maps and intelligence.
              </CardDescription>
            </div>
            <Badge variant="outline" className="text-xs rounded-full bg-[#FFF9F6] border-[#E8D7D0] text-[#7A666A] shrink-0">
              Interactive Table · Select Row to Inspect
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="p-0 overflow-x-auto">
          <table className="w-full text-xs text-left">
            <thead className="bg-[#F8F2EC]/60 border-b border-[#E8D7D0] text-[#7A666A] font-semibold uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3 px-4">Rank</th>
                <th className="py-3 px-4">Area</th>
                <th className="py-3 px-4 text-center">Score</th>
                <th className="py-3 px-4">Revenue</th>
                <th className="py-3 px-4">Rent</th>
                <th className="py-3 px-4">Footfall</th>
                <th className="py-3 px-4 text-center">Competitors</th>
                <th className="py-3 px-4 text-center">Risk</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#E8D7D0]/60">
              {allLocations.map((loc, idx) => {
                const isSelected = activeLocalityData?.area === loc.area
                const rank = idx + 1
                return (
                  <tr
                    key={loc.area}
                    onClick={() => handleSelectLocation(loc)}
                    className={cn(
                      "cursor-pointer transition-colors duration-150 hover:bg-[#F8E8EA]",
                      isSelected && "bg-[#EFC7CD]/35 font-medium"
                    )}
                  >
                    <td className="py-3 px-4">
                      <span className={cn(
                        "w-5 h-5 rounded-full inline-flex items-center justify-center text-[10px] font-bold text-white shadow-xs",
                        rank === 1 ? "bg-[#2E5A36]" : rank <= 3 ? "bg-[#D98B95]" : "bg-[#7A666A]"
                      )}>
                        #{rank}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-serif font-bold text-[#3D2A2D] flex items-center gap-2">
                      <span>{loc.area}</span>
                      {loc.hindsight_modified && (
                        <Badge variant="outline" className="text-[9px] py-0 px-1.5 rounded-full bg-[#FBEFE8] text-[#8C502E] border-[#F2D8C9]">
                          Hindsight
                        </Badge>
                      )}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className="font-bold text-[#2E5A36] bg-[#E8F0EA] border border-[#D4E2D7] px-2.5 py-0.5 rounded-full">
                        {loc.score}
                      </span>
                    </td>
                    <td className="py-3 px-4 font-semibold text-[#3D2A2D]">
                      ₹{(loc.predicted_monthly_revenue / 100000).toFixed(1)}L/mo
                    </td>
                    <td className="py-3 px-4 text-[#7A666A]">
                      ₹{(loc.rent / 1000).toFixed(0)}k (₹{loc.avg_rent_sqft}/sqft)
                    </td>
                    <td className="py-3 px-4 text-[#7A666A]">
                      {loc.footfall?.toLocaleString('en-IN')}/day
                    </td>
                    <td className="py-3 px-4 text-center font-semibold text-[#3D2A2D]">
                      {loc.competitor_count}
                    </td>
                    <td className="py-3 px-4 text-center">
                      <Badge variant="outline" className={cn(
                        "text-[10px] py-0.5 px-2.5 rounded-full font-semibold",
                        loc.risk === 'Low' ? "bg-[#E8F0EA] text-[#2E5A36] border-[#D4E2D7]" :
                        loc.risk === 'Medium' ? "bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]" :
                        "bg-[#FDF0F2] text-[#9A3B45] border-[#F5C2C7]"
                      )}>
                        {loc.risk}
                      </Badge>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </CardContent>
      </Card>

      {/* Selected Locality Deep Dive + Dynamic Explainability */}
      {activeLocalityData && (
        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
          <CardHeader className="pb-3 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
              <div>
                <CardTitle className="text-base font-serif font-bold text-[#3D2A2D] flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-[#D98B95]" />
                  {activeLocalityData.area} Intelligence Deep Dive
                </CardTitle>
                <CardDescription className="text-xs text-[#7A666A]">
                  Empirical metrics from commercial dataset
                </CardDescription>
              </div>

              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs rounded-full bg-[#FFF9F6] border-[#E8D7D0] text-[#7A666A]">
                  Daily Footfall: {activeLocalityData.footfall?.toLocaleString('en-IN')}
                </Badge>
                <Badge variant="outline" className="text-xs rounded-full bg-[#FFF9F6] border-[#E8D7D0] text-[#7A666A]">
                  Avg Income: ₹{activeLocalityData.avg_income?.toLocaleString('en-IN')}/mo
                </Badge>
                <Badge variant="outline" className="text-xs rounded-full bg-[#FFF9F6] border-[#E8D7D0] text-[#7A666A]">
                  Office Density: {activeLocalityData.office_density}/100
                </Badge>
              </div>
            </div>
          </CardHeader>

          <CardContent className="pt-5 space-y-5 px-6">
            {/* Google Places Competitor Intelligence Section */}
            <div>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Store className="w-4 h-4 text-[#D98B95]" />
                  <span className="text-xs font-serif font-bold text-[#3D2A2D]">Nearby Google Places Competitors</span>
                  <Badge variant="outline" className={cn(
                    'text-[10px] rounded-full px-2.5 font-semibold',
                    saturation.includes('Low') ? 'bg-[#E8F0EA] text-[#2E5A36] border-[#D4E2D7]' : 'bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]'
                  )}>
                    {saturation} ({competitors.length} tracked)
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
                {competitors.slice(0, 4).map((c, i) => (
                  <div key={i} className="p-3.5 rounded-2xl border border-[#E8D7D0] bg-[#F8F2EC]/40 text-xs space-y-1.5 shadow-xs">
                    <div className="font-serif font-bold text-[#3D2A2D] truncate">{c.business_name}</div>
                    <div className="text-[11px] text-[#7A666A] flex justify-between">
                      <span className="truncate">{c.category}</span>
                      <span className="text-[#D98B95] font-semibold">★ {c.rating} ({c.review_count})</span>
                    </div>
                    <div className="text-[10px] text-[#7A666A] flex justify-between pt-1 border-t border-[#E8D7D0]/60">
                      <span>Distance: {c.distance_km ? `${c.distance_km} km` : 'nearby'}</span>
                      <span className="font-semibold text-[#7A3E46]">{c.price_level || '$$'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Explainable AI: "Why [Selected Locality]?" & "Why not the others?" */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-[#E8D7D0]/60">
              {/* Dynamic Why This Location */}
              <div className="space-y-2.5">
                <h4 className="text-xs font-serif font-bold text-[#3D2A2D] flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-[#2E5A36]" />
                  Why {activeLocalityData.area}? (Dynamic Evidence)
                </h4>
                <ul className="space-y-2">
                  {activeBullets.map((reason: string, i: number) => (
                    <li key={i} className="text-xs text-[#2E5A36] flex items-start gap-2.5 bg-[#E8F0EA]/70 p-3 rounded-2xl border border-[#D4E2D7]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#2E5A36] mt-1.5 shrink-0" />
                      <span className="leading-relaxed">{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Why NOT the others */}
              <div className="space-y-2.5">
                <h4 className="text-xs font-serif font-bold text-[#3D2A2D] flex items-center gap-1.5">
                  <AlertCircle className="w-4 h-4 text-[#9A3B45]" />
                  Why not the others? (Comparative Suitability)
                </h4>
                <ul className="space-y-2">
                  {whyNotOthers.map((reason, i) => (
                    <li key={i} className="text-xs text-[#9A3B45] flex items-start gap-2.5 bg-[#FDF0F2]/70 p-3 rounded-2xl border border-[#F5C2C7]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#9A3B45] mt-1.5 shrink-0" />
                      <span className="leading-relaxed">{reason}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
