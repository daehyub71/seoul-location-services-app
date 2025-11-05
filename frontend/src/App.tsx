import { useState, useMemo } from 'react'
import KakaoMap from '@/components/map/KakaoMap'
import ResponsivePanel from '@/components/layout/ResponsivePanel'
import LocationInput from '@/components/location/LocationInput'
import CurrentLocation from '@/components/location/CurrentLocation'
import ServiceList from '@/components/services/ServiceList'
import ServiceDetail from '@/components/services/ServiceDetail'
import type { AnyService } from '@/types/services'
import { ServiceCategory } from '@/types/services'
import { useLocation } from '@/hooks/useLocation'
import { useNearbyServices } from '@/hooks/useServices'

// Mock data for testing (when API is not available)
const mockServices: AnyService[] = [
  {
    id: 'lib-1',
    category: ServiceCategory.LIBRARY,
    name: '서울시립 중앙도서관',
    latitude: 37.5665,
    longitude: 126.978,
    address: '서울특별시 중구 세종대로 110',
  },
  {
    id: 'lib-2',
    category: ServiceCategory.LIBRARY,
    name: '남산도서관',
    latitude: 37.5672,
    longitude: 126.9788,
    address: '서울특별시 중구 소월로 109',
  },
  {
    id: 'cult-1',
    category: ServiceCategory.CULTURAL_SPACE,
    name: '세종문화회관',
    latitude: 37.5720,
    longitude: 126.9762,
    address: '서울특별시 종로구 세종대로 175',
  },
  {
    id: 'lib-3',
    category: ServiceCategory.LIBRARY,
    name: '강남도서관',
    latitude: 37.5172,
    longitude: 127.0473,
    address: '서울특별시 강남구 테헤란로 87길 10',
  },
  {
    id: 'event-1',
    category: ServiceCategory.CULTURAL_EVENT,
    name: '코엑스 문화행사',
    latitude: 37.5130,
    longitude: 127.0590,
    address: '서울특별시 강남구 영동대로 513',
    event_period: '2025-11-01 ~ 2025-11-30',
  },
  {
    id: 'heritage-1',
    category: ServiceCategory.FUTURE_HERITAGE,
    name: '창덕궁',
    latitude: 37.5794,
    longitude: 126.9910,
    address: '서울특별시 종로구 율곡로 99',
  },
  {
    id: 'reserve-1',
    category: ServiceCategory.PUBLIC_RESERVATION,
    name: '서울시민청',
    latitude: 37.5662,
    longitude: 126.9779,
    address: '서울특별시 중구 세종대로 110',
    operating_hours: '평일 09:00-21:00',
  },
] as AnyService[]

function App() {
  const [selectedService, setSelectedService] = useState<AnyService | null>(null)
  const [detailModalOpen, setDetailModalOpen] = useState(false)
  const [searchLocation, setSearchLocation] = useState<{
    latitude: number
    longitude: number
  } | null>(null)
  const [searchRadius, setSearchRadius] = useState(5000) // 5km default

  const { location: userLocation } = useLocation()

  // Use search location or user location
  const activeLocation = searchLocation || userLocation

  // Fetch nearby services (only when location is available)
  const {
    data: servicesData,
    isLoading,
    error,
  } = useNearbyServices(
    {
      latitude: activeLocation?.latitude || 37.5665,
      longitude: activeLocation?.longitude || 126.978,
      radius: searchRadius,
    },
    {
      enabled: !!activeLocation,
    }
  )

  // Use API data if available, otherwise use mock data
  // Memoize to prevent unnecessary marker recreation
  const services = useMemo(() => {
    return servicesData?.data?.services || mockServices
  }, [servicesData?.data?.services])

  const handleServiceClick = (service: AnyService) => {
    setSelectedService(service)
    // Don't open modal - InfoWindow will be shown on map instead
    // setDetailModalOpen(true)
  }

  const handleMapClick = (_latitude: number, _longitude: number) => {
    // Optionally clear selection
    // setSelectedService(null)
  }

  const handleLocationSelect = (
    address: string,
    latitude: number,
    longitude: number
  ) => {
    console.log('Location selected:', { address, latitude, longitude })
    setSearchLocation({ latitude, longitude })
  }

  const handleCurrentLocationChange = (latitude: number, longitude: number) => {
    console.log('Current location updated:', { latitude, longitude })
    // Clear search location to use current location
    setSearchLocation(null)
  }

  return (
    <div className="h-screen w-screen flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b z-20 h-16 flex-shrink-0">
        <div className="px-6 py-4">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900">
            Seoul Location Services
          </h1>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 relative overflow-hidden">
        {/* Left Panel (Desktop) / Bottom Sheet (Mobile) */}
        <ResponsivePanel title="서비스 검색" isOpen={true}>
          <div className="flex flex-col h-full">
            {/* Location Controls */}
            <div className="flex-shrink-0 p-4 space-y-4 border-b bg-gray-50">
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  위치 설정
                </h3>
                <CurrentLocation onLocationChange={handleCurrentLocationChange} />
              </div>

              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-2">
                  주소 검색
                </h3>
                <LocationInput onLocationSelect={handleLocationSelect} />
              </div>

              <div>
                <label className="text-sm font-semibold text-gray-700 block mb-2">
                  검색 반경
                </label>
                <select
                  value={searchRadius}
                  onChange={(e) => setSearchRadius(Number(e.target.value))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value={1000}>1km</option>
                  <option value={2000}>2km</option>
                  <option value={5000}>5km</option>
                  <option value={10000}>10km</option>
                  <option value={20000}>20km</option>
                </select>
              </div>
            </div>

            {/* Service List */}
            <ServiceList
              services={services}
              loading={isLoading}
              error={error as Error}
              userLocation={activeLocation}
              onServiceClick={handleServiceClick}
              selectedServiceId={selectedService?.id}
              className="flex-1"
            />
          </div>
        </ResponsivePanel>

        {/* Map */}
        <div className="absolute inset-0 md:left-80">
          <KakaoMap
            services={services}
            onServiceClick={handleServiceClick}
            onMapClick={handleMapClick}
            userLocation={activeLocation}
            selectedService={selectedService}
            className="w-full h-full"
          />
        </div>
      </main>

      {/* Service Detail Modal */}
      <ServiceDetail
        service={selectedService}
        open={detailModalOpen}
        onOpenChange={setDetailModalOpen}
      />
    </div>
  )
}

export default App
