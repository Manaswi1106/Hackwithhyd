import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Brain, History, Sparkles, TrendingUp, CheckCircle2, Plus, Clock, ArrowRight, RefreshCw, AlertCircle } from 'lucide-react'
import { api } from '@/services/api'

interface MemoryItem {
  id: string
  business_category: string
  chosen_locality: string
  predicted_revenue: number
  actual_revenue: number
  customer_segment: string
  investment: number
  success_or_failure: string
  strategic_lesson: string
  timestamp: string
}

export default function MemoryTimeline() {
  const [memories, setMemories] = useState<MemoryItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isRetaining, setIsRetaining] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)

  // New Memory Form State
  const [newCategory, setNewCategory] = useState('Specialty Coffee')
  const [newLocality, setNewLocality] = useState('Financial District')
  const [newSegment, setNewSegment] = useState('Corporate Executives')
  const [newPredicted, setNewPredicted] = useState(1100000)
  const [newActual, setNewActual] = useState(1320000)
  const [newLesson, setNewLesson] = useState('WaveRock tech campus proximity increased morning express espresso orders by 24%.')

  const fetchMemories = async () => {
    setIsLoading(true)
    try {
      const res = await api.getHindsightExperiences()
      if (res?.success && Array.isArray(res?.data)) {
        setMemories(res.data)
      }
    } catch (e) {
      console.warn('Failed to load memories:', e)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchMemories()
  }, [])

  const handleRetain = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsRetaining(true)
    try {
      const res = await api.retainSimulationExperience({
        business_category: newCategory,
        chosen_locality: newLocality,
        customer_segment: newSegment,
        predicted_revenue: Number(newPredicted),
        actual_revenue: Number(newActual),
        investment: 3000000,
        success_or_failure: newActual >= newPredicted ? 'Success (+20% lift)' : 'Below Target',
        strategic_lesson: newLesson,
      })
      if (res?.success) {
        setShowAddForm(false)
        await fetchMemories()
      }
    } catch (err) {
      console.error('Retention error:', err)
    } finally {
      setIsRetaining(false)
    }
  }

  return (
    <div className="space-y-6 text-[#3D2A2D]">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2.5">
            <h2 className="text-2xl font-serif font-bold tracking-tight text-[#3D2A2D] flex items-center gap-2">
              <Brain className="w-5 h-5 text-[#D98B95]" />
              Hindsight Continuous Memory Timeline
            </h2>
            <Badge variant="outline" className="bg-[#FBEFE8] text-[#8C502E] border-[#F2D8C9] rounded-full px-2.5 font-semibold text-xs">
              Live Retain + Recall
            </Badge>
          </div>
          <p className="text-xs text-[#7A666A] mt-1">
            Every simulation experience is retained into memory and modifies future location rankings.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchMemories}
            className="text-xs h-9 px-3.5 rounded-full border border-[#E8D7D0] bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#7A3E46] gap-1.5 shadow-xs"
            disabled={isLoading}
          >
            <RefreshCw className={`w-3.5 h-3.5 text-[#D98B95] ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>

          <Button
            size="sm"
            onClick={() => setShowAddForm(!showAddForm)}
            className="text-xs h-9 px-4 rounded-full gap-2 bg-[#7A3E46] hover:bg-[#5A2C32] text-white shadow-[0_4px_14px_rgba(122,62,70,0.2)] font-semibold transition-all"
          >
            <Plus className="w-3.5 h-3.5 text-[#EFC7CD]" />
            Retain Experience
          </Button>
        </div>
      </div>

      {/* Memory Intelligence Architecture Banner */}
      <div className="p-4 rounded-2xl bg-[#FBEFE8] border border-[#F2D8C9] text-xs text-[#8C502E] flex items-start gap-3 shadow-[0_4px_14px_rgba(140,80,46,0.06)]">
        <Sparkles className="w-4 h-4 text-[#8C502E] mt-0.5 shrink-0" />
        <div>
          <p className="font-serif font-bold text-sm text-[#8C502E]">Continuous Learning in Action</p>
          <p className="mt-1 text-[#784325] leading-relaxed">
            Hindsight performs semantic recall across past venture simulations. When similar category patterns are detected (e.g., IT corridor coffee outlets achieving +18% revenue lift), the Market Intelligence Engine dynamically modifies location suitability scores in real time.
          </p>
        </div>
      </div>

      {/* Retention Form Modal / Expandable Card */}
      {showAddForm && (
        <Card className="border-[#D98B95] bg-[#FFF9F6] rounded-[28px] shadow-[0_12px_36px_rgba(217,139,149,0.15)] overflow-hidden">
          <CardHeader className="pb-3 border-b border-[#E8D7D0]/60 bg-[#F8F2EC]/30">
            <CardTitle className="text-sm font-serif font-bold text-[#3D2A2D] flex items-center gap-2">
              <Plus className="w-4 h-4 text-[#D98B95]" />
              Retain Simulation Experience into Hindsight
            </CardTitle>
            <CardDescription className="text-xs text-[#7A666A]">
              Simulate an entrepreneur completing a venture cycle and persisting strategic lessons to benefit future users.
            </CardDescription>
          </CardHeader>
          <CardContent className="p-6">
            <form onSubmit={handleRetain} className="space-y-4">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3.5">
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-[#3D2A2D]">Business Category</Label>
                  <Input
                    className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                    value={newCategory}
                    onChange={(e) => setNewCategory(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-[#3D2A2D]">Locality</Label>
                  <Input
                    className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                    value={newLocality}
                    onChange={(e) => setNewLocality(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-[#3D2A2D]">Customer Segment</Label>
                  <Input
                    className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                    value={newSegment}
                    onChange={(e) => setNewSegment(e.target.value)}
                    required
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-[#3D2A2D]">Predicted Monthly Revenue (₹)</Label>
                  <Input
                    type="number"
                    className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                    value={newPredicted}
                    onChange={(e) => setNewPredicted(Number(e.target.value))}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-xs font-semibold text-[#3D2A2D]">Actual Realized Revenue (₹)</Label>
                  <Input
                    type="number"
                    className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                    value={newActual}
                    onChange={(e) => setNewActual(Number(e.target.value))}
                    required
                  />
                </div>
              </div>

              <div className="space-y-1.5">
                <Label className="text-xs font-semibold text-[#3D2A2D]">Strategic Lesson Learned</Label>
                <Input
                  className="text-xs h-10 rounded-[18px] border-[#E8D7D0] bg-[#FFF9F6] text-[#3D2A2D] focus:border-[#D98B95]"
                  value={newLesson}
                  onChange={(e) => setNewLesson(e.target.value)}
                  placeholder="e.g. Higher parking scores correlated with +15% evening check sizes."
                  required
                />
              </div>

              <div className="flex justify-end gap-2.5 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  className="text-xs h-9 px-4 rounded-full border-[#E8D7D0] text-[#7A666A]"
                  onClick={() => setShowAddForm(false)}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  className="text-xs h-9 px-5 rounded-full bg-[#7A3E46] hover:bg-[#5A2C32] text-white font-semibold shadow-xs"
                  disabled={isRetaining}
                >
                  {isRetaining ? 'Retaining to Hindsight...' : 'Commit to Memory'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      {/* Empty State when zero memories */}
      {memories.length === 0 && !isLoading && (
        <Card className="p-10 text-center border-dashed border-[#E8D7D0] bg-[#FFF9F6] rounded-[28px]">
          <Brain className="w-10 h-10 text-[#D98B95] mx-auto mb-2 opacity-60" />
          <h3 className="text-base font-serif font-bold text-[#3D2A2D]">Zero Retained Memories</h3>
          <p className="text-xs text-[#7A666A] mt-1.5 max-w-sm mx-auto leading-relaxed">
            No simulation experiences have been retained yet. Run a What-If simulation and click &quot;Save to Hindsight&quot; or click &quot;Retain Experience&quot; above to persist verified business outcomes.
          </p>
        </Card>
      )}

      {/* Chronological Timeline Stream with Luxury Rose Connector */}
      <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-[#E8D7D0]">
        {memories.map((mem, idx) => {
          const variance = mem.predicted_revenue > 0
            ? Math.round(((mem.actual_revenue - mem.predicted_revenue) / mem.predicted_revenue) * 100)
            : 0

          const isPositive = variance >= 0

          return (
            <div key={mem.id || idx} className="relative group">
              {/* Timeline Marker Pin */}
              <div className="absolute -left-6 top-4 w-4 h-4 rounded-full bg-[#FFF9F6] border-2 border-[#D98B95] group-hover:bg-[#D98B95] group-hover:border-[#7A3E46] transition-colors shadow-xs" />

              <Card className="border-[#E8D7D0] bg-[#FFF9F6] rounded-2xl shadow-[0_4px_14px_rgba(122,62,70,0.04)] hover:shadow-[0_8px_24px_rgba(122,62,70,0.08)] hover:border-[#D98B95] transition-all duration-200">
                <CardContent className="py-4 px-5">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-[#E8D7D0]/60 pb-3 mb-3">
                    <div className="flex items-center gap-2">
                      <span className="font-serif font-bold text-sm text-[#3D2A2D]">
                        {mem.business_category}
                      </span>
                      <span className="text-[#E8D7D0]">·</span>
                      <span className="text-xs font-semibold text-[#7A3E46]">
                        {mem.chosen_locality}
                      </span>
                      <Badge variant="outline" className="text-[10px] ml-1 bg-[#F8F2EC] text-[#7A666A] border-[#E8D7D0] rounded-full px-2">
                        {mem.customer_segment}
                      </Badge>
                    </div>

                    <div className="flex items-center gap-1.5 text-[11px] text-[#7A666A]">
                      <Clock className="w-3 h-3 text-[#D98B95]" />
                      <span>{mem.timestamp ? new Date(mem.timestamp).toLocaleDateString() : 'Recent'}</span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs mb-3 bg-[#F8F2EC]/50 p-3 rounded-xl border border-[#E8D7D0]/60">
                    <div>
                      <span className="text-[#7A666A] block text-[10px] uppercase font-semibold">Predicted Rev</span>
                      <span className="font-semibold text-[#3D2A2D]">
                        ₹{(mem.predicted_revenue / 100000).toFixed(1)}L/mo
                      </span>
                    </div>
                    <div>
                      <span className="text-[#7A666A] block text-[10px] uppercase font-semibold">Actual Rev</span>
                      <span className="font-serif font-bold text-[#3D2A2D]">
                        ₹{(mem.actual_revenue / 100000).toFixed(1)}L/mo
                      </span>
                    </div>
                    <div>
                      <span className="text-[#7A666A] block text-[10px] uppercase font-semibold">Performance</span>
                      <span className={`font-semibold ${isPositive ? 'text-[#2E5A36]' : 'text-[#9A3B45]'}`}>
                        {isPositive ? `+${variance}% Lift` : `${variance}% Variance`}
                      </span>
                    </div>
                    <div>
                      <span className="text-[#7A666A] block text-[10px] uppercase font-semibold">Outcome</span>
                      <span className="font-medium text-[#3D2A2D]">
                        {mem.success_or_failure || 'Validated'}
                      </span>
                    </div>
                  </div>

                  {/* Strategic Lesson Callout */}
                  <div className="flex items-start gap-2.5 text-xs bg-[#F8E8EA] border border-[#EFC7CD] p-3 rounded-xl text-[#7A3E46]">
                    <Sparkles className="w-3.5 h-3.5 text-[#D98B95] mt-0.5 shrink-0" />
                    <div className="leading-relaxed">
                      <span className="font-semibold text-[#7A3E46] mr-1.5">Strategic Lesson:</span>
                      <span>{mem.strategic_lesson}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          )
        })}
      </div>
    </div>
  )
}
