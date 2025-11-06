import { useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { MapPin, Navigation } from 'lucide-react'
import type { AnyService } from '@/types/services'
import { CATEGORY_COLORS, CATEGORY_LABELS } from '@/types/services'
import { formatDistance } from '@/hooks/useLocation'

interface MobileServiceCardsProps {
  services: AnyService[]
  onServiceClick?: (service: AnyService) => void
  selectedServiceId?: string | null
  className?: string
}

export default function MobileServiceCards({
  services,
  onServiceClick,
  selectedServiceId,
  className = '',
}: MobileServiceCardsProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to selected service
  useEffect(() => {
    if (selectedServiceId && scrollContainerRef.current) {
      const selectedCard = scrollContainerRef.current.querySelector(
        `[data-service-id="${selectedServiceId}"]`
      )
      if (selectedCard) {
        selectedCard.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
      }
    }
  }, [selectedServiceId])

  if (services.length === 0) {
    return null
  }

  return (
    <div className={`${className}`}>
      {/* Header */}
      <div className="px-4 py-2 bg-white/95 backdrop-blur-sm border-b">
        <p className="text-sm font-medium text-gray-700">
          주변 서비스 <span className="text-blue-600">{services.length}개</span>
        </p>
      </div>

      {/* Horizontal Scroll Cards */}
      <div
        ref={scrollContainerRef}
        className="flex gap-3 px-4 py-3 overflow-x-auto scrollbar-hide snap-x snap-mandatory bg-white/95 backdrop-blur-sm"
        style={{
          scrollbarWidth: 'none',
          msOverflowStyle: 'none',
        }}
      >
        {services.slice(0, 20).map((service) => {
          const categoryColor = CATEGORY_COLORS[service.category]
          const categoryLabel = CATEGORY_LABELS[service.category]
          const isSelected = selectedServiceId === service.id

          return (
            <motion.div
              key={service.id}
              data-service-id={service.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => onServiceClick?.(service)}
              className={`
                flex-shrink-0 w-64 snap-center
                bg-white rounded-xl shadow-lg
                border-2 transition-all cursor-pointer
                ${isSelected ? 'ring-2 ring-offset-2' : 'hover:shadow-xl'}
              `}
              style={{
                borderColor: isSelected ? categoryColor : '#e5e7eb',
                ringColor: categoryColor,
              }}
            >
              {/* Card Content */}
              <div className="p-4">
                {/* Header */}
                <div className="flex items-start justify-between gap-2 mb-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <div
                        className="w-2 h-2 rounded-full flex-shrink-0"
                        style={{ backgroundColor: categoryColor }}
                      />
                      <span
                        className="text-xs font-medium truncate"
                        style={{ color: categoryColor }}
                      >
                        {categoryLabel}
                      </span>
                    </div>
                    <h3 className="font-semibold text-gray-900 text-sm leading-tight line-clamp-2">
                      {service.name}
                    </h3>
                  </div>

                  {service.distance !== undefined && (
                    <div
                      className="flex-shrink-0 px-2 py-1 rounded-lg text-xs font-bold"
                      style={{
                        backgroundColor: `${categoryColor}15`,
                        color: categoryColor,
                      }}
                    >
                      {formatDistance(service.distance)}
                    </div>
                  )}
                </div>

                {/* Address */}
                {service.address && (
                  <div className="flex items-start gap-1.5 text-xs text-gray-600 mb-3">
                    <MapPin className="h-3 w-3 mt-0.5 flex-shrink-0" />
                    <span className="line-clamp-2 leading-tight">{service.address}</span>
                  </div>
                )}

                {/* Action Button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    onServiceClick?.(service)
                  }}
                  className="w-full py-2 px-3 rounded-lg text-xs font-medium text-white flex items-center justify-center gap-1.5 transition-all hover:brightness-110"
                  style={{ backgroundColor: categoryColor }}
                >
                  <Navigation className="h-3 w-3" />
                  상세보기
                </button>
              </div>
            </motion.div>
          )
        })}
      </div>

      {/* Scroll Hint */}
      {services.length > 3 && (
        <div className="absolute right-0 top-1/2 -translate-y-1/2 pointer-events-none">
          <div className="bg-gradient-to-l from-white/80 to-transparent w-8 h-full" />
        </div>
      )}
    </div>
  )
}
