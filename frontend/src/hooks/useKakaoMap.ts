import { useState, useEffect, useCallback, useRef } from 'react'
import { useLocationStore } from '@/stores/locationStore'
import {
  isKakaoLoaded,
  waitForKakao,
  createMap,
  createLatLng,
  createMarker,
  createCategoryMarkerImage,
  addMarkerClickListener,
  addMapEventListener,
  removeAllMarkers,
  getBoundsFromMarkers,
  type KakaoMap,
  type KakaoMarker,
  type MarkerData,
} from '@/services/kakao'
import type { AnyService } from '@/types/services'

interface UseKakaoMapProps {
  containerId: string
  initialCenter?: { latitude: number; longitude: number }
  initialZoom?: number
  onMapClick?: (latitude: number, longitude: number) => void
  onMarkerClick?: (service: AnyService) => void
  enabled?: boolean
}

interface UseKakaoMapReturn {
  map: KakaoMap | null
  isLoaded: boolean
  error: string | null
  markers: MarkerData[]
  addMarker: (service: AnyService) => void
  addMarkers: (services: AnyService[]) => void
  removeMarker: (id: string) => void
  clearMarkers: () => void
  fitBounds: () => void
  setCenter: (latitude: number, longitude: number) => void
  setZoom: (level: number) => void
  relayout: () => void
}

/**
 * Hook to manage Kakao Map instance and markers
 */
