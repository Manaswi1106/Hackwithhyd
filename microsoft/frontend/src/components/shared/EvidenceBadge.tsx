import { EvidenceType } from '@/types'
import { cn } from '@/lib/utils'

interface EvidenceBadgeProps {
  type?: EvidenceType | 'high_confidence'
  className?: string
}

const badgeStyles: Record<string, string> = {
  observed: 'bg-[#E8F0EA] text-[#2E5A36] border-[#D4E2D7]',
  inferred: 'bg-[#F5E8F8] text-[#7A3E8C] border-[#E8D1ED]',
  modeled: 'bg-[#F0EBF8] text-[#5E418C] border-[#DDD4EE]',
  simulated: 'bg-[#FBEFE8] text-[#8C502E] border-[#F2D8C9]',
  high_confidence: 'bg-[#E6F4EA] text-[#1E653A] border-[#C6E7D0]',
}

const badgeLabels: Record<string, string> = {
  observed: 'OBSERVED',
  inferred: 'AI INFERRED',
  modeled: 'MODELED',
  simulated: 'HINDSIGHT',
  high_confidence: 'HIGH CONFIDENCE',
}

export function EvidenceBadge({
  type = 'observed',
  className = '',
}: EvidenceBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-[10px] font-semibold tracking-wider transition-colors',
        badgeStyles[type] || badgeStyles.observed,
        className
      )}
    >
      {badgeLabels[type] || 'OBSERVED'}
    </span>
  )
}