/* eslint-disable @typescript-eslint/no-explicit-any */
import type { ServiceCategory, AnyService } from '@/types/services'
import { CATEGORY_COLORS, CATEGORY_LABELS } from '@/types/services'

// Kakao Maps SDK Type Definitions
declare global {
  interface Window {
    kakao: any
  }
}

export interface KakaoLatLng {
  getLat(): number
  getLng(): number
}

export interface KakaoMapOptions {
  center: KakaoLatLng
  level: number
}

export interface KakaoMap {
  setCenter(latlng: KakaoLatLng): void
  getCenter(): KakaoLatLng
  setLevel(level: number, options?: { animate?: boolean }): void
  getLevel(): number
  panTo(latlng: KakaoLatLng): void
  relayout(): void
  setBounds(bounds: any): void
  getProjection(): any
}

export interface KakaoMarkerOptions {
  position: KakaoLatLng
  map?: KakaoMap
  title?: string
  image?: KakaoMarkerImage
  clickable?: boolean
  zIndex?: number
}

export interface KakaoMarker {
  setMap(map: KakaoMap | null): void
  getPosition(): KakaoLatLng
  setPosition(latlng: KakaoLatLng): void
  setTitle(title: string): void
  setImage(image: KakaoMarkerImage): void
  setZIndex(zIndex: number): void
}

export interface KakaoMarkerImageOptions {
  size: KakaoSize
  offset?: KakaoPoint
  alt?: string
  coords?: string
  shape?: string
}

export interface KakaoMarkerImage {
  // Marker image instance
}

export interface KakaoSize {
  width: number
  height: number
}

export interface KakaoPoint {
  x: number
  y: number
}

export interface KakaoInfoWindowOptions {
  content: string
  removable?: boolean
  position?: KakaoLatLng
  zIndex?: number
}

export interface KakaoInfoWindow {
  open(map: KakaoMap, marker?: KakaoMarker): void
  close(): void
  setContent(content: string): void
  getContent(): string
  getPosition(): KakaoLatLng
  setPosition(position: KakaoLatLng): void
  setZIndex(zIndex: number): void
}

export interface MarkerData {
  id: string
  category: ServiceCategory
  name: string
  latitude: number
  longitude: number
  marker?: KakaoMarker
}

// Kakao SDK Wrapper Functions

/**
 * Check if Kakao SDK is loaded
 */
export function isKakaoLoaded(): boolean {
  return typeof window !== 'undefined' && window.kakao && window.kakao.maps
}

/**
 * Wait for Kakao SDK to load
 */
export function waitForKakao(timeout = 10000): Promise<void> {
  return new Promise((resolve, reject) => {
    if (isKakaoLoaded()) {
      resolve()
      return
    }

    // Check if script tag exists
    const scriptTag = document.querySelector('script[src*="dapi.kakao.com"]')
    if (!scriptTag) {
      reject(new Error('Kakao SDK script tag not found in HTML'))
      return
    }

    const startTime = Date.now()
    const checkInterval = setInterval(() => {
      if (isKakaoLoaded()) {
        clearInterval(checkInterval)
        resolve()
      } else if (Date.now() - startTime > timeout) {
        clearInterval(checkInterval)
        // Check if window.kakao exists but maps doesn't
        if (window.kakao && !window.kakao.maps) {
          reject(new Error('Kakao SDK loaded but maps API not available. Check your API key and platform settings at https://developers.kakao.com'))
        } else {
          reject(new Error('Kakao SDK load timeout. Check your network connection and API key.'))
        }
      }
    }, 100)
  })
}

/**
 * Create LatLng object
 */
export function createLatLng(latitude: number, longitude: number): KakaoLatLng {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }
  return new window.kakao.maps.LatLng(latitude, longitude)
}

/**
 * Create map instance
 */
export function createMap(container: HTMLElement, options: KakaoMapOptions): KakaoMap {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }
  return new window.kakao.maps.Map(container, options)
}

/**
 * Create marker instance
 */
export function createMarker(options: KakaoMarkerOptions): KakaoMarker {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }
  return new window.kakao.maps.Marker(options)
}

