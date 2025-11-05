import type { AnyService } from '@/types/services'

export interface MarkerCluster {
  id: string
  latitude: number
  longitude: number
  services: AnyService[]
  isCluster: boolean
}

/**
 * Calculate distance between two points using Haversine formula (in meters)
 */
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371e3 // Earth's radius in meters
  const φ1 = (lat1 * Math.PI) / 180
  const φ2 = (lat2 * Math.PI) / 180
  const Δφ = ((lat2 - lat1) * Math.PI) / 180
  const Δλ = ((lon2 - lon1) * Math.PI) / 180

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  return R * c
}

/**
 * Cluster services based on distance threshold
 * @param services - Array of services to cluster
 * @param threshold - Distance threshold in meters (default: 1000m = 1km). Set to 0 to disable clustering.
 * @returns Array of clusters
 */
export function clusterServices(
  services: AnyService[],
  threshold = 1000
): MarkerCluster[] {
  if (services.length === 0) return []

  // If threshold is 0, return all services as individual markers (no clustering)
  if (threshold === 0) {
    return services.map((service) => ({
      id: service.id,
      latitude: service.latitude,
      longitude: service.longitude,
      services: [service],
      isCluster: false,
    }))
  }

  const clusters: MarkerCluster[] = []
  const visited = new Set<string>()

  for (const service of services) {
    if (visited.has(service.id)) continue

    // Find nearby services within threshold
    const nearbyServices = services.filter((other) => {
      if (visited.has(other.id)) return false
      if (service.id === other.id) return true

      const distance = calculateDistance(
        service.latitude,
        service.longitude,
        other.latitude,
        other.longitude
      )

      return distance <= threshold
    })

    // Mark all nearby services as visited
    nearbyServices.forEach((s) => visited.add(s.id))

    // Calculate cluster center (average position)
    const centerLat =
      nearbyServices.reduce((sum, s) => sum + s.latitude, 0) / nearbyServices.length
    const centerLon =
      nearbyServices.reduce((sum, s) => sum + s.longitude, 0) / nearbyServices.length

    clusters.push({
      id: nearbyServices.map((s) => s.id).join('-'),
      latitude: centerLat,
      longitude: centerLon,
      services: nearbyServices,
      isCluster: nearbyServices.length > 1,
    })
  }

  return clusters
}

/**
 * Get dominant category from a cluster
 */
export function getDominantCategory(services: AnyService[]): AnyService['category'] {
  const categoryCounts = services.reduce(
    (acc, service) => {
      acc[service.category] = (acc[service.category] || 0) + 1
      return acc
    },
    {} as Record<string, number>
  )

  return Object.entries(categoryCounts).reduce((a, b) =>
    a[1] > b[1] ? a : b
  )[0] as AnyService['category']
}

/**
 * Format distance for display
 */
export function formatDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)}m`
  }
  return `${(meters / 1000).toFixed(1)}km`
}
