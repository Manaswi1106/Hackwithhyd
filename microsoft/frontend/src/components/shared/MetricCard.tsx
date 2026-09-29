import { EvidenceType } from '@/types'
import { cn } from '@/lib/utils'
import { EvidenceBadge } from './EvidenceBadge'
import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  trend?: 'up' | 'down' | 'stable'
  trendValue?: string
  evidenceType?: EvidenceType
  icon?: React.ReactNode
  className?: string
}

export function MetricCard({ title, value, subtitle, trend, trendValue, evidenceType, className }: MetricCardProps) {
  return (
    <div className={cn('space-y-1.5 flex flex-col justify-between', className)}>
      <div className="flex items-center justify-between gap-1.5">
        <p className="text-[11px] font-semibold tracking-wide text-[#7A666A] uppercase">{title}</p>
        {evidenceType && <EvidenceBadge type={evidenceType} />}
      </div>
      <p className="text-xl font-bold font-serif tabular-nums text-[#3D2A2D] tracking-tight">{value}</p>
      {(trend || subtitle) && (
        <div className="flex items-center gap-1.5 text-[11px]">
          {trend && (
            <span className={cn(
              'flex items-center gap-0.5 font-medium',
              trend === 'up' && 'text-[#2E5A36]',
              trend === 'down' && 'text-[#9A3B45]',
              trend === 'stable' && 'text-[#7A666A]',
            )}>
              {trend === 'up' && <TrendingUp className="h-3 w-3 text-[#2E5A36]" />}
              {trend === 'down' && <TrendingDown className="h-3 w-3 text-[#9A3B45]" />}
              {trend === 'stable' && <Minus className="h-3 w-3 text-[#7A666A]" />}
              {trendValue}
            </span>
          )}
          {subtitle && <span className="text-[11px] text-[#7A666A]">{subtitle}</span>}
        </div>
      )}
    </div>
  )
}