/**
 * Create marker image for category
 */
export function createCategoryMarkerImage(
  category: ServiceCategory,
  isSelected = false
): KakaoMarkerImage {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }

  const color = CATEGORY_COLORS[category]
  const size = isSelected ? 56 : 44 // 크기 증가 (36 -> 44, 48 -> 56)

  // Create custom marker image using canvas (no CORS issues)
  const imageSrc = createCustomMarkerImage(color, size, isSelected)
  const imageSize = new window.kakao.maps.Size(size, size * 1.5)
  const imageOption = {
    offset: new window.kakao.maps.Point(size / 2, size * 1.5),
  }

  console.log('[createCategoryMarkerImage]', {
    category,
    color,
    size,
    imageSrc: imageSrc.substring(0, 50) + '...',
  })

  return new window.kakao.maps.MarkerImage(imageSrc, imageSize, imageOption)
}

/**
 * Create custom colored marker image using canvas
 */
export function createCustomMarkerImage(
  color: string,
  size = 36,
  isSelected = false
): string {
  const canvas = document.createElement('canvas')
  const scale = isSelected ? 1.5 : 1.0
  const actualSize = size * scale

  canvas.width = actualSize
  canvas.height = actualSize * 1.5

  const ctx = canvas.getContext('2d')
  if (!ctx) return ''

  // Draw marker pin shape
  ctx.fillStyle = color
  ctx.beginPath()
  ctx.arc(actualSize / 2, actualSize / 2, actualSize / 2 - 2, 0, Math.PI * 2)
  ctx.fill()

  // Draw border
  ctx.strokeStyle = '#ffffff'
  ctx.lineWidth = 3
  ctx.stroke()

  // Draw pointer
  ctx.beginPath()
  ctx.moveTo(actualSize / 2 - 8, actualSize / 2 + 8)
  ctx.lineTo(actualSize / 2, actualSize * 1.5 - 4)
  ctx.lineTo(actualSize / 2 + 8, actualSize / 2 + 8)
  ctx.closePath()
  ctx.fill()

  return canvas.toDataURL()
}

/**
 * Add click event listener to marker
 */
export function addMarkerClickListener(
  marker: KakaoMarker,
  callback: (marker: KakaoMarker) => void
): void {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }
  window.kakao.maps.event.addListener(marker, 'click', () => callback(marker))
}

/**
 * Add map event listener
 */
export function addMapEventListener(
  map: KakaoMap,
  eventName: string,
  callback: (...args: any[]) => void
): void {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }
  window.kakao.maps.event.addListener(map, eventName, callback)
}

/**
 * Remove all markers from map
 */
export function removeAllMarkers(markers: KakaoMarker[]): void {
  markers.forEach((marker) => {
    marker.setMap(null)
  })
}

/**
 * Calculate bounds from markers
 */
export function getBoundsFromMarkers(markers: MarkerData[]): any {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }

  if (markers.length === 0) return null

  const bounds = new window.kakao.maps.LatLngBounds()
  markers.forEach((markerData) => {
    const position = createLatLng(markerData.latitude, markerData.longitude)
    bounds.extend(position)
  })

  return bounds
}

/**
 * Fit map to bounds
 */
export function fitBounds(map: KakaoMap, bounds: any): void {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }
  map.setBounds(bounds)
}

/**
 * Get distance between two points (in meters)
 */
export function getDistance(lat1: number, lng1: number, lat2: number, lng2: number): number {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }

  const point1 = createLatLng(lat1, lng1)
  const point2 = createLatLng(lat2, lng2)

  const polyline = new window.kakao.maps.Polyline({
    path: [point1, point2],
  })

  return polyline.getLength() // Returns distance in meters
}

/**
 * Convert zoom level to approximate radius (in meters)
 */
export function zoomLevelToRadius(level: number): number {
  // Approximate conversion (may vary by latitude)
  // Level 14: ~2km, Level 13: ~4km, Level 12: ~8km, etc.
  return Math.pow(2, 14 - level) * 2000
}

/**
 * Convert radius to appropriate zoom level
 */
