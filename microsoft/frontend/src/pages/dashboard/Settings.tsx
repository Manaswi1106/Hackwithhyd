import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Settings as SettingsIcon, Save, RotateCcw, ArrowLeft, CheckCircle2,
  MapPin, Globe, Sparkles, Store, Compass, RefreshCw, AlertCircle,
  UtensilsCrossed, Shirt, HeartPulse, Landmark, Laptop, ShoppingBag
} from 'lucide-react'
import { api } from '@/services/api'
import { cn } from '@/lib/utils'
import { BUSINESS_DOMAINS, checkDomainCompatibility } from '@/pages/Setup'

const CUSTOMER_SEGMENTS = [
  'Tech Professionals',
  'Corporate Executives',
  'Students',
  'Families',
  'Luxury Buyers',
  'Transit Commuters'
]

const RADIUS_OPTIONS = [1, 2, 3, 5, 7, 10]

export default function Settings() {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)

  // Context snapshot for Reset / Cancel
  const [originalContext, setOriginalContext] = useState<any>(null)

  // Editable fields
  const [ventureName, setVentureName] = useState('')
  const [selectedDomain, setSelectedDomain] = useState<string>('Food & Beverage')
  const [selectedCategory, setSelectedCategory] = useState<string>('Casual Dining')
  const [retailUrl, setRetailUrl] = useState('')
  const [locationCity, setLocationCity] = useState('')
  const [rent, setRent] = useState<number>(150000)
  const [storeSize, setStoreSize] = useState<number>(1200)
  const [customerSegment, setCustomerSegment] = useState('Tech Professionals')
  const [searchRadiusKm, setSearchRadiusKm] = useState<number>(3.0)

  // URL extraction preview
  const [isAnalyzingUrl, setIsAnalyzingUrl] = useState(false)
  const [urlAnalysisNotice, setUrlAnalysisNotice] = useState<string | null>(null)
  const [domainWarning, setDomainWarning] = useState<string | null>(null)

  const activeDomainDef = BUSINESS_DOMAINS.find(d => d.id === selectedDomain) || BUSINESS_DOMAINS[0]

  const populateForm = (ctx: any) => {
    if (!ctx) return
    setVentureName(ctx.venture_name || ctx.business_name || '')
    if (ctx.domain) {
      const matchDom = BUSINESS_DOMAINS.find(d => d.id.toLowerCase() === ctx.domain.toLowerCase())
      if (matchDom) setSelectedDomain(matchDom.id)
    }
    if (ctx.category) {
      setSelectedCategory(ctx.category)
    }
    setRetailUrl(ctx.retail_url || '')
    setLocationCity(ctx.city || ctx.selected_locality || 'Hyderabad')
    setRent(ctx.rent || ctx.monthly_rent_budget || 150000)
    setStoreSize(ctx.store_size || 1200)
    setCustomerSegment(ctx.customer_segment || 'Tech Professionals')
    setSearchRadiusKm(ctx.search_radius_km || 3.0)
  }

  const loadSettings = async () => {
    setIsLoading(true)
    setErrorMessage(null)
    try {
      const ctx = await api.getContext()
      if (ctx && ctx.is_initialized) {
        setOriginalContext(ctx)
        populateForm(ctx)
      } else {
        setErrorMessage("Business context not initialized. Please complete Setup first.")
      }
    } catch (e: any) {
      setErrorMessage(e.message || "Failed to load settings")
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    loadSettings()
  }, [])

  // Switch domain
  const handleDomainChange = (domainId: string) => {
    setSelectedDomain(domainId)
    const def = BUSINESS_DOMAINS.find(d => d.id === domainId)
    if (def && def.subcategories.length > 0) {
      setSelectedCategory(def.subcategories[0])
    }
    setDomainWarning(null)
  }

  // Analyze URL with Groq intelligence
  const handleAnalyzeUrl = async () => {
    if (!retailUrl.trim()) return
    setIsAnalyzingUrl(true)
    setUrlAnalysisNotice(null)
    setDomainWarning(null)
    setErrorMessage(null)

    try {
      const res = await api.classifyUrl(retailUrl.trim(), selectedCategory, ventureName.trim())
      if (res && res.success && res.data) {
        const d = res.data
        if (d.brand && !ventureName.trim()) {
          setVentureName(d.brand)
        }
        if (d.audience) {
          const matchedSeg = CUSTOMER_SEGMENTS.find(s => s.toLowerCase() === d.audience.toLowerCase())
          if (matchedSeg) setCustomerSegment(matchedSeg)
        }

        const detDom = d.primary_domain || d.domain || 'Commercial'
        const detSub = d.subdomain || d.category || 'Retail'
        const check = checkDomainCompatibility(selectedDomain, selectedCategory, detDom, detSub)

        if (check.isMatch) {
          setUrlAnalysisNotice(`✓ Verified: ${d.brand || 'Brand'} · Domain: ${detDom} · Category: ${detSub}`)
        } else {
          setDomainWarning(check.message || `Website evidence indicates ${detDom}, but selected category is '${selectedCategory}'.`)
        }
      } else {
        setErrorMessage(res?.message || "Insufficient website evidence.")
      }
    } catch (e: any) {
      setErrorMessage(e.message || "Website analysis failed")
    } finally {
      setIsAnalyzingUrl(false)
    }
  }

  // Save changes via POST /api/context/update
  const handleSave = async (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    setIsSaving(true)
    setSaveSuccess(null)
    setErrorMessage(null)

    try {
      const updates: Record<string, any> = {
        venture_name: ventureName.trim(),
        domain: selectedDomain,
        category: selectedCategory,
        retail_url: retailUrl.trim() || null,
        city: locationCity.trim(),
        rent: Number(rent),
        monthly_rent_budget: Number(rent),
        store_size: Number(storeSize),
        customer_segment: customerSegment,
        search_radius_km: Number(searchRadiusKm),
      }

      const updated = await api.updateContext(updates)
      if (updated) {
        setOriginalContext(updated)
        populateForm(updated)
        setSaveSuccess("Settings saved successfully! Overview, Simulation, and Competitors have been refreshed.")
      }
    } catch (e: any) {
      setErrorMessage(e.message || "Failed to update settings")
    } finally {
      setIsSaving(false)
    }
  }

  // Reset to original context
  const handleReset = () => {
    if (originalContext) {
      populateForm(originalContext)
      setSaveSuccess("Restored original venture parameters.")
      setErrorMessage(null)
      setUrlAnalysisNotice(null)
      setDomainWarning(null)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <RefreshCw className="w-4 h-4 animate-spin text-primary" />
          <span>Loading venture settings...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12 text-[#3D2A2D]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#E8D7D0]">
        <div>
          <h2 className="text-2xl font-serif font-bold tracking-tight text-[#3D2A2D] flex items-center gap-2">
            <SettingsIcon className="w-5 h-5 text-[#D98B95]" />
            Venture Settings
          </h2>
          <p className="text-xs text-[#7A666A] mt-1">
            Modify any venture parameter. Saved changes immediately propagate to Overview, Simulation, and Competitor models.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={() => navigate('/dashboard/overview')}
            className="text-xs h-9 px-3.5 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#7A3E46] gap-1.5 shadow-xs"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            Back to Overview
          </Button>
        </div>
      </div>

      {/* Notifications */}
      {saveSuccess && (
        <div className="p-3.5 rounded-2xl bg-[#E8F0EA] border border-[#D4E2D7] text-[#2E5A36] text-xs flex items-center gap-2.5 shadow-xs">
          <CheckCircle2 className="w-4 h-4 shrink-0 text-[#2E5A36]" />
          <span className="font-medium">{saveSuccess}</span>
        </div>
      )}

      {errorMessage && (
        <div className="p-3.5 rounded-2xl bg-[#FDF0F2] border border-[#F5C2C7] text-[#9A3B45] text-xs flex items-center gap-2.5 shadow-xs">
          <AlertCircle className="w-4 h-4 shrink-0 text-[#9A3B45]" />
          <span className="font-medium">{errorMessage}</span>
        </div>
      )}

      <form onSubmit={handleSave} className="space-y-6">
        {/* Card 1: Venture Identity & Category Selection */}
        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
          <CardHeader className="pb-3 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
            <CardTitle className="text-sm font-serif font-bold text-[#3D2A2D] flex items-center gap-2">
              <Store className="w-4 h-4 text-[#D98B95]" />
              Venture Identity & Category
            </CardTitle>
            <CardDescription className="text-xs text-[#7A666A]">
              Venture brand name, industry domain, category, and website URL.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Venture Name */}
              <div className="space-y-1.5">
                <Label htmlFor="ventureName" className="text-xs font-semibold text-[#3D2A2D]">Venture Name</Label>
                <Input
                  id="ventureName"
                  value={ventureName}
                  onChange={(e) => setVentureName(e.target.value)}
                  placeholder="e.g. Blue Tokai Roasters"
                  className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                  required
                />
              </div>

              {/* Location */}
              <div className="space-y-1.5">
                <Label htmlFor="locationCity" className="text-xs font-semibold text-[#3D2A2D]">Location / Metro</Label>
                <div className="relative">
                  <MapPin className="w-3.5 h-3.5 absolute left-3.5 top-3.5 text-[#7A666A]" />
                  <Input
                    id="locationCity"
                    value={locationCity}
                    onChange={(e) => setLocationCity(e.target.value)}
                    placeholder="e.g. Hyderabad, Telangana"
                    className="text-xs h-10 pl-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Business Domain Selection */}
            <div className="space-y-2 pt-2 border-t border-[#E8D7D0]/60">
              <Label className="text-xs font-semibold text-[#3D2A2D]">Business Domain</Label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                {BUSINESS_DOMAINS.map((domain) => {
                  const Icon = domain.icon
                  const isSelected = selectedDomain === domain.id
                  return (
                    <button
                      key={domain.id}
                      type="button"
                      onClick={() => handleDomainChange(domain.id)}
                      className={cn(
                        "p-3 rounded-2xl text-xs font-medium text-left border flex items-center gap-2.5 transition-all duration-150",
                        isSelected
                          ? "bg-[#EFC7CD]/40 text-[#7A3E46] border-[#D98B95] shadow-[0_4px_16px_rgba(217,139,149,0.2)] font-semibold"
                          : "bg-[#FFF9F6] text-[#3D2A2D] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                      )}
                    >
                      <Icon className={cn("w-4 h-4 shrink-0", isSelected ? "text-[#7A3E46]" : "text-[#D98B95]")} />
                      <span className="truncate">{domain.name}</span>
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Specific Category Selection */}
            <div className="space-y-2 pt-1 border-t border-[#E8D7D0]/60">
              <Label className="text-xs font-semibold text-[#3D2A2D]">Business Category</Label>
              <div className="flex flex-wrap gap-2">
                {activeDomainDef.subcategories.map((subcat) => {
                  const isCatSelected = selectedCategory === subcat
                  return (
                    <button
                      key={subcat}
                      type="button"
                      onClick={() => {
                        setSelectedCategory(subcat)
                        setDomainWarning(null)
                      }}
                      className={cn(
                        "px-3.5 py-1.5 rounded-full text-xs font-medium border transition-all duration-150",
                        isCatSelected
                          ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                          : "bg-[#FFF9F6] text-[#3D2A2D] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                      )}
                    >
                      {subcat}
                    </button>
                  )
                })}
              </div>
            </div>

            {/* Website URL */}
            <div className="space-y-2 pt-2 border-t border-[#E8D7D0]/60">
              <div className="flex items-center justify-between">
                <Label htmlFor="retailUrl" className="text-xs font-semibold text-[#3D2A2D]">Business Website URL (Optional)</Label>
                <span className="text-[10px] text-[#7A666A]">AI validates category consistency</span>
              </div>
              <div className="flex gap-2.5">
                <div className="relative flex-1">
                  <Globe className="w-4 h-4 absolute left-3.5 top-3 text-[#7A666A]" />
                  <Input
                    id="retailUrl"
                    type="url"
                    value={retailUrl}
                    onChange={(e) => setRetailUrl(e.target.value)}
                    placeholder="https://example.com"
                    className="text-xs h-10 pl-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                  />
                </div>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAnalyzeUrl}
                  disabled={isAnalyzingUrl || !retailUrl.trim()}
                  className="text-xs h-10 px-4 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#7A3E46] gap-1.5 shrink-0 shadow-xs"
                >
                  {isAnalyzingUrl ? <RefreshCw className="w-3.5 h-3.5 animate-spin text-[#D98B95]" /> : <Sparkles className="w-3.5 h-3.5 text-[#D98B95]" />}
                  Analyze URL
                </Button>
              </div>

              {domainWarning && (
                <div className="p-3.5 rounded-2xl bg-[#FDF0F2] border border-[#F5C2C7] text-[#9A3B45] text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-[#9A3B45]" />
                  <span>{domainWarning}</span>
                </div>
              )}

              {urlAnalysisNotice && (
                <p className="text-[11px] text-[#2E5A36] font-medium mt-1">
                  {urlAnalysisNotice}
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Card 2: Financial & Physical Capacity */}
        <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] overflow-hidden">
          <CardHeader className="pb-3 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
            <CardTitle className="text-sm font-serif font-bold text-[#3D2A2D] flex items-center gap-2">
              <Compass className="w-4 h-4 text-[#D98B95]" />
              Financial & Physical Scope
            </CardTitle>
            <CardDescription className="text-xs text-[#7A666A]">
              Physical square footage, monthly rental capacity, customer segment, and Google Maps radius.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Monthly Rent */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <Label htmlFor="rent" className="font-semibold text-[#3D2A2D]">Monthly Rent Budget</Label>
                  <span className="text-[#7A3E46] font-serif font-bold">₹{rent.toLocaleString('en-IN')} (₹{(rent / 100000).toFixed(2)}L)</span>
                </div>
                <Input
                  id="rent"
                  type="number"
                  min={10000}
                  step={5000}
                  value={rent}
                  onChange={(e) => setRent(Number(e.target.value))}
                  className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                  required
                />
              </div>

              {/* Store Size */}
              <div className="space-y-1.5">
                <div className="flex justify-between text-xs">
                  <Label htmlFor="storeSize" className="font-semibold text-[#3D2A2D]">Store Size (sqft)</Label>
                  <span className="text-[#7A3E46] font-serif font-bold">{storeSize} sqft</span>
                </div>
                <Input
                  id="storeSize"
                  type="number"
                  min={100}
                  step={50}
                  value={storeSize}
                  onChange={(e) => setStoreSize(Number(e.target.value))}
                  className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                  required
                />
              </div>
            </div>

            {/* Customer Segment */}
            <div className="space-y-2 pt-1 border-t border-[#E8D7D0]/60">
              <Label className="text-xs font-semibold text-[#3D2A2D]">Primary Customer Segment</Label>
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5">
                {CUSTOMER_SEGMENTS.map((seg) => (
                  <button
                    key={seg}
                    type="button"
                    onClick={() => setCustomerSegment(seg)}
                    className={cn(
                      "p-3 rounded-2xl text-xs font-medium text-left border transition-all duration-150",
                      customerSegment === seg
                        ? "bg-[#EFC7CD]/40 text-[#7A3E46] border-[#D98B95] shadow-[0_4px_16px_rgba(217,139,149,0.2)] font-semibold"
                        : "bg-[#FFF9F6] text-[#3D2A2D] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                    )}
                  >
                    {seg}
                  </button>
                ))}
              </div>
            </div>

            {/* Google Maps Competitor Radius */}
            <div className="space-y-2 pt-2 border-t border-[#E8D7D0]/60">
              <div className="flex justify-between items-center">
                <Label className="text-xs font-semibold text-[#3D2A2D]">Google Maps Search Radius</Label>
                <span className="text-xs text-[#7A3E46] font-serif font-bold">{searchRadiusKm} km</span>
              </div>
              <div className="flex flex-wrap gap-2 pt-1">
                {RADIUS_OPTIONS.map((r) => (
                  <button
                    key={r}
                    type="button"
                    onClick={() => setSearchRadiusKm(r)}
                    className={cn(
                      "px-3 py-1.5 rounded-full text-xs font-semibold transition-all border",
                      searchRadiusKm === r
                        ? "bg-[#D98B95] text-white border-[#D98B95] shadow-xs"
                        : "bg-[#FFF9F6] text-[#7A666A] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                    )}
                  >
                    {r} km
                  </button>
                ))}
              </div>
              <p className="text-[11px] text-[#7A666A]">
                Google Places Nearby Search queries establishments within this radius and computes competitor saturation.
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Buttons: Save Changes, Reset to Original, Back to Overview */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleReset}
            disabled={isSaving}
            className="text-xs h-10 px-4 rounded-[18px] border-[#E8D7D0] text-[#7A666A] hover:text-[#3D2A2D]"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Reset to Original
          </Button>

          <div className="flex items-center gap-2.5">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => navigate('/dashboard/overview')}
              disabled={isSaving}
              className="text-xs h-10 px-4 rounded-[18px] border-[#E8D7D0] text-[#3D2A2D]"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
              Back
            </Button>

            <Button
              type="submit"
              size="sm"
              disabled={isSaving}
              className="text-xs h-10 px-6 rounded-[18px] bg-gradient-to-r from-[#D98B95] to-[#7A3E46] hover:opacity-95 text-white font-semibold shadow-[0_6px_18px_rgba(217,139,149,0.3)] gap-1.5"
            >
              {isSaving ? (
                <>
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  Saving Changes...
                </>
              ) : (
                <>
                  <Save className="w-3.5 h-3.5" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        </div>
      </form>
    </div>
  )
}
