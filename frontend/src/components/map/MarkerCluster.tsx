import { useEffect, useRef } from 'react'
import type { AnyService } from '@/types/services'
import { CATEGORY_COLORS } from '@/types/services'
import type { KakaoMap, KakaoInfoWindow } from '@/services/kakao'
import {
  createLatLng,
  createMarker,
  createCategoryMarkerImage,
  createInfoWindow,
  createServiceInfoWindowContent
} from '@/services/kakao'
import { clusterServices, getDominantCategory } from '@/utils/clustering'

interface MarkerClusterProps {
  map: KakaoMap | null
  services: AnyService[]
  userLocation?: { latitude: number; longitude: number } | null
  clusterThreshold?: number
  onServiceClick?: (service: AnyService) => void
  selectedService?: AnyService | null
}

export default function MarkerCluster({
  map,
  services,
  userLocation,
  clusterThreshold = 1000,
  onServiceClick,
  selectedService,
}: MarkerClusterProps) {
  const markersRef = useRef<Array<{ service: AnyService; marker: any }>>([])
  const clusterOverlaysRef = useRef<any[]>([])
  const infoWindowRef = useRef<KakaoInfoWindow | null>(null)
  const currentServiceIdRef = useRef<string | null>(null) // Track which service InfoWindow is showing
  const pendingInfoWindowRef = useRef<{ service: AnyService; marker: any; content: string } | null>(null) // Store InfoWindow data during map movement

  // Add map event listeners
  useEffect(() => {
    if (!map || !window.kakao) return

    let isMapMoving = false

    const handleMapClick = () => {
      if (infoWindowRef.current) {
        console.log('[MarkerCluster] Map clicked - closing InfoWindow')
        infoWindowRef.current.close()
        infoWindowRef.current = null
        currentServiceIdRef.current = null
        pendingInfoWindowRef.current = null
      }
    }

    // Track when map starts moving
    const handleDragStart = () => {
      console.log('[MarkerCluster] Map drag started')
      isMapMoving = true
    }

    const handleZoomStart = () => {
      console.log('[MarkerCluster] Zoom started')
      isMapMoving = true
    }

    // When map stops moving, restore InfoWindow if pending
    const handleIdle = () => {
      if (isMapMoving && pendingInfoWindowRef.current) {
        console.log('[MarkerCluster] Map idle - restoring InfoWindow')

        const { service, marker, content } = pendingInfoWindowRef.current

        // Wait a bit to ensure map has fully settled
        setTimeout(() => {
          // Close previous infoWindow
          if (infoWindowRef.current) {
            infoWindowRef.current.close()
          }

          // Create new InfoWindow
          const infoWindow = createInfoWindow({
            content,
            removable: true,
            zIndex: 1000,
          })

          // Open InfoWindow
          infoWindow.open(map, marker)
          infoWindowRef.current = infoWindow
          currentServiceIdRef.current = service.id

          console.log('[MarkerCluster] InfoWindow restored')

          // Clear pending state
          pendingInfoWindowRef.current = null
        }, 100)
      }

      isMapMoving = false
    }

    // Add all listeners
    window.kakao.maps.event.addListener(map, 'click', handleMapClick)
    window.kakao.maps.event.addListener(map, 'dragstart', handleDragStart)
    window.kakao.maps.event.addListener(map, 'zoom_start', handleZoomStart)
    window.kakao.maps.event.addListener(map, 'idle', handleIdle)

    // Cleanup
    return () => {
      window.kakao.maps.event.removeListener(map, 'click', handleMapClick)
      window.kakao.maps.event.removeListener(map, 'dragstart', handleDragStart)
      window.kakao.maps.event.removeListener(map, 'zoom_start', handleZoomStart)
      window.kakao.maps.event.removeListener(map, 'idle', handleIdle)
    }
  }, [map])

  // Update markers when services change
  useEffect(() => {
    if (!map || !window.kakao) {
      console.log('[MarkerCluster] Map or Kakao not ready', { map: !!map, kakao: !!window.kakao })
      return
    }

    console.log('[MarkerCluster] Starting marker update', { servicesCount: services.length })

    // Clear existing markers
    markersRef.current.forEach(({ marker }) => {
      if (marker && marker.setMap) {
        marker.setMap(null)
      }
    })
    markersRef.current = []

    // Clear existing cluster overlays
    clusterOverlaysRef.current.forEach((overlay) => {
      if (overlay && overlay.setMap) {
        overlay.setMap(null)
      }
    })
    clusterOverlaysRef.current = []

    // Clear existing infoWindow
    if (infoWindowRef.current) {
      infoWindowRef.current.close()
      infoWindowRef.current = null
      currentServiceIdRef.current = null
    }

    // Cluster services
    const clusters = clusterServices(services, clusterThreshold)
    console.log('[MarkerCluster] Clusters created', { clustersCount: clusters.length })

    // Create markers for each cluster
    clusters.forEach((cluster, index) => {
      console.log(`[MarkerCluster] Creating marker ${index + 1}/${clusters.length}`, {
        isCluster: cluster.isCluster,
        servicesCount: cluster.services.length,
        position: { lat: cluster.latitude, lng: cluster.longitude }
      })

      const position = createLatLng(cluster.latitude, cluster.longitude)

      if (cluster.isCluster) {
        // Create cluster marker
        const category = getDominantCategory(cluster.services)
        const color = CATEGORY_COLORS[category]
        const count = cluster.services.length

        console.log('[MarkerCluster] Creating cluster marker', { category, color, count })

        const content = document.createElement('div')
        content.style.cssText = `
          background: ${color};
          color: white;
          border: 3px solid white;
          border-radius: 50%;
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-weight: bold;
          font-size: 16px;
          box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
          cursor: pointer;
        `
        content.textContent = String(count)

        const customOverlay = new window.kakao.maps.CustomOverlay({
          position,
          content,
          zIndex: 10,
        })

        customOverlay.setMap(map)
        console.log('[MarkerCluster] Cluster marker added to map')

        // Add click handler
        content.addEventListener('click', (e) => {
          e.stopPropagation() // Prevent map click event
          map.setCenter(position)
          map.setLevel(Math.max(1, map.getLevel() - 2), { animate: true })
        })

        // Track cluster overlay for cleanup
        clusterOverlaysRef.current.push(customOverlay)
      } else {
        // Create single marker
        const service = cluster.services[0]
        console.log('[MarkerCluster] Creating single marker', { name: service.name, category: service.category })

        const markerImage = createCategoryMarkerImage(service.category, false)

        const marker = createMarker({
          position,
          map,
          title: service.name,
          image: markerImage,
          zIndex: 100, // 높은 z-index로 다른 마커 위에 표시
        })

        console.log('[MarkerCluster] Single marker created', {
          marker: !!marker,
          position: position.toString(),
          latitude: cluster.latitude,
          longitude: cluster.longitude,
        })

        // Add click handler
        window.kakao.maps.event.addListener(marker, 'click', () => {
          console.log('[MarkerCluster] Marker clicked', { service: service.name, category: service.category })

          // Create InfoWindow content
          const content = createServiceInfoWindowContent(service)

          // Close previous infoWindow
          if (infoWindowRef.current) {
            infoWindowRef.current.close()
            infoWindowRef.current = null
          }

          // Always store InfoWindow data for restoration
          pendingInfoWindowRef.current = { service, marker, content }

          // Show InfoWindow immediately
          const infoWindow = createInfoWindow({
            content,
            removable: true,
            zIndex: 1000,
          })

          infoWindow.open(map, marker)
          infoWindowRef.current = infoWindow
          currentServiceIdRef.current = service.id

          console.log('[MarkerCluster] InfoWindow opened')

          // Call parent handler
          if (onServiceClick) {
            onServiceClick(service)
          }
        })

        markersRef.current.push({ service, marker })
      }
    })

    // Cleanup on unmount
    return () => {
      markersRef.current.forEach(({ marker }) => {
        if (marker && marker.setMap) {
          marker.setMap(null)
        }
      })
      clusterOverlaysRef.current.forEach((overlay) => {
        if (overlay && overlay.setMap) {
          overlay.setMap(null)
        }
      })
      if (infoWindowRef.current) {
        infoWindowRef.current.close()
        infoWindowRef.current = null
        currentServiceIdRef.current = null
      }
    }
  }, [map, services, clusterThreshold, userLocation, onServiceClick])

  // Handle selectedService change - open InfoWindow for selected service
  useEffect(() => {
    if (!map || !selectedService) return

    console.log('[MarkerCluster] Selected service changed', {
      service: selectedService.name,
      latitude: selectedService.latitude,
      longitude: selectedService.longitude,
      id: selectedService.id
    })

    // If InfoWindow is already showing this service, don't close and reopen it
    if (currentServiceIdRef.current === selectedService.id && infoWindowRef.current) {
      console.log('[MarkerCluster] InfoWindow already showing selected service - keeping it open')
      return
    }

    // Find marker for selected service
    const markerData = markersRef.current.find(({ service }) => service.id === selectedService.id)

    // Close previous infoWindow
    if (infoWindowRef.current) {
      infoWindowRef.current.close()
      currentServiceIdRef.current = null
    }

    if (!markerData) {
      console.log('[MarkerCluster] Marker not found for selected service (might be in cluster)', {
        serviceId: selectedService.id,
        latitude: selectedService.latitude,
        longitude: selectedService.longitude
      })

      // Validate coordinates
      if (!selectedService.latitude || !selectedService.longitude ||
          isNaN(selectedService.latitude) || isNaN(selectedService.longitude)) {
        console.error('[MarkerCluster] Invalid coordinates for selected service', {
          latitude: selectedService.latitude,
          longitude: selectedService.longitude,
          service: selectedService
        })
        return
      }

      // Service is in a cluster - create InfoWindow at service position
      const position = createLatLng(selectedService.latitude, selectedService.longitude)
      const content = createServiceInfoWindowContent(selectedService)

      const infoWindow = createInfoWindow({
        content,
        removable: true,
        zIndex: 1000,
      })

      // Open InfoWindow at position (without marker)
      infoWindow.open(map)
      infoWindow.setPosition(position)
      infoWindowRef.current = infoWindow
      currentServiceIdRef.current = selectedService.id

      // Don't move map - just show InfoWindow
      // map.panTo(position)
      // map.setLevel(Math.max(1, map.getLevel() - 1), { animate: true })

      console.log('[MarkerCluster] InfoWindow opened at service position (no map movement)')
      return
    }

    const { service, marker } = markerData

    // Create InfoWindow with all API data
    const content = createServiceInfoWindowContent(service)

    const infoWindow = createInfoWindow({
      content,
      removable: true,
      zIndex: 1000,
    })

    // Open InfoWindow
    infoWindow.open(map, marker)
    infoWindowRef.current = infoWindow
    currentServiceIdRef.current = selectedService.id

    console.log('[MarkerCluster] InfoWindow opened for selected service (no map movement)')

    // Don't move map - just show InfoWindow
    // const position = createLatLng(service.latitude, service.longitude)
    // map.panTo(position)
  }, [map, selectedService])

  return null
}