export function radiusToZoomLevel(radius: number): number {
  // Inverse of zoomLevelToRadius
  return Math.max(1, Math.min(14, 14 - Math.log2(radius / 2000)))
}

/**
 * Create InfoWindow instance
 */
export function createInfoWindow(options: KakaoInfoWindowOptions): KakaoInfoWindow {
  if (!isKakaoLoaded()) {
    throw new Error('Kakao SDK not loaded')
  }
  return new window.kakao.maps.InfoWindow(options)
}

/**
 * Create InfoWindow content HTML for a service
 * Now displays ALL API data fields dynamically
 */
export function createServiceInfoWindowContent(service: AnyService): string {
  const categoryLabel = CATEGORY_LABELS[service.category]
  const categoryColor = CATEGORY_COLORS[service.category]

  // Helper to format field names (snake_case to readable)
  const formatFieldName = (key: string): string => {
    // Skip internal fields
    if (['id', 'category', 'name', 'latitude', 'longitude', 'distance'].includes(key)) {
      return ''
    }

    // Convert snake_case to Title Case
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  // Helper to format field values
  const formatValue = (value: any, key: string): string => {
    if (value === null || value === undefined || value === '') {
      return '-'
    }

    // Check if it's a URL
    if (
      typeof value === 'string' &&
      (value.startsWith('http://') || value.startsWith('https://'))
    ) {
      return `<a href="${value}" target="_blank" style="color: #1971C2; text-decoration: underline;">바로가기</a>`
    }

    // Check if it's a number with specific formatting needs
    if (typeof value === 'number') {
      // If key suggests it's a count/quantity, format with commas
      if (key.includes('co') || key.includes('count') || key.includes('num')) {
        return value.toLocaleString()
      }
      return String(value)
    }

    // If it's an object or array, stringify it
    if (typeof value === 'object') {
      return JSON.stringify(value, null, 2)
    }

    // Return as string
    return String(value).replace(/</g, '&lt;').replace(/>/g, '&gt;')
  }

  // Build details HTML by iterating over all properties
  let detailsHtml = ''
  const serviceObj = service as any

  // Get all keys and sort them (optional - can remove sort for original order)
  const keys = Object.keys(serviceObj)

  keys.forEach((key) => {
    const fieldName = formatFieldName(key)
    if (!fieldName) return // Skip internal fields

    const value = serviceObj[key]
    const formattedValue = formatValue(value, key)

    detailsHtml += `
      <div class="info-row">
        <span class="label">${fieldName}:</span>
        <span class="value">${formattedValue}</span>
      </div>
    `
  })

  // Build complete HTML
  const html = `
    <div class="kakao-infowindow" style="padding: 16px; min-width: 320px; max-width: 450px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
      <div style="display: flex; align-items: center; margin-bottom: 12px; padding-bottom: 12px; border-bottom: 2px solid ${categoryColor};">
        <div style="width: 12px; height: 12px; border-radius: 50%; background-color: ${categoryColor}; margin-right: 8px;"></div>
        <div style="flex: 1;">
          <div style="font-size: 10px; color: #868e96; text-transform: uppercase; letter-spacing: 0.5px;">${categoryLabel}</div>
          <div style="font-size: 16px; font-weight: 700; color: #212529; margin-top: 2px;">${service.name}</div>
        </div>
      </div>
      <div style="font-size: 13px; line-height: 1.6; color: #495057; max-height: 500px; overflow-y: auto;">
        ${detailsHtml}
        <div class="info-row" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #e9ecef;">
          <span class="label">좌표:</span>
          <span class="value">${service.latitude.toFixed(6)}, ${service.longitude.toFixed(6)}</span>
        </div>
      </div>
    </div>
    <style>
      .kakao-infowindow .info-row {
        margin-bottom: 8px;
        display: flex;
        gap: 8px;
        align-items: flex-start;
      }
      .kakao-infowindow .label {
        font-weight: 600;
        color: #495057;
        min-width: 100px;
        flex-shrink: 0;
      }
      .kakao-infowindow .value {
        flex: 1;
        word-break: break-word;
        white-space: pre-wrap;
      }
      .kakao-infowindow a {
        word-break: break-all;
      }
    </style>
  `

  return html
}
