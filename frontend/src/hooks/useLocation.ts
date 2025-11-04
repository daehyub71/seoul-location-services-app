import { useState, useEffect, useCallback } from 'react'
import { useLocationStore } from '@/stores/locationStore'
import type { Location } from '@/stores/locationStore'

interface LocationError {
  code: number
  message: string
}

interface UseLocationReturn {
  location: Location | null
  error: LocationError | null
  loading: boolean
  requestLocation: () => void
  clearError: () => void
  permissionStatus: PermissionState | null
}

// Default location: Seoul City Hall
const DEFAULT_LOCATION: Location = {
  latitude: 37.5665,
  longitude: 126.978,
}

/**
 * Hook to manage user's geolocation
 */
export function useLocation(): UseLocationReturn {
  const { userLocation, setUserLocation } = useLocationStore()
  const [error, setError] = useState<LocationError | null>(null)
  const [loading, setLoading] = useState(false)
  const [permissionStatus, setPermissionStatus] = useState<PermissionState | null>(null)

  // Check geolocation permission status
  useEffect(() => {
    if (!navigator.permissions) return

    navigator.permissions
      .query({ name: 'geolocation' })
      .then((result) => {
        setPermissionStatus(result.state)

        // Listen for permission changes
        result.addEventListener('change', () => {
          setPermissionStatus(result.state)
        })
      })
      .catch((err) => {
        console.error('Failed to query geolocation permission:', err)
      })
  }, [])

  // Handle geolocation success
  const handleSuccess = useCallback(
    (position: GeolocationPosition) => {
      const newLocation: Location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      }
      setUserLocation(newLocation)
      setError(null)
      setLoading(false)

      if (import.meta.env.DEV) {
        console.log('[Geolocation] Success:', newLocation)
      }
    },
    [setUserLocation]
  )

  // Handle geolocation error
  const handleError = useCallback((err: GeolocationPositionError) => {
    const errorMap: Record<number, string> = {
      1: '위치 정보 접근 권한이 거부되었습니다.',
      2: '위치 정보를 사용할 수 없습니다.',
      3: '위치 정보 요청 시간이 초과되었습니다.',
    }

    const locationError: LocationError = {
      code: err.code,
      message: errorMap[err.code] || '알 수 없는 오류가 발생했습니다.',
    }

    setError(locationError)
    setLoading(false)

    // Set default location on error
    setUserLocation(DEFAULT_LOCATION)

    console.error('[Geolocation] Error:', locationError)
  }, [setUserLocation])

  // Request user location
  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError({
        code: 0,
        message: '이 브라우저는 위치 정보를 지원하지 않습니다.',
      })
      setUserLocation(DEFAULT_LOCATION)
      return
    }

    setLoading(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(handleSuccess, handleError, {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0,
    })
  }, [handleSuccess, handleError, setUserLocation])

  // Clear error
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // Auto-request location on mount if permission is granted
  useEffect(() => {
    if (permissionStatus === 'granted' && !userLocation) {
      requestLocation()
    }
  }, [permissionStatus, userLocation, requestLocation])

  return {
    location: userLocation,
    error,
    loading,
    requestLocation,
    clearError,
    permissionStatus,
  }
}

/**
 * Hook to watch user location changes
 */
export function useWatchLocation(): UseLocationReturn & { watchId: number | null } {
  const { userLocation, setUserLocation } = useLocationStore()
  const [error, setError] = useState<LocationError | null>(null)
  const [loading, setLoading] = useState(false)
  const [permissionStatus, setPermissionStatus] = useState<PermissionState | null>(null)
  const [watchId, setWatchId] = useState<number | null>(null)

  // Check geolocation permission status
  useEffect(() => {
    if (!navigator.permissions) return

    navigator.permissions
      .query({ name: 'geolocation' })
      .then((result) => {
        setPermissionStatus(result.state)
        result.addEventListener('change', () => {
          setPermissionStatus(result.state)
        })
      })
      .catch((err) => {
        console.error('Failed to query geolocation permission:', err)
      })
  }, [])

  // Handle geolocation success
  const handleSuccess = useCallback(
    (position: GeolocationPosition) => {
      const newLocation: Location = {
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
      }
      setUserLocation(newLocation)
      setError(null)
      setLoading(false)

      if (import.meta.env.DEV) {
        console.log('[Geolocation Watch] Update:', newLocation)
      }
    },
    [setUserLocation]
  )

  // Handle geolocation error
  const handleError = useCallback((err: GeolocationPositionError) => {
    const errorMap: Record<number, string> = {
      1: '위치 정보 접근 권한이 거부되었습니다.',
      2: '위치 정보를 사용할 수 없습니다.',
      3: '위치 정보 요청 시간이 초과되었습니다.',
    }

    const locationError: LocationError = {
      code: err.code,
      message: errorMap[err.code] || '알 수 없는 오류가 발생했습니다.',
    }

    setError(locationError)
    setLoading(false)
    console.error('[Geolocation Watch] Error:', locationError)
  }, [])

  // Start watching location
  const requestLocation = useCallback(() => {
    if (!navigator.geolocation) {
      setError({
        code: 0,
        message: '이 브라우저는 위치 정보를 지원하지 않습니다.',
      })
      return
    }

    // Clear existing watch
    if (watchId !== null) {
      navigator.geolocation.clearWatch(watchId)
    }

    setLoading(true)
    setError(null)

    const id = navigator.geolocation.watchPosition(handleSuccess, handleError, {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 30000, // 30 seconds
    })

    setWatchId(id)
  }, [watchId, handleSuccess, handleError])

  // Clear error
  const clearError = useCallback(() => {
    setError(null)
  }, [])

  // Cleanup watch on unmount
  useEffect(() => {
    return () => {
      if (watchId !== null) {
        navigator.geolocation.clearWatch(watchId)
      }
    }
  }, [watchId])

  return {
    location: userLocation,
    error,
    loading,
    requestLocation,
    clearError,
    permissionStatus,
    watchId,
  }
}

/**
 * Calculate distance between two points using Haversine formula
 * Returns distance in meters
 */
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371e3 // Earth radius in meters
  const φ1 = (lat1 * Math.PI) / 180
  const φ2 = (lat2 * Math.PI) / 180
  const Δφ = ((lat2 - lat1) * Math.PI) / 180
  const Δλ = ((lon2 - lon1) * Math.PI) / 180

  const a =
    Math.sin(Δφ / 2) * Math.sin(Δφ / 2) +
    Math.cos(φ1) * Math.cos(φ2) * Math.sin(Δλ / 2) * Math.sin(Δλ / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))

  return R * c // Distance in meters
}

/**
 * Format distance for display
 */
export function formatDistance(distanceInMeters: number): string {
  if (distanceInMeters < 1000) {
    return `${Math.round(distanceInMeters)}m`
  }
  return `${(distanceInMeters / 1000).toFixed(1)}km`
}
