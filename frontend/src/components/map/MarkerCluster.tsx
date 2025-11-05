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

  // Add map click listener to close InfoWindow
  useEffect(() => {
    if (!map || !window.kakao) return

    const handleMapClick = () => {
      if (infoWindowRef.current) {
        console.log('[MarkerCluster] Map clicked - closing InfoWindow')
        infoWindowRef.current.close()
        infoWindowRef.current = null
      }
    }

    // Add click listener to map
    window.kakao.maps.event.addListener(map, 'click', handleMapClick)

    // Cleanup
    return () => {
      window.kakao.maps.event.removeListener(map, 'click', handleMapClick)
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

          // Close previous infoWindow
          if (infoWindowRef.current) {
            infoWindowRef.current.close()
          }

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

          console.log('[MarkerCluster] InfoWindow opened (no map movement)')

          // Don't pan to marker - just show InfoWindow
          // map.panTo(position)

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

    // Find marker for selected service
    const markerData = markersRef.current.find(({ service }) => service.id === selectedService.id)

    // Close previous infoWindow
    if (infoWindowRef.current) {
      infoWindowRef.current.close()
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

    console.log('[MarkerCluster] InfoWindow opened for selected service (no map movement)')

    // Don't move map - just show InfoWindow
    // const position = createLatLng(service.latitude, service.longitude)
    // map.panTo(position)
  }, [map, selectedService])

  return null
}
