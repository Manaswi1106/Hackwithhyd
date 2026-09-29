/**
 * Dynamic Dataset Reference
 * All locality data is now loaded live from the backend API (/api/context, /api/markets).
 * Zero hardcoded locality metrics or coordinates in frontend.
 */

export interface LocalityDetail {
  id: string
  name: string
  lat: number
  lng: number
  signal_score: number
  opportunity_level: string
  demand_signal: string
  competition_signal: string
  spending_power: string
  competitor_count: number
  competitor_density_per_sqkm: number
  average_price: number
  median_price: number
  price_range: { min: number; median: number; max: number }
  target_audience: string[]
  working_professional_pct: number
  student_pct: number
  business_density: string
  observed_activity: string
  reasoning: string
}

export const CALIBRATED_LOCALITIES: LocalityDetail[] = []
