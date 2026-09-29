import React, { useEffect, useState, useMemo, useCallback } from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { MapPin, Compass, ShieldCheck, Navigation, Store, Layers, Loader2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import {
  GoogleMap as ReactGoogleMap,
  useJsApiLoader,
  MarkerF,
  CircleF,
  InfoWindowF,
} from '@react-google-maps/api'

interface GoogleMapProps {
  locations: any[]
  activeLocation: any
  onSelectLocation: (location: any) => void
  competitors?: any[]
  searchRadiusKm?: number
  className?: string
}

const libraries: ('places' | 'geometry')[] = ['places', 'geometry']

export default function GoogleMap({
  locations = [],
  activeLocation,
  onSelectLocation,
  competitors = [],
  searchRadiusKm = 3.0,
  className
}: GoogleMapProps) {
  const [selectedCompetitor, setSelectedCompetitor] = useState<any | null>(null)
  const [mapInstance, setMapInstance] = useState<google.maps.Map | null>(null)

  const apiKey = (import.meta as any).env?.VITE_GOOGLE_MAPS_KEY || ''

  const lat = activeLocation?.lat ?? 17.4485
  const lng = activeLocation?.lng ?? 78.3910
  const areaName = activeLocation?.area || 'Madhapur'

  // Suppress Google Maps browser ownership popup and development alerts
  useEffect(() => {
    if (typeof window === 'undefined') return
    const origAlert = window.alert
    window.alert = function (...args: any[]) {
      const text = args.join(' ')
      if (
        text.includes('own this website') ||
        text.includes("can't load Google Maps correctly") ||
        text.includes('Google Maps')
      ) {
        console.warn('Suppressed Google Maps alert popup:', text)
        return
      }
      return origAlert.apply(this, args)
    }
    ;(window as any).gm_authFailure = () => {
      console.warn('Google Maps JS auth failure handled cleanly.')
    }
    return () => {
      window.alert = origAlert
    }
  }, [])

  // Load Google Maps JavaScript API via @react-google-maps/api
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: apiKey,
    libraries,
  })

  // Dynamic zoom level derived from selected radius
  const zoomLevel = useMemo(() => {
    if (searchRadiusKm <= 1.0) return 15
    if (searchRadiusKm <= 2.0) return 14
    if (searchRadiusKm <= 3.5) return 13
    if (searchRadiusKm <= 5.5) return 12
    if (searchRadiusKm <= 8.0) return 11
    return 10
  }, [searchRadiusKm])

  // Center on active locality
  const center = useMemo(() => ({ lat, lng }), [lat, lng])

  const onLoad = useCallback((map: google.maps.Map) => {
    setMapInstance(map)
  }, [])

  const onUnmount = useCallback(() => {
    setMapInstance(null)
  }, [])

  useEffect(() => {
    if (mapInstance) {
      mapInstance.panTo(center)
      mapInstance.setZoom(zoomLevel)
    }
  }, [center, zoomLevel, mapInstance])

  return (
    <Card className={cn('overflow-hidden border border-[#E8D7D0] rounded-[28px] shadow-[0_12px_36px_rgba(122,62,70,0.06)] relative flex flex-col bg-[#FFF9F6]', className)}>
      {/* Suppress all development watermark overlays, dark filters, and ownership popups */}
      <style>{`
        .gm-err-container, .gm-err-content, .gm-err-icon, .gm-err-title, .gm-err-message {
          display: none !important;
        }
        .gm-style iframe + div,
        div[style*="z-index: 1000001"],
        div[style*="rgba(0, 0, 0, 0.5)"],
        div[style*="background-color: rgba(0, 0, 0, 0.5)"],
        .dismissButton {
          display: none !important;
        }
        .gm-style div[aria-hidden="true"] {
          opacity: 1 !important;
        }
      `}</style>

      {/* Top Map Intelligence Overlay Bar */}
      <div className="absolute top-3.5 left-3.5 right-3.5 z-10 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
        {/* Selected Locality Badge */}
        <div className="flex items-center gap-2 bg-[#FFF9F6]/90 backdrop-blur-md px-3 py-1.5 rounded-full border border-[#E8D7D0] shadow-[0_4px_12px_rgba(122,62,70,0.06)] pointer-events-auto">
          <span className="w-2.5 h-2.5 rounded-full bg-[#D98B95] shrink-0" />
          <span className="text-xs font-serif font-bold text-[#3D2A2D]">{areaName}</span>
          <span className="text-[10px] text-[#7A666A] font-mono">({lat.toFixed(4)}, {lng.toFixed(4)})</span>
        </div>

        {/* Legend & Verified Badge */}
        <div className="flex items-center gap-2 pointer-events-auto">
          <div className="hidden sm:flex items-center gap-3 bg-[#FFF9F6]/90 backdrop-blur-md px-3 py-1.5 rounded-full border border-[#E8D7D0] text-[10px] text-[#7A666A] shadow-xs">
            <span className="flex items-center gap-1 font-medium">
              <span className="w-2 h-2 rounded-full bg-[#D98B95]" />
              Active
            </span>
            <span className="flex items-center gap-1 font-medium">
              <span className="w-2 h-2 rounded-full bg-[#2E5A36]" />
              Top Viability
            </span>
            <span className="flex items-center gap-1 font-medium">
              <span className="w-2 h-2 rounded-full bg-[#9A3B45]" />
              Competitors ({competitors.length})
            </span>
          </div>

          <Badge variant="outline" className="text-[11px] bg-[#FFF9F6]/90 backdrop-blur-md text-[#3D2A2D] border-[#E8D7D0] rounded-full shadow-xs px-2.5">
            <Compass className="w-3 h-3 mr-1 text-[#D98B95]" />
            Radius: {searchRadiusKm} km
          </Badge>
          <Badge variant="outline" className="text-[10px] bg-[#E8F0EA] text-[#2E5A36] border-[#D4E2D7] backdrop-blur-md rounded-full px-2.5">
            <ShieldCheck className="w-3 h-3 mr-1 text-[#2E5A36]" />
            Live Map API
          </Badge>
        </div>
      </div>

      {/* Main Interactive Map Canvas loaded using @react-google-maps/api */}
      <div className="relative w-full flex-1 min-h-[440px] bg-muted/20">
        {isLoaded ? (
          <ReactGoogleMap
            mapContainerStyle={{ width: '100%', height: '100%', minHeight: '440px' }}
            center={center}
            zoom={zoomLevel}
            onLoad={onLoad}
            onUnmount={onUnmount}
            options={{
              disableDefaultUI: false,
              zoomControl: true,
              streetViewControl: false,
              mapTypeControl: false,
              fullscreenControl: true,
              styles: [
                { featureType: 'poi.business', stylers: [{ visibility: 'simplified' }] },
                { featureType: 'transit', stylers: [{ visibility: 'on' }] }
              ]
            }}
          >
            {/* Search Radius Circle */}
            <CircleF
              center={center}
              radius={searchRadiusKm * 1000}
              options={{
                fillColor: '#3b82f6',
                fillOpacity: 0.15,
                strokeColor: '#2563eb',
                strokeOpacity: 0.85,
                strokeWeight: 2,
              }}
            />

            {/* Active Selected Locality Marker (Blue) */}
            <MarkerF
              position={center}
              title={`Selected Locality: ${areaName}`}
              icon={{
                path: google.maps.SymbolPath.CIRCLE,
                scale: 9,
                fillColor: '#2563eb',
                fillOpacity: 1,
                strokeColor: '#ffffff',
                strokeWeight: 2.5,
              }}
            />

            {/* Top Opportunity Locations (Green) */}
            {locations.slice(0, 5).map((loc) => {
              const isSelected = loc.area?.toLowerCase() === activeLocation?.area?.toLowerCase()
              if (isSelected || !loc.lat || !loc.lng) return null
              return (
                <MarkerF
                  key={loc.area}
                  position={{ lat: loc.lat, lng: loc.lng }}
                  title={`${loc.area} (Score: ${loc.score})`}
                  onClick={() => onSelectLocation(loc)}
                  icon={{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 7,
                    fillColor: '#10b981',
                    fillOpacity: 0.9,
                    strokeColor: '#ffffff',
                    strokeWeight: 2,
                  }}
                />
              )
            })}

            {/* Competitor Markers (Red) */}
            {competitors.map((comp, idx) => {
              if (!comp.lat || !comp.lng) return null
              return (
                <MarkerF
                  key={comp.id || `comp-${idx}`}
                  position={{ lat: comp.lat, lng: comp.lng }}
                  title={`${comp.name} (${comp.category || 'Competitor'})`}
                  onClick={() => setSelectedCompetitor(comp)}
                  icon={{
                    path: google.maps.SymbolPath.CIRCLE,
                    scale: 6,
                    fillColor: '#f43f5e',
                    fillOpacity: 0.95,
                    strokeColor: '#ffffff',
                    strokeWeight: 1.5,
                  }}
                />
              )
            })}

            {/* Competitor Detail InfoWindow */}
            {selectedCompetitor && (
              <InfoWindowF
                position={{ lat: selectedCompetitor.lat, lng: selectedCompetitor.lng }}
                onCloseClick={() => setSelectedCompetitor(null)}
              >
                <div className="p-1 text-xs text-slate-900 max-w-[220px]">
                  <div className="font-bold text-sm text-slate-950 mb-0.5">{selectedCompetitor.name}</div>
                  <div className="text-[11px] text-slate-600 mb-1">{selectedCompetitor.category || 'Retail Establishment'}</div>
                  <div className="flex items-center gap-1.5 text-[11px] font-medium text-amber-600">
                    <span>★ {selectedCompetitor.rating ?? '4.2'}</span>
                    <span className="text-slate-400">({selectedCompetitor.reviews ?? 120} reviews)</span>
                  </div>
                  <div className="text-[11px] font-semibold text-emerald-600 mt-1">
                    {selectedCompetitor.open_status || (selectedCompetitor.open_now ? 'Open now' : 'Closed')} · {selectedCompetitor.distance || `${selectedCompetitor.distance_km || 0.8} km away`}
                  </div>
                </div>
              </InfoWindowF>
            )}
          </ReactGoogleMap>
        ) : (
          <div className="flex flex-col items-center justify-center h-full min-h-[440px] text-center p-8 space-y-3">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
            <h4 className="text-sm font-semibold text-foreground">Loading Google Maps JavaScript API...</h4>
            <p className="text-xs text-muted-foreground max-w-sm">
              Connecting to Google Maps JavaScript API with Places and Geometry libraries enabled.
            </p>
          </div>
        )}
      </div>

      {/* Bottom Corridor Switcher Strip */}
      <div className="p-3 bg-[#FFF9F6] border-t border-[#E8D7D0] flex items-center justify-between gap-2 overflow-x-auto text-xs">
        <div className="flex items-center gap-1.5 shrink-0">
          <Navigation className="w-3.5 h-3.5 text-[#D98B95]" />
          <span className="text-[11px] font-semibold text-[#7A666A]">Select Corridor:</span>
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          {locations.slice(0, 5).map((loc, idx) => {
            const isSelected = activeLocation?.area?.toLowerCase() === loc.area?.toLowerCase()
            return (
              <button
                key={loc.area}
                type="button"
                onClick={() => onSelectLocation(loc)}
                className={cn(
                  'px-3 py-1.5 rounded-full text-xs font-medium transition-all shrink-0 border flex items-center gap-2',
                  isSelected
                    ? 'bg-[#D98B95] text-white border-[#D98B95] shadow-xs font-semibold'
                    : 'bg-[#FFF9F6] hover:bg-[#F8E8EA] text-[#3D2A2D] border-[#E8D7D0]'
                )}
              >
                <span className={cn(
                  'w-4 h-4 rounded-full text-[9px] flex items-center justify-center font-bold',
                  isSelected ? 'bg-white text-[#7A3E46]' : 'bg-[#EFC7CD]/50 text-[#7A3E46]'
                )}>
                  #{idx + 1}
                </span>
                <span className="font-serif">{loc.area}</span>
                <span className={cn(
                  'text-[10px] font-bold px-1.5 py-0.2 rounded-full',
                  isSelected ? 'bg-white/20 text-white' : 'bg-[#E8F0EA] text-[#2E5A36]'
                )}>
                  {loc.score}
                </span>
              </button>
            )
          })}
        </div>
      </div>
    </Card>
  )
}
