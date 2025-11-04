import { useEffect } from 'react'
import { useKakaoMap } from '@/hooks/useKakaoMap'
import { useLocation } from '@/hooks/useLocation'
import { useLocationStore } from '@/stores/locationStore'
import type { AnyService } from '@/types/services'
import MarkerCluster from './MarkerCluster'
import { MapSkeleton } from '@/components/ui/skeleton'

interface KakaoMapProps {
  services?: AnyService[]
  onServiceClick?: (service: AnyService) => void
  onMapClick?: (latitude: number, longitude: number) => void
  userLocation?: { latitude: number; longitude: number } | null
  className?: string
}

export default function KakaoMap({
  services = [],
  onServiceClick,
  onMapClick,
  userLocation: propUserLocation,
  className = '',
}: KakaoMapProps) {
  const { userLocation: storeUserLocation } = useLocationStore()
  const { location: currentLocation, requestLocation } = useLocation()

  // Use prop location if provided, otherwise use store location
  const userLocation = propUserLocation || currentLocation || storeUserLocation

  const {
    map,
    isLoaded,
    error,
    setCenter,
    relayout,
  } = useKakaoMap({
    containerId: 'kakao-map',
    initialCenter: userLocation || {
      latitude: 37.5665, // Seoul City Hall
      longitude: 126.978,
    },
    initialZoom: 6, // 더 확대된 상태로 시작 (숫자가 작을수록 더 확대)
    onMapClick,
    enabled: true, // Container is always in DOM now
  })

  // Update map center when user location changes
  useEffect(() => {
    if (currentLocation && isLoaded) {
      setCenter(currentLocation.latitude, currentLocation.longitude)
    }
  }, [currentLocation, isLoaded, setCenter])

  // Request location on mount
  useEffect(() => {
    if (!currentLocation) {
      requestLocation()
    }
  }, [currentLocation, requestLocation])

  // Handle window resize and call relayout
  useEffect(() => {
    if (!isLoaded || !relayout) return

    const handleResize = () => {
      console.log('[KakaoMap] Window resized, calling relayout')
      relayout()
    }

    // Call relayout on mount
    relayout()

    // Listen for resize events
    window.addEventListener('resize', handleResize)

    // Also listen for orientation change (mobile)
    window.addEventListener('orientationchange', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      window.removeEventListener('orientationchange', handleResize)
    }
  }, [isLoaded, relayout])

  return (
    <div className={`relative ${className}`}>
      {/* Map Container - Always rendered */}
      <div id="kakao-map" className="w-full h-full" />

      {/* Marker Cluster - Render when map is loaded */}
      {isLoaded && map && (
        <MarkerCluster
          map={map}
          services={services}
          userLocation={currentLocation || userLocation}
          clusterThreshold={500}
          onServiceClick={onServiceClick}
        />
      )}

      {/* Error Overlay */}
      {error && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100 z-20">
          <div className="text-center p-8 max-w-2xl">
            <div className="text-red-500 text-lg font-semibold mb-3">
              지도를 불러올 수 없습니다
            </div>
            <div className="text-gray-700 text-sm mb-4 bg-red-50 p-4 rounded-lg border border-red-200">
              {error}
            </div>
            <div className="text-left text-sm text-gray-600 space-y-2 bg-white p-4 rounded-lg border">
              <p className="font-semibold mb-2">문제 해결 방법:</p>
              <ol className="list-decimal list-inside space-y-1">
                <li>
                  <a
                    href="https://developers.kakao.com/console/app"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Kakao Developers 콘솔
                  </a>에서 앱 설정 확인
                </li>
                <li>앱 키가 <strong>JavaScript 키</strong>인지 확인 (REST API 키 아님)</li>
                <li>플랫폼 설정 → 웹 플랫폼 등록 → <code className="bg-gray-100 px-1 rounded">http://localhost:5173</code> 추가</li>
                <li>사이트 도메인 저장 후 5-10분 대기</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* Loading Overlay */}
      {!isLoaded && !error && (
        <div className="absolute inset-0 z-20">
          <MapSkeleton />
        </div>
      )}

      {/* Map Controls Overlay - Only shown when loaded */}
      {isLoaded && (
        <>
          <div className="absolute top-4 left-4 z-10 space-y-2">
            {/* Current Location Button */}
            <button
              onClick={() => {
                if (currentLocation) {
                  setCenter(currentLocation.latitude, currentLocation.longitude)
                } else {
                  requestLocation()
                }
              }}
              className="bg-white rounded-lg shadow-md p-3 hover:bg-gray-50 transition-colors"
              title="내 위치로 이동"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-gray-700"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </button>
          </div>

          {/* Map Info Overlay */}
          <div className="absolute bottom-4 left-4 z-10 bg-white rounded-lg shadow-md px-4 py-2">
            <div className="flex items-center space-x-4 text-sm">
              <div className="text-gray-600">
                서비스: <span className="font-semibold text-gray-900">{services.length}</span>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
