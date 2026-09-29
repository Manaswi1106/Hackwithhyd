// ============================================
// CORE TYPES — VentureScope Platform
// ============================================

// Evidence classification
export type EvidenceType = 'observed' | 'inferred' | 'modeled' | 'simulated'
export type ConfidenceLevel = 'high' | 'medium' | 'low' | 'insufficient'
export type Scenario = 'optimistic' | 'expected' | 'pessimistic'

// Base interfaces
export interface EvidenceSource {
  id: string
  url?: string
  name: string
  retrievedAt: string
  evidenceType: EvidenceType
  confidence: ConfidenceLevel
}

export interface EvidencedMetric<T = number> {
  value: T
  source?: EvidenceSource
  confidence: ConfidenceLevel
  evidenceType: EvidenceType
  timestamp: string
  assumptions?: string[]
}

// Category system
export interface Category {
  id: string
  name: string
  icon: string
  subcategories: Subcategory[]
}

export interface Subcategory {
  id: string
  name: string
  categoryId: string
}

// Market
export interface Market {
  id: string
  cityId: string
  cityName: string
  categoryId: string
  subcategoryId: string
  categoryName: string
  subcategoryName: string
  createdAt: string
}

// Venture
export interface Venture {
  id: string
  userId: string
  name: string
  description?: string
  url?: string
  marketId: string
  createdAt: string
}

// Competitor
export interface Competitor {
  id: string
  name: string
  category: string
  priceRange: { min: number; max: number }
  positioning: 'budget' | 'mid-range' | 'premium' | 'luxury'
  targetAudience: string[]
  customerSegments: string[]
  majorLocations: string[]
  popularProducts: string[]
  evidenceType: EvidenceType
  source?: EvidenceSource
  mapPosition?: { x: number; y: number } // for positioning map
}

// Location Intelligence
export interface LocationMetrics {
  locationId: string
  name: string
  lat: number
  lng: number
  competitorDensity: EvidencedMetric
  customerConcentration: EvidencedMetric
  demandSignal: EvidencedMetric
  averagePrice: EvidencedMetric
  opportunitySignal: EvidencedMetric
  targetAudience: string[]
  observedActivity: EvidencedMetric<string>
}

// Market Pulse
export interface MarketPulse {
  demandTrend: EvidencedMetric<'increasing' | 'stable' | 'decreasing'>
  competitionTrend: EvidencedMetric<'increasing' | 'stable' | 'decreasing'>
  averagePrice: EvidencedMetric
  searchTrend: EvidencedMetric<'increasing' | 'stable' | 'decreasing'>
  marketGrowthSignal: EvidencedMetric<'strong' | 'moderate' | 'weak'>
}

// Trajectory
export interface TrajectoryPoint {
  month: number
  demand: number
  competition: number
  averagePrice: number
  customerGrowth: number
  opportunitySignal: number
}

export interface MarketTrajectory {
  optimistic: TrajectoryPoint[]
  expected: TrajectoryPoint[]
  pessimistic: TrajectoryPoint[]
  assumptions: Record<string, string>
  drivers: TrajectoryDriver[]
}

export interface TrajectoryDriver {
  name: string
  direction: 'increasing' | 'stable' | 'decreasing'
  impact: 'high' | 'medium' | 'low'
  explanation: string
}

// Customer Segment
export interface CustomerSegment {
  id: string
  name: string
  icon: string
  demandSignal: EvidencedMetric<'high' | 'medium' | 'low'>
  typicalSpend: EvidencedMetric
  priceSensitivity: EvidencedMetric<'high' | 'medium' | 'low'>
  purchaseFrequency: EvidencedMetric<string>
  preferences: string[]
  motivations: string[]
  objections: string[]
  discoveryChannels: string[]
  purchaseTriggers: string[]
  repeatPurchaseSignal: EvidencedMetric<'high' | 'medium' | 'low'>
}

// Venture X-Ray
export interface VentureXRay {
  businessModel: EvidencedMetric<string>
  product: EvidencedMetric<string>
  price: EvidencedMetric<string>
  targetAudience: EvidencedMetric<string>
  positioning: EvidencedMetric<string>
  differentiators: string[]
  competitiveOverlap: string[]
  strengthSignals: string[]
  riskSignals: string[]
}

// Simulation
export interface SimulationAssumptions {
  deploymentModel: 'online' | 'physical' | 'hybrid' | 'multi-location'
  targetLocation?: string
  monthlyCustomers: number
  customerAcquisitionCost: number
  averageOrderValue: number
  purchaseFrequency: number
  retentionRate: number
  operatingCostMonthly: number
  marketingBudgetMonthly: number
  grossMarginPercent: number
  investmentAmount: number
}

export interface SimulationResult {
  scenario: Scenario
  months: SimulationMonth[]
  breakEvenMonth: number | null
  totalInvestmentRequired: number
  recoveryMonth: number | null
  finalMonthMetrics: MonthlyMetrics
}

