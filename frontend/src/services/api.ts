import axios, { AxiosError, AxiosInstance } from 'axios'
import type {
  NearbyServicesRequest,
  NearbyServicesResponse,
  ServiceDetailRequest,
  ServiceDetailResponse,
  GeocodeRequest,
  GeocodeResponse,
  ReverseGeocodeRequest,
  ReverseGeocodeResponse,
  ApiErrorResponse,
  ServiceCategory,
} from '@/types/services'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const API_TIMEOUT = 30000 // 30 seconds

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: API_TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add timestamp to prevent caching
    config.params = {
      ...config.params,
      _t: Date.now(),
    }

    // Log request in development
    if (import.meta.env.DEV) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      })
    }

    return config
  },
  (error) => {
    console.error('[API Request Error]', error)
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (import.meta.env.DEV) {
      console.log(`[API Response] ${response.config.url}`, response.data)
    }

    return response
  },
  (error: AxiosError<ApiErrorResponse>) => {
    // Handle error responses
    const errorMessage = error.response?.data?.message || error.message || 'Unknown error occurred'

    console.error('[API Response Error]', {
      url: error.config?.url,
      status: error.response?.status,
      message: errorMessage,
      details: error.response?.data?.details,
    })

    // Customize error based on status code
    if (error.response?.status === 401) {
      // Handle unauthorized
      console.error('Unauthorized access')
    } else if (error.response?.status === 403) {
      // Handle forbidden
      console.error('Access forbidden')
    } else if (error.response?.status === 404) {
      // Handle not found
      console.error('Resource not found')
    } else if (error.response?.status === 500) {
      // Handle server error
      console.error('Server error')
    } else if (error.code === 'ECONNABORTED') {
      // Handle timeout
      console.error('Request timeout')
    }

    return Promise.reject(error)
  }
)

// API Functions

/**
 * Get nearby services within a radius
 */
export async function getNearbyServices(
  params: NearbyServicesRequest
): Promise<NearbyServicesResponse> {
  // Backend expects lat/lon instead of latitude/longitude
  const queryParams = {
    lat: params.latitude,
    lon: params.longitude,
    radius: params.radius,
    categories: params.categories?.join(','),
    limit: params.limit,
  }

  const response = await apiClient.get<any>('/api/v1/services/nearby', {
    params: queryParams,
  })

  // Transform backend response to match frontend types
  const backendData = response.data

  console.log('[API] Backend response:', backendData)
  console.log('[API] Services count:', (backendData.services || backendData.locations || []).length)

  // Map backend "services" to frontend format
  // Backend may return either "services" or "locations" key depending on endpoint
  const services = (backendData.services || backendData.locations || [])
    .map((serviceItem: any) => {
      // Backend structure from simple_app.py:
      // {
      //   id, api_id, latitude, longitude, _table, distance, distance_formatted,
      //   library_name/fac_name/title/svcnm/name, address, ...other fields
      // }

      // Extract coordinates - backend provides normalized 'location' object
      // Fallback to various field names for compatibility:
      // - location.lat, location.lon (preferred - normalized by backend)
      // - raw_data.lat, raw_data.lot (cultural_events)
      // - latitude, longitude (libraries, future_heritages)
      // - y_coord, x_coord (public_reservations)
      let latitude: number = serviceItem.location?.lat || serviceItem.latitude || serviceItem.lat || serviceItem.y_coord || 0
      let longitude: number = serviceItem.location?.lon || serviceItem.longitude || serviceItem.lon || serviceItem.lot || serviceItem.x_coord || 0

      // Validate coordinates
      if (isNaN(latitude) || isNaN(longitude)) {
        console.warn('[API] Invalid coordinates for service', {
          service: serviceItem,
          parsedLat: latitude,
          parsedLon: longitude
        })
        latitude = 0
        longitude = 0
      }

      const service: any = {
        id: serviceItem.id,
        category: serviceItem.category, // Backend already provides normalized category
        name: serviceItem.title || serviceItem.library_name || serviceItem.fac_name || serviceItem.svcnm || serviceItem.name,
        latitude,
        longitude,
        address: serviceItem.address || serviceItem.addr,
        distance: serviceItem.location?.distance || serviceItem.distance,
        distance_formatted: serviceItem.distance_formatted,
        // Preserve all fields for InfoWindow
        ...serviceItem,
      }

      return service
    })
    .filter((service: any) => {
      // Filter out services with invalid coordinates (0, 0) or missing data
      // Seoul coordinates are roughly: latitude 37.4-37.7, longitude 126.7-127.2
      const hasValidCoords = service.latitude !== 0 && service.longitude !== 0 &&
                             !isNaN(service.latitude) && !isNaN(service.longitude) &&
                             service.latitude >= 33 && service.latitude <= 39 && // South Korea bounds
                             service.longitude >= 124 && service.longitude <= 132 // South Korea bounds

      if (!hasValidCoords) {
        console.warn('[API] Filtering out service with invalid coordinates:', {
          id: service.id,
          name: service.name,
          latitude: service.latitude,
          longitude: service.longitude
        })
      }

      return hasValidCoords
    })

  console.log('[API] Valid services after filtering:', services.length)

  return {
    success: backendData.success !== false,
    data: {
      services,
      total: services.length,
      query: {
        latitude: params.latitude,
        longitude: params.longitude,
        radius: params.radius,
        categories: params.categories || [],
      },
    },
    message: backendData.message,
  }
}

/**
 * Get services by category
 */
export async function getServicesByCategory(
  category: ServiceCategory,
  latitude: number,
  longitude: number,
  radius: number = 5000
): Promise<NearbyServicesResponse> {
  return getNearbyServices({
    latitude,
    longitude,
    radius,
    categories: [category],
  })
}

/**
 * Get service detail by ID
 */
export async function getServiceDetail(
  params: ServiceDetailRequest
): Promise<ServiceDetailResponse> {
  const { category, id } = params
  const response = await apiClient.get<ServiceDetailResponse>(
    `/api/v1/services/${category}/${id}`
  )
  return response.data
}

/**
 * Geocode address to coordinates
 * Uses Kakao Maps SDK Geocoder (no backend API needed)
 */
export async function geocodeAddress(params: GeocodeRequest): Promise<GeocodeResponse> {
  const { geocodeAddress: geocode } = await import('./kakao-geocoding')
  const result = await geocode(params.address)
  return {
    success: result.success,
    latitude: result.latitude,
    longitude: result.longitude,
    address: result.address || params.address,
  }
}

/**
 * Reverse geocode coordinates to address
 * Uses Kakao Maps SDK Geocoder (no backend API needed)
 */
export async function reverseGeocode(
  params: ReverseGeocodeRequest
): Promise<ReverseGeocodeResponse> {
  const { reverseGeocode: revGeocode } = await import('./kakao-geocoding')
  const result = await revGeocode(params.latitude, params.longitude)
  return {
    success: result.success,
    data: {
      address: result.address || '',
      sido: '',
      sigungu: '',
      dong: '',
      latitude: result.latitude,
      longitude: result.longitude,
    },
  }
}

// Export axios instance for custom requests
export { apiClient }
export default apiClient
