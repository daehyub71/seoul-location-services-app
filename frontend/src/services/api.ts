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

  // Map backend "services" to frontend format
  const services = (backendData.services || []).map((serviceItem: any) => {
    // Backend structure:
    // {
    //   id, title, category, category_label, icon,
    //   location: { lat, lon, distance },
    //   address, description, raw_data
    // }

    let latitude: number
    let longitude: number

    // Try to get coordinates from location object or raw_data
    if (serviceItem.location) {
      latitude = parseFloat(serviceItem.location.lat)
      longitude = parseFloat(serviceItem.location.lon)
    } else if (serviceItem.raw_data) {
      const raw = serviceItem.raw_data
      if (raw.y !== undefined && raw.y !== null) {
        latitude = parseFloat(raw.y)
        longitude = parseFloat(raw.x)
      } else if (raw.lat !== undefined && raw.lat !== null) {
        latitude = parseFloat(raw.lat)
        longitude = parseFloat(raw.lon !== undefined ? raw.lon : raw.lot)
      } else {
        latitude = parseFloat(raw.latitude)
        longitude = parseFloat(raw.longitude)
      }
    } else {
      latitude = 0
      longitude = 0
    }

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
      category: serviceItem.category,
      name: serviceItem.title,
      latitude,
      longitude,
      address: serviceItem.address,
      distance: serviceItem.location?.distance,
      description: serviceItem.description,
      icon: serviceItem.icon,
      category_label: serviceItem.category_label,
      // Preserve raw data for InfoWindow
      raw_data: serviceItem.raw_data,
    }

    // Add category-specific fields from raw_data
    if (serviceItem.raw_data) {
      const raw = serviceItem.raw_data
      if (raw.strtdate && raw.end_date) {
        service.event_period = `${raw.strtdate} ~ ${raw.end_date}`
      }
      service.use_fee = raw.use_fee || raw.is_free
      service.operating_hours = raw.opertime
      service.homepage = raw.homepage || raw.hmpg_addr || raw.org_link
    }

    return service
  })

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

// Helper function to map backend table names to frontend categories
function mapTableToCategory(tableName: string): string {
  const mapping: Record<string, string> = {
    'cultural_events': 'cultural_events',
    'culturalEventInfo': 'cultural_events',
    'libraries': 'libraries',
    'library': 'libraries',
    'cultural_spaces': 'cultural_spaces',
    'public_reservations': 'public_reservations',
    'future_heritage': 'future_heritage',
  }
  return mapping[tableName] || 'cultural_events'
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
 */
export async function geocodeAddress(params: GeocodeRequest): Promise<GeocodeResponse> {
  const response = await apiClient.post<GeocodeResponse>('/api/v1/geocode', params)
  return response.data
}

/**
 * Reverse geocode coordinates to address
 */
export async function reverseGeocode(
  params: ReverseGeocodeRequest
): Promise<ReverseGeocodeResponse> {
  const response = await apiClient.post<ReverseGeocodeResponse>(
    '/api/v1/geocode/reverse',
    params
  )
  return response.data
}

// Export axios instance for custom requests
export { apiClient }
export default apiClient
