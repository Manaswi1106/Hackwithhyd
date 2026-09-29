import React, { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { MapPin, Store, Layers, AlertCircle, Info } from 'lucide-react'

// Mapbox Token from Vite environment
const MAPBOX_TOKEN = (import.meta as any).env?.VITE_MAPBOX_TOKEN || ''

// Helper to generate geojson circle for search radius
function createGeoJSONCircle(center: [number, number], radiusInKm: number, points = 64) {
  const [lng, lat] = center
  const coords = []
  const distanceX = radiusInKm / (111.320 * Math.cos((lat * Math.PI) / 180))
  const distanceY = radiusInKm / 110.574

  for (let i = 0; i < points; i++) {
    const theta = (i / points) * (2 * Math.PI)
    const x = distanceX * Math.cos(theta)
    const y = distanceY * Math.sin(theta)
    coords.push([lng + x, lat + y])
  }
  coords.push(coords[0])

  return {
    type: 'Feature' as const,
    geometry: {
      type: 'Polygon' as const,
      coordinates: [coords],
    },
    properties: {},
  }
}

interface MapLocation {
  area: string
  score: number
  predicted_monthly_revenue: number
  rent: number
  footfall: number
  office_density?: number
  risk?: string
  lat: number
  lng: number
  avg_rent_sqft?: number
  competitor_count?: number
}

interface Competitor {
  business_name: string
  category: string
  rating: number
  review_count: number
  distance_km?: number
  coordinates: { lat: number; lng: number }
  price_level?: string
}

interface MapboxLiveMapProps {
  locations: MapLocation[]
  activeLocation?: MapLocation | null
  onSelectLocation?: (loc: MapLocation) => void
  competitors?: Competitor[]
  searchRadiusKm?: number
  isDemoCompetitorData?: boolean
  className?: string
}

export const MapboxLiveMap: React.FC<MapboxLiveMapProps> = ({
  locations = [],
  activeLocation,
  onSelectLocation,
  competitors = [],
  searchRadiusKm = 2.5,
  isDemoCompetitorData = false,
  className = '',
}) => {
  const mapContainer = useRef<HTMLDivElement>(null)
  const mapRef = useRef<mapboxgl.Map | null>(null)
  const markersRef = useRef<mapboxgl.Marker[]>([])
  const compMarkersRef = useRef<mapboxgl.Marker[]>([])
  const [mapLoaded, setMapLoaded] = useState(false)
  const [tokenMissing, setTokenMissing] = useState(!MAPBOX_TOKEN)

  useEffect(() => {
    if (!mapContainer.current) return

    // If Mapbox token is not set, we can either use token or show banner
    if (!MAPBOX_TOKEN) {
      setTokenMissing(true)
      // Provide a standard Mapbox public access token for demo preview if not configured
      mapboxgl.accessToken = 'pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4M29iazA2Z2gycXA4N2pmbDZmangifQ.-g_vE53SD2WrJ6tFX7QHmA'
    } else {
      mapboxgl.accessToken = MAPBOX_TOKEN
      setTokenMissing(false)
    }

    try {
      const map = new mapboxgl.Map({
        container: mapContainer.current,
        style: 'mapbox://styles/mapbox/dark-v11',
        center: activeLocation ? [activeLocation.lng, activeLocation.lat] : [78.385, 17.442],
        zoom: 11.5,
      })

      map.addControl(new mapboxgl.NavigationControl({ showCompass: true }), 'top-right')

      map.on('load', () => {
        setMapLoaded(true)
      })

      mapRef.current = map

      return () => {
        markersRef.current.forEach(m => m.remove())
        compMarkersRef.current.forEach(m => m.remove())
        map.remove()
      }
    } catch (err) {
      console.warn('Mapbox initialization notice:', err)
      setTokenMissing(true)
    }
  }, [])

  // Update Top 5 Recommended Location Markers & Heatmap
  useEffect(() => {
    const map = mapRef.current
    if (!map || !mapLoaded || locations.length === 0) return

    // Clear old recommendation markers
    markersRef.current.forEach(m => m.remove())
    markersRef.current = []

    // 1. Add / Update GeoJSON Opportunity Heatmap Layer
    const heatmapFeatures = locations.map(loc => ({
      type: 'Feature' as const,
      geometry: {
        type: 'Point' as const,
        coordinates: [loc.lng, loc.lat] as [number, number],
      },
      properties: {
        score: loc.score,
        area: loc.area,
        revenue: loc.predicted_monthly_revenue,
      },
    }))

    const geojsonData: any = {
      type: 'FeatureCollection',
      features: heatmapFeatures,
    }

    if (map.getSource('opportunity-source')) {
      (map.getSource('opportunity-source') as mapboxgl.GeoJSONSource).setData(geojsonData)
    } else {
      map.addSource('opportunity-source', {
        type: 'geojson',
        data: geojsonData,
      })

      // Opportunity Heatmap Thermal Glow
      map.addLayer({
        id: 'opportunity-heat',
        type: 'heatmap',
        source: 'opportunity-source',
        maxzoom: 15,
        paint: {
          'heatmap-weight': ['interpolate', ['linear'], ['get', 'score'], 40, 0.2, 90, 1.0],
          'heatmap-intensity': ['interpolate', ['linear'], ['zoom'], 9, 1, 14, 2.5],
          'heatmap-color': [
            'interpolate',
            ['linear'],
            ['heatmap-density'],
            0, 'rgba(0, 0, 0, 0)',
            0.2, 'rgba(56, 189, 248, 0.4)',
            0.5, 'rgba(16, 185, 129, 0.65)',
            0.8, 'rgba(234, 179, 8, 0.85)',
            1, 'rgba(244, 63, 94, 0.95)',
          ],
          'heatmap-radius': ['interpolate', ['linear'], ['zoom'], 9, 20, 14, 45],
          'heatmap-opacity': 0.65,
        },
      })
    }

    // 2. Add Interactive Custom DOM Markers for Top Locations
    locations.slice(0, 5).forEach((loc, index) => {
      const el = document.createElement('div')
      const isSelected = activeLocation?.area.toLowerCase() === loc.area.toLowerCase()
      const rank = index + 1

      el.className = `flex items-center justify-center cursor-pointer transition-transform duration-200 ${
        isSelected ? 'scale-125 z-30' : 'hover:scale-110 z-20'
      }`

      el.innerHTML = `
        <div class="relative flex items-center justify-center">
          <div class="w-8 h-8 rounded-full ${
            rank === 1
              ? 'bg-emerald-500 shadow-[0_0_18px_rgba(16,185,129,0.8)]'
              : rank <= 3
              ? 'bg-blue-600 shadow-[0_0_12px_rgba(37,99,235,0.6)]'
              : 'bg-slate-700 shadow-md'
          } text-white font-bold text-xs flex items-center justify-center border-2 ${
            isSelected ? 'border-amber-300 ring-2 ring-amber-400' : 'border-white'
          }">
            #${rank}
          </div>
          <span class="absolute -bottom-5 bg-background/90 text-foreground text-[10px] font-semibold px-1.5 py-0.5 rounded shadow border border-border whitespace-nowrap">
            ${loc.area}
          </span>
        </div>
      `

      // Popup Content Card
      const popupHtml = `
        <div class="p-3 text-slate-900 min-w-[210px] font-sans">
          <div class="flex items-center justify-between border-b pb-1.5 mb-2">
            <span class="font-bold text-sm text-slate-900">${loc.area}</span>
            <span class="bg-emerald-100 text-emerald-800 text-[11px] font-semibold px-2 py-0.5 rounded-full">
              Score: ${loc.score}/100
            </span>
          </div>
          <div class="space-y-1 text-xs text-slate-700">
            <div class="flex justify-between">
              <span class="text-slate-500">Exp. Monthly Revenue:</span>
              <span class="font-semibold text-emerald-700">₹${(loc.predicted_monthly_revenue / 100000).toFixed(1)}L</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Rent:</span>
              <span class="font-medium">₹${(loc.rent / 1000).toFixed(0)}k/mo (₹${loc.avg_rent_sqft || 180}/sqft)</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Daily Footfall:</span>
              <span class="font-medium">${(loc.footfall || 50000).toLocaleString('en-IN')}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Office Density:</span>
              <span class="font-medium">${loc.office_density || 80}/100</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-500">Risk Profile:</span>
              <span class="font-medium ${loc.risk === 'Low' ? 'text-emerald-600' : 'text-amber-600'}">${loc.risk || 'Low'}</span>
            </div>
          </div>
        </div>
      `

      const popup = new mapboxgl.Popup({ offset: 25, closeButton: false }).setHTML(popupHtml)

      el.addEventListener('click', () => {
        if (onSelectLocation) onSelectLocation(loc)
        map.flyTo({ center: [loc.lng, loc.lat], zoom: 13.5, essential: true })
      })

      const marker = new mapboxgl.Marker(el)
        .setLngLat([loc.lng, loc.lat])
        .setPopup(popup)
        .addTo(map)

      markersRef.current.push(marker)
    })
  }, [locations, mapLoaded, activeLocation])

  // Update Search Radius Circle around Active Location
  useEffect(() => {
    const map = mapRef.current
    if (!map || !mapLoaded || !activeLocation) return

    const circleGeoJSON = createGeoJSONCircle(
      [activeLocation.lng, activeLocation.lat],
      searchRadiusKm
    )

    if (map.getSource('search-radius-source')) {
      (map.getSource('search-radius-source') as mapboxgl.GeoJSONSource).setData(circleGeoJSON as any)
    } else {
      map.addSource('search-radius-source', {
        type: 'geojson',
        data: circleGeoJSON as any,
      })

      map.addLayer({
        id: 'search-radius-fill',
        type: 'fill',
        source: 'search-radius-source',
        paint: {
          'fill-color': '#0284c7',
          'fill-opacity': 0.12,
        },
      })

      map.addLayer({
        id: 'search-radius-line',
        type: 'line',
        source: 'search-radius-source',
        paint: {
          'line-color': '#38bdf8',
          'line-width': 2,
          'line-dasharray': [2, 2],
        },
      })
    }

    // Smooth camera transition to active selection
    map.flyTo({
      center: [activeLocation.lng, activeLocation.lat],
      zoom: 13,
      duration: 1200,
      essential: true,
    })
  }, [activeLocation, searchRadiusKm, mapLoaded])

  // Update Competitor Markers
  useEffect(() => {
    const map = mapRef.current
    if (!map || !mapLoaded) return

    compMarkersRef.current.forEach(m => m.remove())
    compMarkersRef.current = []

    competitors.forEach((comp) => {
      const lat = comp.coordinates?.lat
      const lng = comp.coordinates?.lng
      if (!lat || !lng) return

      const el = document.createElement('div')
      el.className = 'cursor-pointer hover:scale-125 transition-transform z-10'
      el.innerHTML = `
        <div class="w-5 h-5 rounded-full bg-rose-500/80 border border-white text-white flex items-center justify-center shadow-sm">
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
          </svg>
        </div>
      `

      const popupHtml = `
        <div class="p-2 text-slate-900 text-xs font-sans min-w-[170px]">
          <div class="font-bold text-slate-900">${comp.business_name}</div>
          <div class="text-[11px] text-slate-500">${comp.category} · ${comp.price_level || '$$'}</div>
          <div class="mt-1 flex items-center justify-between text-[11px]">
            <span class="text-amber-600 font-semibold">★ ${comp.rating} (${comp.review_count})</span>
            <span class="text-slate-400">${comp.distance_km ? `${comp.distance_km}km` : 'nearby'}</span>
          </div>
        </div>
      `

      const popup = new mapboxgl.Popup({ offset: 15, closeButton: false }).setHTML(popupHtml)

      const marker = new mapboxgl.Marker(el)
        .setLngLat([lng, lat])
        .setPopup(popup)
        .addTo(map)

      compMarkersRef.current.push(marker)
    })
  }, [competitors, mapLoaded])

  return (
    <div className={`relative w-full h-full rounded-lg overflow-hidden border border-border ${className}`}>
      {/* Mapbox Canvas */}
      <div ref={mapContainer} className="w-full h-full min-h-[440px]" />

      {/* Top Left Badge Overlay: Mapbox Engine Indicator */}
      <div className="absolute top-3 left-3 z-10 flex flex-col gap-1.5 pointer-events-none">
        <div className="flex items-center gap-2 bg-background/90 backdrop-blur-md px-3 py-1.5 rounded-md border border-border shadow-sm text-xs font-medium text-foreground">
          <Layers className="w-3.5 h-3.5 text-primary" />
          <span>Mapbox Live Location Intelligence</span>
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse ml-1" />
        </div>

        {isDemoCompetitorData && (
          <div className="flex items-center gap-1.5 bg-amber-500/10 backdrop-blur-md px-2.5 py-1 rounded border border-amber-500/30 text-[11px] font-semibold text-amber-500">
            <Info className="w-3 h-3" />
            <span>DEMO DATA (Google Places API key optional)</span>
          </div>
        )}
      </div>

      {/* Bottom Right Legend */}
      <div className="absolute bottom-3 right-3 z-10 bg-background/90 backdrop-blur-md p-2.5 rounded-md border border-border shadow-sm text-[11px] space-y-1.5 pointer-events-auto">
        <div className="font-semibold text-xs text-foreground flex items-center gap-1">
          <Store className="w-3 h-3 text-emerald-500" />
          Map Legend
        </div>
        <div className="flex items-center gap-2 text-muted-foreground">
          <div className="w-3 h-3 rounded-full bg-emerald-500 border border-white" />
          <span>Top #1 Recommended Corridor</span>
        </div>
        <div className="flex items-center gap-2 text-muted-foreground">
          <div className="w-3 h-3 rounded-full bg-blue-600 border border-white" />
          <span>Top #2 - #5 Corridors</span>
        </div>
        <div className="flex items-center gap-2 text-muted-foreground">
          <div className="w-3 h-3 rounded-full bg-rose-500 border border-white" />
          <span>Competitor Establishment</span>
        </div>
        <div className="flex items-center gap-2 text-muted-foreground">
          <div className="w-3 h-1 border-t-2 border-dashed border-sky-400" />
          <span>Search Radius ({searchRadiusKm} km)</span>
        </div>
      </div>
    </div>
  )
}
export default MapboxLiveMap
