import { useQuery, useMutation, UseQueryResult, UseMutationResult } from '@tanstack/react-query'
import {
  getNearbyServices,
  getServicesByCategory,
  getServiceDetail,
  geocodeAddress,
  reverseGeocode,
} from '@/services/api'
import type {
  NearbyServicesRequest,
  NearbyServicesResponse,
  ServiceCategory,
  ServiceDetailRequest,
  ServiceDetailResponse,
  GeocodeRequest,
  GeocodeResponse,
  ReverseGeocodeRequest,
  ReverseGeocodeResponse,
} from '@/types/services'

// Query Keys
export const servicesKeys = {
  all: ['services'] as const,
  nearby: (params: NearbyServicesRequest) => ['services', 'nearby', params] as const,
  byCategory: (category: ServiceCategory, lat: number, lon: number, radius: number) =>
    ['services', 'category', category, lat, lon, radius] as const,
  detail: (category: ServiceCategory, id: string) =>
    ['services', 'detail', category, id] as const,
  geocode: (address: string) => ['geocode', address] as const,
  reverseGeocode: (lat: number, lon: number) => ['geocode', 'reverse', lat, lon] as const,
}

// Cache time: 5 minutes
const CACHE_TIME = 1000 * 60 * 5

/**
 * Hook to fetch nearby services
 */
export function useNearbyServices(
  params: NearbyServicesRequest,
  options?: {
    enabled?: boolean
    staleTime?: number
  }
): UseQueryResult<NearbyServicesResponse, Error> {
  return useQuery({
    queryKey: servicesKeys.nearby(params),
    queryFn: () => getNearbyServices(params),
    staleTime: options?.staleTime ?? CACHE_TIME,
    enabled: options?.enabled ?? true,
    retry: 2,
  })
}

/**
 * Hook to fetch services by category
 */
export function useServicesByCategory(
  category: ServiceCategory,
  latitude: number,
  longitude: number,
  radius: number = 5000,
  options?: {
    enabled?: boolean
    staleTime?: number
  }
): UseQueryResult<NearbyServicesResponse, Error> {
  return useQuery({
    queryKey: servicesKeys.byCategory(category, latitude, longitude, radius),
    queryFn: () => getServicesByCategory(category, latitude, longitude, radius),
    staleTime: options?.staleTime ?? CACHE_TIME,
    enabled: options?.enabled ?? true,
    retry: 2,
  })
}

/**
 * Hook to fetch service detail
 */
export function useServiceDetail(
  params: ServiceDetailRequest,
  options?: {
    enabled?: boolean
    staleTime?: number
  }
): UseQueryResult<ServiceDetailResponse, Error> {
  return useQuery({
    queryKey: servicesKeys.detail(params.category, params.id),
    queryFn: () => getServiceDetail(params),
    staleTime: options?.staleTime ?? CACHE_TIME,
    enabled: options?.enabled ?? true,
    retry: 2,
  })
}

/**
 * Hook to geocode address (mutation for on-demand geocoding)
 */
export function useGeocode(): UseMutationResult<GeocodeResponse, Error, GeocodeRequest> {
  return useMutation({
    mutationFn: (params: GeocodeRequest) => geocodeAddress(params),
    retry: 1,
  })
}

/**
 * Hook to reverse geocode coordinates
 */
export function useReverseGeocode(
  latitude: number,
  longitude: number,
  options?: {
    enabled?: boolean
    staleTime?: number
  }
): UseQueryResult<ReverseGeocodeResponse, Error> {
  return useQuery({
    queryKey: servicesKeys.reverseGeocode(latitude, longitude),
    queryFn: () => reverseGeocode({ latitude, longitude }),
    staleTime: options?.staleTime ?? CACHE_TIME,
    enabled: options?.enabled ?? true,
    retry: 2,
  })
}

/**
 * Hook to reverse geocode coordinates (mutation for on-demand)
 */
export function useReverseGeocodeMutation(): UseMutationResult<
  ReverseGeocodeResponse,
  Error,
  ReverseGeocodeRequest
> {
  return useMutation({
    mutationFn: (params: ReverseGeocodeRequest) => reverseGeocode(params),
    retry: 1,
  })
}
