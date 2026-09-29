import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import {
  Store, MapPin, Globe, Sparkles, Compass, ShieldCheck,
  RotateCcw, XCircle, Save, ArrowRight, Loader2, AlertCircle, CheckCircle2,
  UtensilsCrossed, Shirt, HeartPulse, Landmark, Laptop, ShoppingBag, GraduationCap
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { api } from '@/services/api'

export interface DomainDefinition {
  id: string
  name: string
  icon: any
  subcategories: string[]
}

export const BUSINESS_DOMAINS: DomainDefinition[] = [
  {
    id: 'Food & Beverage',
    name: 'Food & Beverage',
    icon: UtensilsCrossed,
    subcategories: [
      'Casual Dining',
      'Specialty Coffee',
      'Café & Bakery',
      'Quick Service Restaurant',
      'Cloud Kitchen',
      'Fine Dining'
    ]
  },
  {
    id: 'Fashion',
    name: 'Fashion & Apparel',
    icon: Shirt,
    subcategories: [
      'Apparel & Clothing',
      'Footwear',
      'Luxury Fashion',
      'Jewelry & Accessories',
      'Athleisure'
    ]
  },
  {
    id: 'Healthcare',
    name: 'Healthcare & Wellness',
    icon: HeartPulse,
    subcategories: [
      'Clinic & Consultations',
      'Pharmacy & Medical',
      'Salon & Spa',
      'Fitness & Gym',
      'Diagnostic Center'
    ]
  },
  {
    id: 'Fintech',
    name: 'Fintech & Financial',
    icon: Landmark,
    subcategories: [
      'WealthTech & Brokerage',
      'Digital Payments',
      'Lending & Banking',
      'Insurance & Advisory'
    ]
  },
  {
    id: 'SaaS',
    name: 'SaaS & Technology',
    icon: Laptop,
    subcategories: [
      'B2B SaaS',
      'Enterprise Software',
      'Cloud & DevTools',
      'AI & Data Platforms'
    ]
  },
  {
    id: 'Education',
    name: 'Education & EdTech',
    icon: GraduationCap,
    subcategories: [
      'EdTech & Online Learning',
      'Coaching & Test Prep',
      'K-12 Tutoring',
      'Skill Training & Academy',
      'Language & Arts School'
    ]
  },
  {
    id: 'Retail',
    name: 'Retail & Consumer',
    icon: ShoppingBag,
    subcategories: [
      'Supermarket & Grocery',
      'Electronics & Appliances',
      'Home Decor & Furnishing',
      'Books & Stationery'
    ]
  }
]

const CUSTOMER_SEGMENTS = [
  'Tech Professionals',
  'Corporate Executives',
  'Students',
  'Families',
  'Luxury Buyers',
  'Transit Commuters'
]

export const checkDomainCompatibility = (
  selectedDomain: string,
  selectedCategory: string,
  detectedDomain: string,
  detectedSubdomain: string
): { isMatch: boolean; message?: string } => {
  const sel = `${selectedDomain} ${selectedCategory}`.toLowerCase()
  const det = `${detectedDomain} ${detectedSubdomain}`.toLowerCase()

  const isFoodSel = /food|beverage|dining|restaurant|cafe|coffee|cloud kitchen|barbecue|grill|bakery|qsr/.test(sel)
  const isFashionSel = /fashion|apparel|clothing|wear|footwear|shoe|jewelry|accessory|lifestyle/.test(sel)
  const isHealthSel = /health|clinic|medical|pharma|wellness|salon|spa|doctor|fitness/.test(sel)
  const isFintechSel = /fintech|finance|wealth|broker|invest|bank|payment/.test(sel)
  const isSaasSel = /saas|software|tech|cloud|b2b|devtools/.test(sel)
  const isRetailSel = /retail|supermarket|grocery|store|electronics|home/.test(sel)

  const isFoodDet = /food|beverage|dining|restaurant|cafe|coffee|cloud kitchen|barbecue|grill|bakery|qsr/.test(det)
  const isFashionDet = /fashion|apparel|clothing|wear|footwear|shoe|jewelry|accessory|lifestyle/.test(det)
  const isHealthDet = /health|clinic|medical|pharma|wellness|salon|spa|doctor|fitness/.test(det)
  const isFintechDet = /fintech|finance|wealth|broker|invest|bank|payment/.test(det)
  const isSaasDet = /saas|software|tech|cloud|b2b|devtools/.test(det)
  const isRetailDet = /retail|supermarket|grocery|store|electronics|home/.test(det)

  let matched = true
  if (isFoodSel) matched = isFoodDet
  else if (isFashionSel) matched = isFashionDet
  else if (isHealthSel) matched = isHealthDet
  else if (isFintechSel) matched = isFintechDet
  else if (isSaasSel) matched = isSaasDet
  else if (isRetailSel) matched = isRetailDet

  if (!matched) {
    return {
      isMatch: false,
      message: `Website evidence indicates a ${detectedDomain} (${detectedSubdomain}) venture, but selected category is '${selectedCategory}'. Please adjust your category or verify your URL.`
    }
  }

  return { isMatch: true }
}

export default function Setup() {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const isEditMode = searchParams.get('edit') === 'true'

  // Loading & State
  const [isLoadingContext, setIsLoadingContext] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  // Original snapshot for Reset
  const [originalSnapshot, setOriginalSnapshot] = useState<any>(null)

  // Mandatory Business Fields
  const [ventureName, setVentureName] = useState('')
  const [selectedDomain, setSelectedDomain] = useState<string>('Food & Beverage')
  const [selectedCategory, setSelectedCategory] = useState<string>('Casual Dining')
  const [currentLocation, setCurrentLocation] = useState('')
  const [latitude, setLatitude] = useState<number | null>(null)
  const [longitude, setLongitude] = useState<number | null>(null)
  const [monthlyRent, setMonthlyRent] = useState<string>('')
  const [storeSize, setStoreSize] = useState<string>('')
  const [customerSegment, setCustomerSegment] = useState<string>('')
  const [websiteUrl, setWebsiteUrl] = useState('')

  // Geolocation state
  const [isDetectingLocation, setIsDetectingLocation] = useState(false)

  // AI Website Intelligence state
  const [isAnalyzingUrl, setIsAnalyzingUrl] = useState(false)
  const [extractedDna, setExtractedDna] = useState<any>(null)
  const [domainMismatchWarning, setDomainMismatchWarning] = useState<string | null>(null)
  const [domainVerifiedNotice, setDomainVerifiedNotice] = useState<string | null>(null)

  // Subcategories available for active domain
  const activeDomainDef = BUSINESS_DOMAINS.find(d => d.id === selectedDomain) || BUSINESS_DOMAINS[0]

  // Switch domain and automatically select first subcategory
  const handleDomainChange = (domainId: string) => {
    setSelectedDomain(domainId)
    const def = BUSINESS_DOMAINS.find(d => d.id === domainId)
    if (def && def.subcategories.length > 0) {
      const newCat = def.subcategories[0]
      setSelectedCategory(newCat)
      // If we already extracted DNA, re-check compatibility immediately
      if (extractedDna) {
        recheckDnaMatch(domainId, newCat, extractedDna)
      }
    }
  }

  // Handle Category selection
  const handleCategoryChange = (category: string) => {
    setSelectedCategory(category)
    if (extractedDna) {
      recheckDnaMatch(selectedDomain, category, extractedDna)
    }
  }

  const recheckDnaMatch = (dom: string, cat: string, dna: any) => {
    const detDom = dna.primary_domain || dna.domain || 'Commercial'
    const detSub = dna.subdomain || dna.category || 'Retail'
    const check = checkDomainCompatibility(dom, cat, detDom, detSub)
    if (check.isMatch) {
      setDomainMismatchWarning(null)
      setDomainVerifiedNotice(`✓ Domain verified: Website DNA matches '${dom}' · Detected: ${dna.brand || 'Brand'} (${detSub})`)
    } else {
      setDomainVerifiedNotice(null)
      setDomainMismatchWarning(check.message || `Website evidence indicates ${detDom}, but selected category is '${cat}'.`)
    }
  }

  // Load existing context if in edit mode or already initialized
  useEffect(() => {
    const checkContext = async () => {
      setIsLoadingContext(true)
      try {
        const ctx = await api.getContext()
        if (ctx && ctx.is_initialized) {
          setOriginalSnapshot(ctx)
          if (isEditMode) {
            setVentureName(ctx.venture_name || ctx.business_name || '')
            if (ctx.domain) {
              const matchedDom = BUSINESS_DOMAINS.find(d => d.id.toLowerCase() === ctx.domain.toLowerCase())
              if (matchedDom) setSelectedDomain(matchedDom.id)
            }
            if (ctx.category) {
              setSelectedCategory(ctx.category)
            }
            setCurrentLocation(ctx.city || ctx.selected_locality || 'Hyderabad, Telangana')
            setLatitude(ctx.latitude || null)
            setLongitude(ctx.longitude || null)
            setMonthlyRent(ctx.rent ? ctx.rent.toString() : '150000')
            setStoreSize(ctx.store_size ? ctx.store_size.toString() : '1200')
            setCustomerSegment(ctx.customer_segment || 'Tech Professionals')
            setWebsiteUrl(ctx.retail_url || '')
          }
        }
      } catch (e) {
        console.warn('Error loading context for setup:', e)
      } finally {
        setIsLoadingContext(false)
      }
    }
    checkContext()
  }, [isEditMode])

  // Geolocation detection using HTML5 Geolocation and Google Geocoding API
  const handleDetectLocation = () => {
    setErrorMessage(null)
    if (!('geolocation' in navigator)) {
      setErrorMessage("Geolocation is not supported by your browser. Please enter your location manually.")
      return
    }

    setIsDetectingLocation(true)
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        try {
          const lat = pos.coords.latitude
          const lng = pos.coords.longitude
          setLatitude(lat)
          setLongitude(lng)

          const geo = await api.reverseGeocode(lat, lng)
          if (geo && geo.formatted_address) {
            setCurrentLocation(geo.formatted_address)
          } else {
            setCurrentLocation("Hyderabad, Telangana")
          }
        } catch {
          setCurrentLocation("Hyderabad, Telangana")
        } finally {
          setIsDetectingLocation(false)
        }
      },
      (err) => {
        setIsDetectingLocation(false)
        console.warn("Geolocation error:", err)
        setErrorMessage("Location access was denied. Please enter your city manually.")
      },
      { timeout: 8000, enableHighAccuracy: true }
    )
  }

  // AI Website Intelligence: Website URL -> Crawl -> Groq extracts DNA -> Compares Domain vs Category
  const handleAnalyzeWebsite = async () => {
    if (!websiteUrl.trim()) return
    setIsAnalyzingUrl(true)
    setDomainMismatchWarning(null)
    setDomainVerifiedNotice(null)
    setExtractedDna(null)
    setErrorMessage(null)

    try {
      const res = await api.classifyUrl(websiteUrl.trim(), selectedCategory, ventureName.trim())
      if (res && res.success && res.data) {
        const dna = res.data
        setExtractedDna(dna)

        // Automatically infer venture name if blank
        if (!ventureName.trim() && dna.brand) {
          setVentureName(dna.brand)
        }
        // Automatically infer customer segment if detected
        if (dna.audience) {
          const match = CUSTOMER_SEGMENTS.find(s => s.toLowerCase() === dna.audience.toLowerCase())
          if (match) setCustomerSegment(match)
        }

        // Compare detected domain vs selected category
        const detDom = dna.primary_domain || dna.domain || 'Commercial'
        const detSub = dna.subdomain || dna.category || 'Retail'
        const check = checkDomainCompatibility(selectedDomain, selectedCategory, detDom, detSub)

        if (check.isMatch) {
          setDomainVerifiedNotice(`✓ Domain verified: Website DNA matches '${selectedDomain}' · Detected: ${dna.brand || 'Brand'} (${detSub})`)
          setDomainMismatchWarning(null)
        } else {
          setDomainVerifiedNotice(null)
          // Show red validation message, DO NOT remove selected category, allow editing
          setDomainMismatchWarning(check.message || `Website evidence indicates a ${detDom} venture, but selected category is '${selectedCategory}'.`)
        }
      } else {
        setDomainVerifiedNotice(null)
        setDomainMismatchWarning(null)
        setErrorMessage(res?.message || "Insufficient website evidence.")
      }
    } catch (e: any) {
      setErrorMessage(e.message || "Website analysis failed")
    } finally {
      setIsAnalyzingUrl(false)
    }
  }

  // Handle Form Submission (Create or Update Context)
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setErrorMessage(null)
    setSuccessMessage(null)

    // Validate mandatory fields
    if (!ventureName.trim()) {
      setErrorMessage("Venture Name is required.")
      return
    }
    if (!selectedCategory.trim()) {
      setErrorMessage("Please select a Business Category.")
      return
    }
    if (!currentLocation.trim()) {
      setErrorMessage("Location is required.")
      return
    }
    if (!monthlyRent || Number(monthlyRent) <= 0) {
      setErrorMessage("Valid Monthly Rent Budget is required.")
      return
    }
    if (!storeSize || Number(storeSize) <= 0) {
      setErrorMessage("Valid Store Size in sqft is required.")
      return
    }
    if (!customerSegment) {
      setErrorMessage("Please select your primary Customer Segment.")
      return
    }

    setIsSubmitting(true)
    try {
      const rentVal = Number(monthlyRent)
      const sizeVal = Number(storeSize)

      if (isEditMode) {
        // Update existing context without recreating
        const updates: Record<string, any> = {
          venture_name: ventureName.trim(),
          domain: selectedDomain,
          category: selectedCategory,
          retail_url: websiteUrl.trim() || null,
          city: currentLocation.trim(),
          rent: rentVal,
          monthly_rent_budget: rentVal,
          store_size: sizeVal,
          customer_segment: customerSegment,
        }

        const updated = await api.updateContext(updates)
        if (updated) {
          localStorage.setItem('venturescope_setup_completed', 'true')
          setSuccessMessage("Venture setup updated successfully!")
          setTimeout(() => navigate('/dashboard/overview'), 600)
        }
      } else {
        // Initialize new venture context
        const initPayload = {
          retail_url: websiteUrl.trim() || undefined,
          venture_name: ventureName.trim(),
          category: selectedCategory,
          city: currentLocation.trim(),
          latitude: latitude || undefined,
          longitude: longitude || undefined,
          budget: rentVal * 20, // Amortized working capital proxy
          monthly_rent_budget: rentVal,
          store_size: sizeVal,
          customer_segment: customerSegment,
        }

        const state = await api.initializeContext(initPayload)
        if (state) {
          localStorage.setItem('venturescope_setup_completed', 'true')
          navigate('/dashboard/overview')
        }
      }
    } catch (e: any) {
      setErrorMessage(e.message || "Failed to save venture setup.")
    } finally {
      setIsSubmitting(false)
    }
  }

  // Cancel in Edit Mode
  const handleCancel = () => {
    navigate('/dashboard/overview')
  }

  // Reset to Original
  const handleReset = () => {
    if (originalSnapshot) {
      setVentureName(originalSnapshot.venture_name || originalSnapshot.business_name || '')
      if (originalSnapshot.domain) setSelectedDomain(originalSnapshot.domain)
      if (originalSnapshot.category) setSelectedCategory(originalSnapshot.category)
      setCurrentLocation(originalSnapshot.city || 'Hyderabad, Telangana')
      setMonthlyRent(originalSnapshot.rent ? originalSnapshot.rent.toString() : '150000')
      setStoreSize(originalSnapshot.store_size ? originalSnapshot.store_size.toString() : '1200')
      setCustomerSegment(originalSnapshot.customer_segment || 'Tech Professionals')
      setWebsiteUrl(originalSnapshot.retail_url || '')
      setExtractedDna(null)
      setDomainMismatchWarning(null)
      setDomainVerifiedNotice(null)
      setErrorMessage(null)
    }
  }

  if (isLoadingContext) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#F8F2EC]">
        <div className="flex items-center gap-2.5 text-xs text-[#7A666A]">
          <Loader2 className="w-5 h-5 animate-spin text-[#D98B95]" />
          <span className="font-serif text-sm font-medium">Loading venture profile...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-[#F8F2EC] text-[#3D2A2D] flex flex-col relative overflow-hidden selection:bg-[#EFC7CD] selection:text-[#7A3E46]">
      {/* Decorative luxury blush background orbs */}
      <div className="absolute -top-32 -left-32 w-96 h-96 rounded-full bg-[#EFC7CD]/30 blur-3xl pointer-events-none" />
      <div className="absolute top-1/2 -right-32 w-96 h-96 rounded-full bg-[#D98B95]/15 blur-3xl pointer-events-none" />

      {/* Top Header */}
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
              Retail Intelligence
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-[#E8F0EA] border border-[#D4E2D7] text-xs text-[#2E5A36] font-medium">
          <ShieldCheck className="w-3.5 h-3.5 text-[#2E5A36]" />
          <span className="text-[11px]">{isEditMode ? 'Editing Active Venture' : 'Mandatory Business Onboarding'}</span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-3xl mx-auto w-full px-4 py-10 relative z-10">
        <div className="space-y-6">
          <div className="space-y-2 text-center">
            <span className="inline-block px-3 py-1 rounded-full bg-[#F5E8F8] border border-[#E8D1ED] text-[11px] font-semibold tracking-wider text-[#7A3E8C] uppercase">
              {isEditMode ? 'Venture Calibration' : 'Step 1 of 1 · Business Architecture'}
            </span>
            <h1 className="text-3xl font-serif font-bold text-[#3D2A2D] tracking-tight">
              {isEditMode ? 'Edit Venture Parameters' : 'Configure Your Retail Business'}
            </h1>
            <p className="text-xs text-[#7A666A] max-w-lg mx-auto leading-relaxed">
              {isEditMode
                ? 'Update your venture parameters. All changes synchronize immediately across Overview, Simulation, and Google Places.'
                : 'Enter your business parameters to unlock real-time location intelligence, demographic scoring, and what-if financial projections.'}
            </p>
          </div>

          {errorMessage && (
            <div className="p-3.5 rounded-2xl bg-[#FDF0F2] border border-[#F5C2C7] text-[#9A3B45] text-xs flex items-center gap-2.5 shadow-xs">
              <AlertCircle className="w-4 h-4 shrink-0 text-[#9A3B45]" />
              <span className="font-medium">{errorMessage}</span>
            </div>
          )}

          {successMessage && (
            <div className="p-3.5 rounded-2xl bg-[#E8F0EA] border border-[#D4E2D7] text-[#2E5A36] text-xs flex items-center gap-2.5 shadow-xs">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-[#2E5A36]" />
              <span className="font-medium">{successMessage}</span>
            </div>
          )}

          <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px] shadow-[0_16px_40px_rgba(122,62,70,0.07)] overflow-hidden">
            <CardHeader className="pb-4 pt-6 px-6 sm:px-8 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-xl bg-[#EFC7CD]/50 flex items-center justify-center text-[#7A3E46]">
                  <Store className="w-4 h-4 text-[#7A3E46]" />
                </div>
                <div>
                  <CardTitle className="text-base font-serif font-bold text-[#3D2A2D]">
                    Business Parameters (Zero Hardcoding)
                  </CardTitle>
                  <CardDescription className="text-xs text-[#7A666A]">
                    All inputs feed directly into the multi-criteria location model, Google Maps API, and financial simulations.
                  </CardDescription>
                </div>
              </div>
            </CardHeader>

            <CardContent className="p-6 sm:p-8">
              <form onSubmit={handleSubmit} className="space-y-6">
                {/* 1. Venture Name */}
                <div className="space-y-1.5">
                  <Label htmlFor="vname" className="text-xs font-semibold text-[#3D2A2D]">
                    Venture Name <span className="text-[#9A3B45]">*</span>
                  </Label>
                  <Input
                    id="vname"
                    value={ventureName}
                    onChange={(e) => setVentureName(e.target.value)}
                    placeholder="e.g. Barbeque Nation, Blue Tokai, Myntra, Practo"
                    className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] px-4 focus:border-[#D98B95] focus:ring-[#D98B95]"
                    required
                  />
                </div>

                {/* 2. Business Domain & Subcategory Selection */}
                <div className="space-y-3">
                  <div>
                    <Label className="text-xs font-semibold text-[#3D2A2D]">
                      Business Domain <span className="text-[#9A3B45]">*</span>
                    </Label>
                    <p className="text-[11px] text-[#7A666A] mt-0.5">
                      Select your primary industry sector
                    </p>
                  </div>

                  {/* 7 Domain Selector Cards */}
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
                            "p-3 rounded-2xl text-xs font-medium text-left border flex items-center gap-2.5 transition-all duration-200",
                            isSelected
                              ? "bg-[#EFC7CD]/40 text-[#7A3E46] border-[#D98B95] shadow-[0_4px_16px_rgba(217,139,149,0.25)] font-semibold"
                              : "bg-[#FFF9F6] text-[#3D2A2D] border-[#E8D7D0] hover:bg-[#F8E8EA]"
                          )}
                        >
                          <Icon className={cn("w-4 h-4 shrink-0", isSelected ? "text-[#7A3E46]" : "text-[#D98B95]")} />
                          <span className="truncate">{domain.name}</span>
                        </button>
                      )
                    })}
                  </div>

                  {/* Subcategory / Specific Category Selector */}
                  <div className="space-y-2 pt-2 border-t border-[#E8D7D0]/60">
                    <Label className="text-xs font-semibold text-[#3D2A2D]">
                      Subcategory / Category <span className="text-[#9A3B45]">*</span>
                    </Label>
                    <div className="flex flex-wrap gap-2">
                      {activeDomainDef.subcategories.map((subcat) => {
                        const isCatSelected = selectedCategory === subcat
                        return (
                          <button
                            key={subcat}
                            type="button"
                            onClick={() => handleCategoryChange(subcat)}
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
                </div>

                {/* 3. Website URL (Optional) with DNA Analysis */}
                <div className="space-y-2.5 pt-1">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="wurl" className="text-xs font-semibold text-[#3D2A2D]">
                      Business Website URL (Optional)
                    </Label>
                    <span className="text-[10px] text-[#7A666A]">AI validates category consistency</span>
                  </div>
                  <div className="flex gap-2.5">
                    <div className="relative flex-1">
                      <Globe className="w-4 h-4 absolute left-3.5 top-3 text-[#7A666A]" />
                      <Input
                        id="wurl"
                        type="url"
                        value={websiteUrl}
                        onChange={(e) => setWebsiteUrl(e.target.value)}
                        placeholder="https://barbecuenation.com or https://myntra.com"
                        className="text-xs h-10 pl-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                      />
                    </div>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleAnalyzeWebsite}
                      disabled={isAnalyzingUrl || !websiteUrl.trim()}
                      className="text-xs h-10 px-4 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#7A3E46] font-semibold gap-1.5 shrink-0 shadow-xs"
                    >
                      {isAnalyzingUrl ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5 text-[#D98B95]" />}
                      Analyze DNA
                    </Button>
                  </div>

                  {/* Red Mismatch Banner */}
                  {domainMismatchWarning && (
                    <div className="p-3.5 rounded-2xl bg-[#FDF0F2] border border-[#F5C2C7] text-[#9A3B45] text-xs flex items-start gap-2.5">
                      <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                      <div className="space-y-1">
                        <span className="font-semibold">Category Mismatch Warning</span>
                        <p className="text-[11px] leading-relaxed">{domainMismatchWarning}</p>
                      </div>
                    </div>
                  )}

                  {/* Green Verified Banner */}
                  {domainVerifiedNotice && (
                    <div className="p-3 rounded-2xl bg-[#E8F0EA] border border-[#D4E2D7] text-[#2E5A36] text-xs flex items-center gap-2">
                      <CheckCircle2 className="w-4 h-4 shrink-0" />
                      <span>{domainVerifiedNotice}</span>
                    </div>
                  )}

                  {extractedDna && (
                    <div className="p-3.5 bg-[#F8F2EC]/60 rounded-2xl border border-[#E8D7D0] text-xs space-y-1.5">
                      <div className="flex items-center justify-between font-semibold text-[#3D2A2D]">
                        <span className="font-serif">{extractedDna.brand || 'Detected Venture'}</span>
                        <Badge variant="outline" className="text-[10px] rounded-full bg-[#FFF9F6] border-[#E8D7D0] text-[#7A666A]">
                          {extractedDna.primary_domain || extractedDna.domain} · {extractedDna.subdomain || extractedDna.category}
                        </Badge>
                      </div>
                      {extractedDna.products && extractedDna.products.length > 0 && (
                        <p className="text-[#7A666A] text-[11px]">
                          Key Offerings: {extractedDna.products.join(', ')}
                        </p>
                      )}
                    </div>
                  )}
                </div>

                {/* 4. Location with Auto-detect */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="loc" className="text-xs font-semibold text-[#3D2A2D]">
                      Current Location <span className="text-[#9A3B45]">*</span>
                    </Label>
                    <button
                      type="button"
                      onClick={handleDetectLocation}
                      disabled={isDetectingLocation}
                      className="text-xs text-[#7A3E46] font-semibold flex items-center gap-1 hover:underline"
                    >
                      {isDetectingLocation ? (
                        <>
                          <Loader2 className="w-3 h-3 animate-spin text-[#D98B95]" />
                          <span>Detecting GPS...</span>
                        </>
                      ) : (
                        <>
                          <MapPin className="w-3.5 h-3.5 text-[#D98B95]" />
                          <span>Use My Current Location</span>
                        </>
                      )}
                    </button>
                  </div>
                  <Input
                    id="loc"
                    value={currentLocation}
                    onChange={(e) => setCurrentLocation(e.target.value)}
                    placeholder="e.g. Hyderabad, Telangana"
                    className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] px-4 focus:border-[#D98B95]"
                    required
                  />
                </div>

                {/* 5. Monthly Rent & Store Size */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <Label htmlFor="mrent" className="text-xs font-semibold text-[#3D2A2D]">
                        Monthly Rent Budget <span className="text-[#9A3B45]">*</span>
                      </Label>
                      {monthlyRent && (
                        <span className="text-[11px] font-mono text-[#7A3E46] font-bold">
                          ₹{(Number(monthlyRent) / 100000).toFixed(2)} Lakhs
                        </span>
                      )}
                    </div>
                    <Input
                      id="mrent"
                      type="number"
                      min={10000}
                      step={5000}
                      value={monthlyRent}
                      onChange={(e) => setMonthlyRent(e.target.value)}
                      placeholder="e.g. 150000"
                      className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] px-4 focus:border-[#D98B95]"
                      required
                    />
                  </div>

                  <div className="space-y-1.5">
                    <Label htmlFor="ssize" className="text-xs font-semibold text-[#3D2A2D]">
                      Store Size (sqft) <span className="text-[#9A3B45]">*</span>
                    </Label>
                    <Input
                      id="ssize"
                      type="number"
                      min={100}
                      step={50}
                      value={storeSize}
                      onChange={(e) => setStoreSize(e.target.value)}
                      placeholder="e.g. 1200"
                      className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] px-4 focus:border-[#D98B95]"
                      required
                    />
                  </div>
                </div>

                {/* 6. Customer Segment */}
                <div className="space-y-2">
                  <Label className="text-xs font-semibold text-[#3D2A2D]">
                    Target Customer Segment <span className="text-[#9A3B45]">*</span>
                  </Label>
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

                {/* Form Buttons */}
                <div className="pt-6 border-t border-[#E8D7D0]/60 flex flex-wrap items-center justify-between gap-3">
                  {isEditMode ? (
                    <>
                      <Button
                        type="button"
                        variant="outline"
                        onClick={handleReset}
                        disabled={isSubmitting}
                        className="text-xs h-10 px-4 rounded-[18px] border-[#E8D7D0] text-[#7A666A] hover:text-[#3D2A2D] gap-1.5"
                      >
                        <RotateCcw className="w-3.5 h-3.5" />
                        Reset to Original
                      </Button>

                      <div className="flex items-center gap-2.5">
                        <Button
                          type="button"
                          variant="outline"
                          onClick={handleCancel}
                          disabled={isSubmitting}
                          className="text-xs h-10 px-4 rounded-[18px] border-[#E8D7D0] text-[#3D2A2D] gap-1.5"
                        >
                          <XCircle className="w-3.5 h-3.5" />
                          Cancel
                        </Button>

                        <Button
                          type="submit"
                          disabled={isSubmitting}
                          className="text-xs h-10 px-6 rounded-[18px] bg-gradient-to-r from-[#D98B95] to-[#7A3E46] hover:opacity-95 text-white font-semibold shadow-[0_6px_18px_rgba(217,139,149,0.3)] gap-1.5"
                        >
                          {isSubmitting ? (
                            <Loader2 className="w-3.5 h-3.5 animate-spin" />
                          ) : (
                            <Save className="w-3.5 h-3.5" />
                          )}
                          Save Changes
                        </Button>
                      </div>
                    </>
                  ) : (
                    <div className="w-full">
                      <Button
                        type="submit"
                        disabled={isSubmitting}
                        className="w-full h-12 rounded-[18px] text-xs font-semibold tracking-wide bg-gradient-to-r from-[#D98B95] to-[#7A3E46] hover:opacity-95 text-white shadow-[0_8px_24px_rgba(217,139,149,0.35)] flex items-center justify-center gap-2 transition-all active:scale-[0.99]"
                      >
                        {isSubmitting ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Calculating Location Viability & Demographic Match...
                          </>
                        ) : (
                          <>
                            <span className="text-sm font-serif">Launch VentureScope Intelligence Dashboard</span>
                            <ArrowRight className="w-4 h-4" />
                          </>
                        )}
                      </Button>
                    </div>
                  )}
                </div>
              </form>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