export function useKakaoMap({
  containerId,
  initialCenter,
  initialZoom = 13,
  onMapClick,
  onMarkerClick,
  enabled = true,
}: UseKakaoMapProps): UseKakaoMapReturn {
  const [map, setMap] = useState<KakaoMap | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [markers, setMarkers] = useState<MarkerData[]>([])

  const { mapCenter, zoomLevel, setMapCenter, setZoomLevel } = useLocationStore()
  const markersRef = useRef<Map<string, KakaoMarker>>(new Map())
  const initializingRef = useRef(false)
  const mapInstanceRef = useRef<KakaoMap | null>(null)

  // Initialize map
  useEffect(() => {
    // Don't initialize if not enabled
    if (!enabled) {
      return
    }

    // Prevent double initialization in StrictMode
    if (initializingRef.current || mapInstanceRef.current) {
      return
    }

    initializingRef.current = true
    let mounted = true

    const initMap = async () => {
      try {
        console.log('[KakaoMap] Starting initialization...')

        // Wait for Kakao SDK to load
        await waitForKakao()
        console.log('[KakaoMap] Kakao SDK loaded')

        if (!mounted) return

        if (!isKakaoLoaded()) {
          throw new Error('Kakao SDK failed to load')
        }

        // Wait a bit for DOM to be ready
        await new Promise(resolve => setTimeout(resolve, 100))

        if (!mounted) return

        // Get container element
        const container = document.getElementById(containerId)
        console.log('[KakaoMap] Container element:', container)

        if (!container) {
          throw new Error(`Container #${containerId} not found`)
        }

        // Use initial center or store center
        const center = initialCenter || mapCenter
        const centerLatLng = createLatLng(center.latitude, center.longitude)

        // Create map instance
        const mapInstance = createMap(container, {
          center: centerLatLng,
          level: initialZoom || zoomLevel,
        })

        // Add map event listeners
        addMapEventListener(mapInstance, 'center_changed', () => {
          const center = mapInstance.getCenter()
          setMapCenter({
            latitude: center.getLat(),
            longitude: center.getLng(),
          })
        })

        addMapEventListener(mapInstance, 'zoom_changed', () => {
          const level = mapInstance.getLevel()
          setZoomLevel(level)
        })

        if (onMapClick) {
          addMapEventListener(mapInstance, 'click', (mouseEvent: any) => {
            const latlng = mouseEvent.latLng
            onMapClick(latlng.getLat(), latlng.getLng())
          })
        }

        mapInstanceRef.current = mapInstance
        setMap(mapInstance)
        setIsLoaded(true)
        setError(null)

        if (import.meta.env.DEV) {
          console.log('[KakaoMap] Map initialized successfully')
        }
      } catch (err) {
        initializingRef.current = false
        const errorMessage = err instanceof Error ? err.message : 'Failed to initialize map'
        setError(errorMessage)
        console.error('[KakaoMap] Initialization error:', err)
      }
    }

    initMap()

    // Cleanup
    return () => {
      mounted = false
      // Don't clear mapInstanceRef on unmount to prevent re-initialization in StrictMode
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [containerId, enabled])

  // Add single marker
  const addMarker = useCallback(
    (service: AnyService) => {
      if (!map || !isLoaded) return

      try {
        const position = createLatLng(service.latitude, service.longitude)
        const markerImage = createCategoryMarkerImage(service.category)

        const marker = createMarker({
          position,
          map,
          title: service.name,
          image: markerImage,
        })

        // Add click listener
        if (onMarkerClick) {
          addMarkerClickListener(marker, () => {
            onMarkerClick(service)
          })
        }

        // Store marker
        markersRef.current.set(service.id, marker)

        // Update markers state
        setMarkers((prev) => [
          ...prev.filter((m) => m.id !== service.id),
          {
            id: service.id,
            category: service.category,
            name: service.name,
            latitude: service.latitude,
            longitude: service.longitude,
            marker,
          },
        ])

        if (import.meta.env.DEV) {
          console.log('[KakaoMap] Marker added:', service.name)
        }
      } catch (err) {
        console.error('[KakaoMap] Failed to add marker:', err)
      }
    },
    [map, isLoaded, onMarkerClick]
  )

  // Add multiple markers
  const addMarkers = useCallback(
    (services: AnyService[]) => {
      services.forEach((service) => addMarker(service))
    },
    [addMarker]
  )

  // Remove marker by ID
  const removeMarker = useCallback((id: string) => {
    const marker = markersRef.current.get(id)
    if (marker) {
      marker.setMap(null)
      markersRef.current.delete(id)
      setMarkers((prev) => prev.filter((m) => m.id !== id))

      if (import.meta.env.DEV) {
        console.log('[KakaoMap] Marker removed:', id)
      }
    }
  }, [])

  // Clear all markers
  const clearMarkers = useCallback(() => {
    const markerArray = Array.from(markersRef.current.values())
    removeAllMarkers(markerArray)
    markersRef.current.clear()
    setMarkers([])

    if (import.meta.env.DEV) {
      console.log('[KakaoMap] All markers cleared')
    }
  }, [])

  // Fit map bounds to markers
  const fitBounds = useCallback(() => {
    if (!map || markers.length === 0) return

    try {
      const bounds = getBoundsFromMarkers(markers)
      if (bounds) {
        map.setBounds(bounds)

        if (import.meta.env.DEV) {
          console.log('[KakaoMap] Bounds adjusted')
        }
      }
    } catch (err) {
      console.error('[KakaoMap] Failed to fit bounds:', err)
    }
  }, [map, markers])

  // Set map center
  const setCenter = useCallback(
    (latitude: number, longitude: number) => {
      if (!map) return

      try {
        const center = createLatLng(latitude, longitude)
        map.setCenter(center)
        setMapCenter({ latitude, longitude })

        if (import.meta.env.DEV) {
          console.log('[KakaoMap] Center changed:', latitude, longitude)
        }
      } catch (err) {
        console.error('[KakaoMap] Failed to set center:', err)
      }
    },
    [map, setMapCenter]
  )

  // Set zoom level
  const setZoom = useCallback(
    (level: number) => {
      if (!map) return

      try {
        map.setLevel(level, { animate: true })
        setZoomLevel(level)

        if (import.meta.env.DEV) {
          console.log('[KakaoMap] Zoom level changed:', level)
        }
      } catch (err) {
        console.error('[KakaoMap] Failed to set zoom:', err)
      }
    },
    [map, setZoomLevel]
  )

  // Relayout map (call this when container size changes)
  const relayout = useCallback(() => {
    if (!map) return

    try {
      map.relayout()

      if (import.meta.env.DEV) {
        console.log('[KakaoMap] Map relayout completed')
      }
    } catch (err) {
      console.error('[KakaoMap] Failed to relayout:', err)
    }
  }, [map])

  return {
    map,
    isLoaded,
    error,
    markers,
    addMarker,
    addMarkers,
    removeMarker,
    clearMarkers,
    fitBounds,
    setCenter,
    setZoom,
    relayout,
  }
}