export interface SimulationMonth {
  month: number
  customers: number
  revenue: number
  costs: number
  profit: number
  cumulativeProfit: number
  cumulativeInvestment: number
}

export interface MonthlyMetrics {
  customers: number
  revenue: number
  cac: number
  operatingCosts: number
  marketingCosts: number
  grossMargin: number
  netMargin: number
  burn: number
  runway: number
}

// Market Gaps
export interface MarketGap {
  id: string
  type: 'price' | 'customer' | 'feature' | 'geographic' | 'product' | 'positioning' | 'distribution'
  title: string
  description: string
  demandLevel: EvidencedMetric<'high' | 'medium' | 'low'>
  competitionLevel: EvidencedMetric<'high' | 'medium' | 'low'>
  evidence: EvidenceSource[]
  potentialOpportunity: string
}

// Hindsight - What Changed
export interface HindsightChange {
  field: string
  previousValue: string | number
  currentValue: string | number
  changeType: 'increase' | 'decrease' | 'new' | 'removed' | 'updated'
  timestamp: string
  significance: 'high' | 'medium' | 'low'
}

export interface HindsightContext {
  ventureId: string
  previousAnalysisId?: string
  currentAnalysisId: string
  changes: HindsightChange[]
  summary: string
  previousAnalysisDate?: string
  currentAnalysisDate: string
}

// Analysis Run
export interface AnalysisRun {
  id: string
  ventureId: string
  marketId: string
  status: 'pending' | 'researching' | 'analyzing' | 'simulating' | 'complete' | 'error'
  progress: number
  stages: AnalysisStage[]
  createdAt: string
  completedAt?: string
}

export interface AnalysisStage {
  name: string
  status: 'pending' | 'running' | 'complete' | 'error'
  description: string
}

// Map data
export interface MapHeatmapData {
  locations: LocationMetrics[]
  bounds: {
    north: number
    south: number
    east: number
    west: number
  }
  defaultCenter: { lat: number; lng: number }
  defaultZoom: number
}

export type MapLayer = 'opportunity' | 'competition' | 'demand' | 'price' | 'customers'

// ============================================
// VENTURE CLASSIFICATION & INTERVENTION TYPES
// ============================================

export interface DomainClassification {
  primary_domain: string
  primary_domain_name: string
  confidence: number
  confidence_label: 'high' | 'medium' | 'low' | 'insufficient'
  sub_domain: string
  supporting_evidence: string[]
  secondary_domains: Array<{
    domain: string
    name: string
    score: number
    evidence: string[]
  }>
  user_category?: string
  user_category_compatible: boolean
  mismatch_explanation: string
}

export interface DomainRecommendation {
  id: string
  title: string
  description: string
  domain: string
  category: 'growth' | 'retention' | 'pricing' | 'operations' | 'marketing'
  expected_impact: string
  effort: 'low' | 'medium' | 'high'
  evidence_basis: 'observed' | 'inferred' | 'modeled'
  simulation_params?: Record<string, number>
  rationale?: string
}

export interface InterventionComparison {
  month_12_revenue: {
    before: number
    after: number
    delta: number
    delta_pct: number
  }
  month_12_profit: {
    before: number
    after: number
    delta: number
  }
  month_12_customers: {
    before: number
    after: number
    delta: number
  }
  break_even_month: {
    before: number | null
    after: number | null
  }
}

export interface InterventionResult {
  success: boolean
  recommendation: DomainRecommendation
  changes_applied: Array<{
    parameter: string
    old_value: number
    new_value: number
    change_type: string
    delta: string
  }>
  comparison: InterventionComparison
  impact_summary: string
  before_trajectory: Array<{ month: number; revenue: number; profit: number; customers: number }>
  after_trajectory: Array<{ month: number; revenue: number; profit: number; customers: number }>
}

export interface WebsiteEvidenceSummary {
  pages_crawled: number
  pages_attempted: number
  domain: string
  brand_name: string
  brand_name_confidence: string
  has_ecommerce: boolean
  has_pricing_page: boolean
  business_model_signals: string[]
  detected_products_count: number
  detected_pricing_count: number
  schema_org_types: string[]
  errors: string[]
}

export interface SWOTItem {
  title: string
  evidence: string
  source: string
  classification: 'observed' | 'inferred' | 'modeled' | 'unknown'
  confidence: 'high' | 'medium' | 'low' | 'insufficient'
}

export interface VentureSWOT {
  strengths: SWOTItem[]
  weaknesses: SWOTItem[]
  opportunities: SWOTItem[]
  risks: SWOTItem[]
}

export interface MarketFitDimension {
  dimension: string
  score: number
  rating: string
  rationale: string
  classification: 'observed' | 'inferred' | 'modeled' | 'unknown'
  confidence?: 'high' | 'medium' | 'low' | 'insufficient'
}

export interface VentureMarketFit {
  customer_fit: MarketFitDimension
  price_fit: MarketFitDimension
  location_fit: MarketFitDimension
  competitive_pressure: MarketFitDimension
  demand_fit: MarketFitDimension
}


