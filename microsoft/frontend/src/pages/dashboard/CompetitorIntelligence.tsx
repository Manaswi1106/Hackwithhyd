import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { MetricCard } from '@/components/shared/MetricCard'
import {
  Store, MapPin, RefreshCw, Compass, AlertCircle,
  Star, DollarSign, Clock, ShieldCheck, CheckCircle2, ChevronRight
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/services/api'
import { useNavigate } from 'react-router-dom'

export default function CompetitorIntelligence() {
  const navigate = useNavigate()
  const [businessContext, setBusinessContext] = useState<any>(null)
  const [isInitialized, setIsInitialized] = useState<boolean>(true)
  const [selectedLocality, setSelectedLocality] = useState<string>('Madhapur')
  const [radiusKm, setRadiusKm] = useState<number>(3.0)
  const [competitors, setCompetitors] = useState<any[]>([])
  const [saturation, setSaturation] = useState<string>('Medium saturation')
  const [isDemoData, setIsDemoData] = useState<boolean>(true)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [activeCategoryFilter, setActiveCategoryFilter] = useState<string>('auto')
  const [domainMismatchError, setDomainMismatchError] = useState<string | null>(null)

  const loadData = async () => {
    setIsLoading(true)
    setDomainMismatchError(null)
    try {
      const ctx = await api.getContext()
      if (ctx && ctx.is_initialized) {
        setIsInitialized(true)
        setBusinessContext(ctx)
        setSelectedLocality(ctx.selected_locality || 'Madhapur')
        setRadiusKm(ctx.search_radius_km || 3.0)

        const comps = ctx.competitor_data || {}
        setCompetitors(comps.competitors || [])
        setSaturation(comps.saturation || 'Medium saturation')
        setIsDemoData(comps.is_demo_data ?? true)
      } else {
        setIsInitialized(false)
      }
    } catch (e) {
      console.warn('Failed to load competitor intelligence:', e)
      setIsInitialized(false)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleLocalityChange = async (newLocality: string) => {
    setSelectedLocality(newLocality)
    setIsLoading(true)
    try {
      const updated = await api.updateContext({ selected_locality: newLocality })
      if (updated) {
        setBusinessContext(updated)
        const comps = updated.competitor_data || {}
        setCompetitors(comps.competitors || [])
        setSaturation(comps.saturation || 'Medium saturation')
        setIsDemoData(comps.is_demo_data ?? true)
      }
    } catch (e) {
      console.warn('Failed to update locality for competitors:', e)
    } finally {
      setIsLoading(false)
    }
  }

  const handleRadiusChange = async (newRadius: number) => {
    setRadiusKm(newRadius)
    setIsLoading(true)
    try {
      const updated = await api.updateContext({ search_radius_km: newRadius })
      if (updated) {
        setBusinessContext(updated)
        const comps = updated.competitor_data || {}
        setCompetitors(comps.competitors || [])
        setSaturation(comps.saturation || 'Medium saturation')
        setIsDemoData(comps.is_demo_data ?? true)
      }
    } catch (e) {
      console.warn('Failed to update radius for competitors:', e)
    } finally {
      setIsLoading(false)
    }
  }

  const handleCategoryFilterClick = (targetDomain: string) => {
    const ventureCat = (businessContext?.category || 'Specialty Coffee').toLowerCase()
    const isFood = ventureCat.includes('coffee') || ventureCat.includes('food') || ventureCat.includes('restaurant') || ventureCat.includes('bakery') || ventureCat.includes('cafe')

    if (targetDomain === 'Fashion') {
      if (isFood) {
        setDomainMismatchError("The detected business domain is Food & Beverage. Competitor analysis for Fashion cannot be generated.")
        return
      }
    } else if (targetDomain === 'Food & Beverage') {
      if (!isFood) {
        setDomainMismatchError("The detected business domain is Fashion & Lifestyle. Competitor analysis for Food & Beverage cannot be generated.")
        return
      }
    }

    setDomainMismatchError(null)
    setActiveCategoryFilter(targetDomain)
  }

  if (!isInitialized && !isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center p-6 space-y-4">
        <div className="w-16 h-16 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary mb-2">
          <Store className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-foreground">Retail Business Setup Required</h2>
        <p className="text-sm text-muted-foreground max-w-md">
          Competitor intelligence requires a verified retail category and location before querying Google Places API.
        </p>
        <Button onClick={() => navigate('/setup')} className="gap-2">
          Configure Retail Business <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    )
  }

  const detectedCategory = businessContext?.category || 'Specialty Coffee'

  return (
    <div className="space-y-6 text-[#3D2A2D]">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-2xl font-serif font-bold tracking-tight text-[#3D2A2D]">
              Competitor Intelligence & Saturation
            </h2>
            <Badge variant="outline" className={cn(
              "text-xs font-semibold rounded-full px-2.5",
              isDemoData ? "bg-[#FEF3C7] text-[#92400E] border-[#FDE68A]" : "bg-[#E8F0EA] text-[#2E5A36] border-[#D4E2D7]"
            )}>
              {isDemoData ? "Calibrated Reference · DEMO DATA" : "Live Google Places API"}
            </Badge>
          </div>
          <p className="text-xs text-[#7A666A] mt-1">
            Active Venture: <span className="font-semibold text-[#3D2A2D] font-serif">{businessContext?.business_name || 'Retail Venture'}</span> · Category: <span className="font-semibold text-[#3D2A2D]">{detectedCategory}</span>
          </p>
        </div>

        <div className="flex items-center gap-2">
          {/* Locality Selector */}
          <select
            value={selectedLocality}
            onChange={(e) => handleLocalityChange(e.target.value)}
            className="text-xs h-9 px-3 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] shadow-xs focus:border-[#D98B95]"
          >
            {['Madhapur', 'Gachibowli', 'HITEC City', 'Kondapur', 'Financial District', 'Jubilee Hills', 'Banjara Hills', 'Begumpet', 'Secunderabad', 'Ameerpet', 'Kukatpally'].map((loc) => (
              <option key={loc} value={loc}>{loc}</option>
            ))}
          </select>

          <Button
            variant="outline"
            size="sm"
            onClick={loadData}
            className="text-xs h-9 px-3.5 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#7A3E46] gap-1.5 shadow-xs"
            disabled={isLoading}
          >
            <RefreshCw className={cn('w-3.5 h-3.5 text-[#D98B95]', isLoading && 'animate-spin')} />
            Refresh
          </Button>
        </div>
      </div>

      {/* KPI Ribbon */}
      <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
        <CardContent className="py-5 px-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 divide-y sm:divide-y-0 sm:divide-x divide-[#E8D7D0]/60">
            <MetricCard
              title="Tracked Competitors"
              value={`${competitors.length} Outlets`}
              trend="stable"
              trendValue={`Within ${radiusKm} km radius`}
              evidenceType="observed"
            />
            <MetricCard
              title="Market Saturation"
              value={saturation}
              trend={saturation.includes('Low') ? 'up' : 'stable'}
              trendValue="Empirical Density Score"
              evidenceType="observed"
              className="pt-4 sm:pt-0 sm:pl-6"
            />
            <MetricCard
              title="Average Rating"
              value={competitors.length > 0 ? `★ ${(competitors.reduce((acc, c) => acc + (c.rating || 4.0), 0) / competitors.length).toFixed(1)}` : '—'}
              trend="up"
              trendValue="Aggregated Reviews"
              evidenceType="observed"
              className="pt-4 sm:pt-0 sm:pl-6"
            />
            <MetricCard
              title="Search Radius"
              value={`${radiusKm} km`}
              trend="stable"
              trendValue="Haversine Geo-Perimeter"
              evidenceType="modeled"
              className="pt-4 sm:pt-0 sm:pl-6"
            />
          </div>
        </CardContent>
      </Card>

      {/* Controls & Domain Validation Filter Strip */}
      <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
        <CardContent className="p-5 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            {/* Domain Filter Buttons */}
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-[#7A666A] uppercase tracking-wider">
                Category Domain Verification:
              </span>
              <div className="flex flex-wrap gap-2 pt-0.5">
                <Button
                  type="button"
                  size="sm"
                  variant={activeCategoryFilter === 'auto' ? 'default' : 'outline'}
                  onClick={() => { setDomainMismatchError(null); setActiveCategoryFilter('auto') }}
                  className={cn(
                    "text-xs h-8 px-3 rounded-full transition-all",
                    activeCategoryFilter === 'auto'
                      ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                      : "bg-[#FFF9F6] text-[#7A666A] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                  )}
                >
                  Verified Domain ({detectedCategory})
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={activeCategoryFilter === 'Food & Beverage' ? 'default' : 'outline'}
                  onClick={() => handleCategoryFilterClick('Food & Beverage')}
                  className={cn(
                    "text-xs h-8 px-3 rounded-full transition-all",
                    activeCategoryFilter === 'Food & Beverage'
                      ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                      : "bg-[#FFF9F6] text-[#7A666A] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                  )}
                >
                  Food & Beverage
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant={activeCategoryFilter === 'Fashion' ? 'default' : 'outline'}
                  onClick={() => handleCategoryFilterClick('Fashion')}
                  className={cn(
                    "text-xs h-8 px-3 rounded-full transition-all",
                    activeCategoryFilter === 'Fashion'
                      ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                      : "bg-[#FFF9F6] text-[#7A666A] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                  )}
                >
                  Fashion & Retail
                </Button>
              </div>
            </div>

            {/* Radius Buttons */}
            <div className="space-y-1.5">
              <span className="text-[11px] font-semibold text-[#7A666A] uppercase tracking-wider">
                Radius Filter:
              </span>
              <div className="flex gap-1.5 pt-0.5">
                {[1, 2, 3, 5, 7, 10].map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => handleRadiusChange(r)}
                    className={cn(
                      "px-3 py-1 rounded-full text-xs font-semibold transition-all border",
                      radiusKm === r
                        ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                        : "bg-[#FFF9F6] text-[#7A666A] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                    )}
                  >
                    {r} km
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Domain Mismatch Alert (Mandatory Exact Text Requirement) */}
          {domainMismatchError && (
            <div className="p-3.5 rounded-2xl bg-[#FDF0F2] border border-[#F5C2C7] text-[#9A3B45] text-xs flex items-start gap-2.5 shadow-xs">
              <AlertCircle className="w-4 h-4 mt-0.5 shrink-0 text-[#9A3B45]" />
              <div className="leading-relaxed font-semibold">
                {domainMismatchError}
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Competitor Cards: ONLY Name, Rating, Reviews, Distance, Category, Open/Closed, Price Level */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Store className="w-4 h-4 text-[#D98B95]" />
            <h3 className="text-base font-serif font-bold text-[#3D2A2D]">
              Competitor Establishments in {selectedLocality}
            </h3>
            <Badge variant="outline" className="text-xs rounded-full bg-[#FFF9F6] border-[#E8D7D0] text-[#7A666A]">
              {competitors.length} Results
            </Badge>
          </div>
          <span className="text-xs text-[#7A666A]">
            Strict domain match: <span className="font-semibold text-[#3D2A2D]">{detectedCategory}</span>
          </span>
        </div>

        {competitors.length === 0 ? (
          <Card className="p-8 text-center border-dashed border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px]">
            <p className="text-sm text-[#7A666A]">No direct competitors found within {radiusKm} km of {selectedLocality}. Try increasing the search radius.</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {competitors.map((comp, idx) => (
              <Card key={idx} className="border-[#E8D7D0] bg-[#FFF9F6] hover:border-[#D98B95] rounded-2xl shadow-[0_4px_14px_rgba(122,62,70,0.04)] hover:shadow-[0_8px_24px_rgba(122,62,70,0.08)] transition-all duration-200">
                <CardContent className="p-4 space-y-2.5">
                  {/* Name and Price Level */}
                  <div className="flex items-start justify-between gap-2">
                    <h4 className="font-serif font-bold text-sm text-[#3D2A2D] leading-snug">
                      {comp.business_name}
                    </h4>
                    <span className="text-xs font-bold text-[#7A3E46] bg-[#EFC7CD]/40 border border-[#D98B95]/30 px-2.5 py-0.5 rounded-full shrink-0">
                      {comp.price_level || '$$'}
                    </span>
                  </div>

                  {/* Category */}
                  <div className="text-xs text-[#7A666A] flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#D98B95] shrink-0" />
                    <span className="truncate">{comp.category}</span>
                  </div>

                  {/* Rating & Review Count */}
                  <div className="flex items-center justify-between text-xs pt-1.5 border-t border-[#E8D7D0]/60">
                    <div className="flex items-center gap-1 text-[#D98B95] font-semibold">
                      <Star className="w-3.5 h-3.5 fill-[#D98B95] text-[#D98B95]" />
                      <span>{comp.rating}</span>
                      <span className="text-[#7A666A] font-normal">({comp.review_count} reviews)</span>
                    </div>

                    {/* Open / Closed Status */}
                    <Badge variant="outline" className={cn(
                      "text-[10px] py-0 px-2 rounded-full font-semibold",
                      comp.open_now !== false ? "bg-[#E8F0EA] text-[#2E5A36] border-[#D4E2D7]" : "bg-[#FDF0F2] text-[#9A3B45] border-[#F5C2C7]"
                    )}>
                      {comp.open_now !== false ? "Open Now" : "Closed"}
                    </Badge>
                  </div>

                  {/* Distance */}
                  <div className="text-[11px] text-[#7A666A] flex items-center justify-between pt-0.5">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-[#D98B95]" />
                      Distance
                    </span>
                    <span className="font-medium text-[#3D2A2D]">
                      {comp.distance_km ? `${comp.distance_km} km away` : 'Nearby'}
                    </span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
