import { useState, useMemo, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Filter, SortAsc, Loader2, AlertCircle, Inbox, RefreshCw } from 'lucide-react'
import type { AnyService } from '@/types/services'
import { ServiceCategory, CATEGORY_LABELS, CATEGORY_COLORS } from '@/types/services'
import ServiceListItem from './ServiceListItem'
import { calculateDistance } from '@/hooks/useLocation'
import { ServiceListSkeleton } from '@/components/ui/skeleton'
import { Button } from '@/components/ui/button'

export type SortOption = 'distance' | 'name' | 'date'

export interface ServiceListProps {
  services: AnyService[]
  loading?: boolean
  error?: Error | null
  userLocation?: { latitude: number; longitude: number } | null
  onServiceClick?: (service: AnyService) => void
  selectedServiceId?: string | null
  onRetry?: () => void
  className?: string
}

export default function ServiceList({
  services,
  loading = false,
  error = null,
  userLocation,
  onServiceClick,
  selectedServiceId,
  onRetry,
  className = '',
}: ServiceListProps) {
  const [selectedCategories, setSelectedCategories] = useState<Set<ServiceCategory>>(
    new Set(Object.values(ServiceCategory))
  )
  const [sortBy, setSortBy] = useState<SortOption>('distance')
  const [showFilters, setShowFilters] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)
  const [page, setPage] = useState(1)
  const ITEMS_PER_PAGE = 20

  // Calculate distances for all services
  const servicesWithDistance = useMemo(() => {
    return services.map((service) => ({
      ...service,
      distance: userLocation
        ? calculateDistance(
            userLocation.latitude,
            userLocation.longitude,
            service.latitude,
            service.longitude
          )
        : undefined,
    }))
  }, [services, userLocation])

  // Filter and sort services
  const filteredAndSortedServices = useMemo(() => {
    let result = servicesWithDistance.filter((service) =>
      selectedCategories.has(service.category)
    )

    // Sort services
    result.sort((a, b) => {
      switch (sortBy) {
        case 'distance':
          if (a.distance === undefined) return 1
          if (b.distance === undefined) return -1
          return a.distance - b.distance

        case 'name':
          return a.name.localeCompare(b.name, 'ko')

        case 'date': {
          // For events, sort by date; for others, by name
          const aDate = (a as any).strtdate || (a as any).svcopnbgndt || ''
          const bDate = (b as any).strtdate || (b as any).svcopnbgndt || ''
          if (aDate && bDate) {
            return bDate.localeCompare(aDate) // Newest first
          }
          return a.name.localeCompare(b.name, 'ko')
        }

        default:
          return 0
      }
    })

    return result
  }, [servicesWithDistance, selectedCategories, sortBy])

  // Paginated services for infinite scroll
  const paginatedServices = useMemo(() => {
    return filteredAndSortedServices.slice(0, page * ITEMS_PER_PAGE)
  }, [filteredAndSortedServices, page])

  // Infinite scroll handler
  useEffect(() => {
    const listElement = listRef.current
    if (!listElement) return

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = listElement
      if (scrollTop + clientHeight >= scrollHeight - 100) {
        // Load more when near bottom
        if (paginatedServices.length < filteredAndSortedServices.length) {
          setPage((prev) => prev + 1)
        }
      }
    }

    listElement.addEventListener('scroll', handleScroll)
    return () => listElement.removeEventListener('scroll', handleScroll)
  }, [paginatedServices.length, filteredAndSortedServices.length])

  // Reset page when filters or sort changes
  useEffect(() => {
    setPage(1)
  }, [selectedCategories, sortBy])

  const toggleCategory = (category: ServiceCategory) => {
    const newCategories = new Set(selectedCategories)
    if (newCategories.has(category)) {
      newCategories.delete(category)
    } else {
      newCategories.add(category)
    }
    setSelectedCategories(newCategories)
  }

  const toggleAllCategories = () => {
    if (selectedCategories.size === Object.values(ServiceCategory).length) {
      setSelectedCategories(new Set())
    } else {
      setSelectedCategories(new Set(Object.values(ServiceCategory)))
    }
  }

  // Loading state
  if (loading) {
    return (
      <div className={`flex flex-col h-full ${className}`}>
        <div className="flex-shrink-0 p-4 border-b bg-white">
          <h2 className="text-lg font-bold text-gray-900">
            서비스 목록
            <span className="ml-2 text-sm font-normal text-gray-500">로딩 중...</span>
          </h2>
        </div>
        <div className="flex-1 overflow-y-auto p-4">
          <ServiceListSkeleton count={5} />
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className={`flex flex-col items-center justify-center h-full p-6 ${className}`}>
        <div className="max-w-sm w-full bg-red-50 border border-red-200 rounded-lg p-6 space-y-4">
          <div className="flex items-center gap-3 text-red-600">
            <AlertCircle className="h-8 w-8 flex-shrink-0" />
            <h3 className="font-bold text-lg">서비스를 불러올 수 없습니다</h3>
          </div>
          <p className="text-sm text-gray-700">{error.message}</p>
          {onRetry && (
            <Button onClick={onRetry} className="w-full" variant="default">
              <RefreshCw className="mr-2 h-4 w-4" />
              다시 시도
            </Button>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className={`flex flex-col h-full ${className}`}>
      {/* Header with filters and sort */}
      <div className="flex-shrink-0 p-4 border-b bg-white">
        <div className="flex items-center justify-between gap-2 mb-3">
          <h2 className="text-lg font-bold text-gray-900">
            서비스 목록
            <span className="ml-2 text-sm font-normal text-gray-500">
              ({filteredAndSortedServices.length}개)
            </span>
          </h2>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className={`
              p-2 rounded-lg transition-all
              ${showFilters ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'}
            `}
            aria-label="Toggle filters"
          >
            <Filter className="h-4 w-4" />
          </button>
        </div>

        <AnimatePresence>
          {showFilters && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="space-y-3 overflow-hidden"
            >
              {/* Category filters */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-xs font-medium text-gray-700">카테고리</label>
                  <button
                    onClick={toggleAllCategories}
                    className="text-xs text-blue-600 hover:underline"
                  >
                    {selectedCategories.size === Object.values(ServiceCategory).length
                      ? '전체 해제'
                      : '전체 선택'}
                  </button>
                </div>
                <div className="flex flex-wrap gap-2">
                  {Object.values(ServiceCategory).map((category) => {
                    const isSelected = selectedCategories.has(category)
                    const color = CATEGORY_COLORS[category]
                    return (
                      <button
                        key={category}
                        onClick={() => toggleCategory(category)}
                        className={`
                          px-3 py-1.5 rounded-full text-xs font-medium transition-all
                          ${isSelected ? 'text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}
                        `}
                        style={{
                          backgroundColor: isSelected ? color : undefined,
                        }}
                      >
                        {CATEGORY_LABELS[category]}
                      </button>
                    )
                  })}
                </div>
              </div>

              {/* Sort options */}
              <div>
                <label className="text-xs font-medium text-gray-700 mb-2 flex items-center gap-1">
                  <SortAsc className="h-3 w-3" />
                  정렬
                </label>
                <div className="flex gap-2">
                  {[
                    { value: 'distance' as SortOption, label: '거리순' },
                    { value: 'name' as SortOption, label: '이름순' },
                    { value: 'date' as SortOption, label: '날짜순' },
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => setSortBy(option.value)}
                      className={`
                        px-3 py-1.5 rounded-lg text-xs font-medium transition-all
                        ${
                          sortBy === option.value
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }
                      `}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Service list */}
      <div ref={listRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        <AnimatePresence mode="popLayout">
          {paginatedServices.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex flex-col items-center justify-center h-full text-center p-6"
            >
              <Inbox className="h-12 w-12 text-gray-400 mb-3" />
              <p className="text-sm font-medium text-gray-900 mb-1">
                검색 결과가 없습니다
              </p>
              <p className="text-xs text-gray-600">
                다른 카테고리나 위치를 선택해보세요.
              </p>
            </motion.div>
          ) : (
            paginatedServices.map((service) => (
              <ServiceListItem
                key={service.id}
                service={service}
                onClick={onServiceClick}
                isSelected={selectedServiceId === service.id}
              />
            ))
          )}
        </AnimatePresence>

        {/* Load more indicator */}
        {paginatedServices.length < filteredAndSortedServices.length && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-5 w-5 text-gray-400 animate-spin" />
            <span className="ml-2 text-sm text-gray-600">더 불러오는 중...</span>
          </div>
        )}
      </div>
    </div>
  )
}
