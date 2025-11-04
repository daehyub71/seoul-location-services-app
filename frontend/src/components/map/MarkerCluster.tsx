import { useEffect, useRef } from 'react'
import type { AnyService } from '@/types/services'
import { CATEGORY_COLORS, CATEGORY_LABELS } from '@/types/services'
import type { KakaoMap } from '@/services/kakao'
import { createLatLng, createMarker, createCategoryMarkerImage } from '@/services/kakao'
import { clusterServices, getDominantCategory, calculateDistance, formatDistance } from '@/utils/clustering'

interface MarkerClusterProps {
  map: KakaoMap | null
  services: AnyService[]
  userLocation?: { latitude: number; longitude: number } | null
  clusterThreshold?: number
  onServiceClick?: (service: AnyService) => void
}

export default function MarkerCluster({
  map,
  services,
  userLocation,
  clusterThreshold = 1000,
  onServiceClick,
}: MarkerClusterProps) {
  const markersRef = useRef<any[]>([])
  const overlayRef = useRef<any>(null)

  // Update markers when services change
  useEffect(() => {
    if (!map || !window.kakao) {
      console.log('[MarkerCluster] Map or Kakao not ready', { map: !!map, kakao: !!window.kakao })
      return
    }

    console.log('[MarkerCluster] Starting marker update', { servicesCount: services.length })

    // Clear existing markers
    markersRef.current.forEach((marker) => {
      if (marker && marker.setMap) {
        marker.setMap(null)
      }
    })
    markersRef.current = []

    // Clear existing overlay
    if (overlayRef.current) {
      overlayRef.current.setMap(null)
      overlayRef.current = null
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
        content.addEventListener('click', () => {
          map.setCenter(position)
          map.setLevel(Math.max(1, map.getLevel() - 2), { animate: true })
        })

        markersRef.current.push(customOverlay)
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
          // Close previous overlay
          if (overlayRef.current) {
            overlayRef.current.setMap(null)
          }

          // Calculate distance
          const distance = userLocation
            ? calculateDistance(
                userLocation.latitude,
                userLocation.longitude,
                service.latitude,
                service.longitude
              )
            : undefined

          // Create overlay content
          const categoryColor = CATEGORY_COLORS[service.category]
          const categoryLabel = CATEGORY_LABELS[service.category]
          const distanceText = distance ? formatDistance(distance) : ''

          const overlayContent = document.createElement('div')
          overlayContent.style.cssText = `
            background: white;
            border: 2px solid ${categoryColor};
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            min-width: 250px;
            max-width: 300px;
          `
          overlayContent.innerHTML = `
            <div style="
              background: ${categoryColor}15;
              padding: 12px;
              border-radius: 6px 6px 0 0;
              display: flex;
              align-items: center;
              justify-content: space-between;
            ">
              <div style="display: flex; align-items: center; gap: 8px;">
                <div style="
                  width: 12px;
                  height: 12px;
                  border-radius: 50%;
                  background: ${categoryColor};
                "></div>
                <span style="
                  color: ${categoryColor};
                  font-weight: 600;
                  font-size: 14px;
                ">${categoryLabel}</span>
              </div>
              <button
                style="
                  background: none;
                  border: none;
                  cursor: pointer;
                  padding: 4px;
                  font-size: 20px;
                  line-height: 1;
                  color: #666;
                "
                onclick="this.closest('div').parentElement.remove()"
              >×</button>
            </div>
            <div style="padding: 12px;">
              <h3 style="
                font-weight: bold;
                font-size: 16px;
                margin: 0 0 8px 0;
                color: #111;
              ">${service.name}</h3>
              ${distanceText ? `
                <div style="
                  font-size: 14px;
                  color: #666;
                  margin-bottom: 8px;
                ">📍 ${distanceText}</div>
              ` : ''}
              ${(service as any).address ? `
                <p style="
                  font-size: 13px;
                  color: #666;
                  margin: 0 0 8px 0;
                  line-height: 1.4;
                ">${(service as any).address}</p>
              ` : ''}
              <button
                style="
                  width: 100%;
                  padding: 8px 16px;
                  background: ${categoryColor};
                  color: white;
                  border: none;
                  border-radius: 4px;
                  font-weight: 500;
                  cursor: pointer;
                  font-size: 14px;
                "
              >상세보기</button>
            </div>
          `

          const overlay = new window.kakao.maps.CustomOverlay({
            position,
            content: overlayContent,
            yAnchor: 1,
            zIndex: 1000,
          })

          overlay.setMap(map)
          overlayRef.current = overlay

          // Pan to marker
          map.panTo(position)

          // Call parent handler
          if (onServiceClick) {
            onServiceClick(service)
          }
        })

        markersRef.current.push(marker)
      }
    })

    // Cleanup on unmount
    return () => {
      markersRef.current.forEach((marker) => {
        if (marker && marker.setMap) {
          marker.setMap(null)
        }
      })
      if (overlayRef.current) {
        overlayRef.current.setMap(null)
      }
    }
  }, [map, services, clusterThreshold, userLocation, onServiceClick])

  return null
}
