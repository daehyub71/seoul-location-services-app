import { memo } from 'react'
import { motion } from 'framer-motion'
import { MapPin, Calendar, Phone, Globe, Clock, Heart } from 'lucide-react'
import type { AnyService } from '@/types/services'
import { CATEGORY_COLORS, CATEGORY_LABELS, ServiceCategory } from '@/types/services'
import { formatDistance } from '@/hooks/useLocation'
import { useFavorites } from '@/hooks/useFavorites'

export interface ServiceListItemProps {
  service: AnyService
  onClick?: (service: AnyService) => void
  isSelected?: boolean
}

function ServiceListItem({
  service,
  onClick,
  isSelected = false,
}: ServiceListItemProps) {
  const categoryColor = CATEGORY_COLORS[service.category]
  const categoryLabel = CATEGORY_LABELS[service.category]
  const { isFavorite, toggleFavorite } = useFavorites()
  const favorite = isFavorite(service.id)

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation()
    toggleFavorite(service.id, service.name, service.category)
  }

  // Get thumbnail image
  const thumbnailUrl = getThumbnailUrl(service)

  const renderServiceDetails = () => {
    switch (service.category) {
      case ServiceCategory.LIBRARY: {
        const lib = service as any
        return (
          <>
            {lib.tel_no && (
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Phone className="h-3 w-3" />
                {lib.tel_no}
              </div>
            )}
            {lib.operTime && (
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Clock className="h-3 w-3" />
                {lib.operTime}
              </div>
            )}
            {lib.homepage && (
              <div className="flex items-center gap-2 text-xs text-blue-600 truncate">
                <Globe className="h-3 w-3 flex-shrink-0" />
                <a
                  href={lib.homepage}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline truncate"
                  onClick={(e) => e.stopPropagation()}
                >
                  웹사이트
                </a>
              </div>
            )}
          </>
        )
      }

      case ServiceCategory.CULTURAL_EVENT: {
        const event = service as any
        return (
          <>
            {event.event_period && (
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Calendar className="h-3 w-3" />
                {event.event_period}
              </div>
            )}
            {event.use_fee && (
              <div className="text-xs text-gray-600">
                <span className="font-medium">이용료:</span> {event.use_fee}
              </div>
            )}
          </>
        )
      }

      case ServiceCategory.CULTURAL_SPACE: {
        const space = service as any
        return (
          <>
            {space.tel_no && (
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Phone className="h-3 w-3" />
                {space.tel_no}
              </div>
            )}
            {space.openTime && (
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Clock className="h-3 w-3" />
                {space.openTime}
              </div>
            )}
          </>
        )
      }

      case ServiceCategory.PUBLIC_RESERVATION: {
        const reservation = service as any
        return (
          <>
            {reservation.usetgtinfo && (
              <div className="text-xs text-gray-600">
                <span className="font-medium">이용대상:</span> {reservation.usetgtinfo}
              </div>
            )}
            {reservation.rcptbgndt && reservation.rcptenddt && (
              <div className="flex items-center gap-2 text-xs text-gray-600">
                <Calendar className="h-3 w-3" />
                {reservation.rcptbgndt} ~ {reservation.rcptenddt}
              </div>
            )}
          </>
        )
      }

      case ServiceCategory.FUTURE_HERITAGE: {
        const heritage = service as any
        return (
          <>
            {heritage.category_name && (
              <div className="text-xs text-gray-600">
                <span className="font-medium">분류:</span> {heritage.category_name}
              </div>
            )}
            {heritage.description && (
              <div className="text-xs text-gray-600 line-clamp-2">
                {heritage.description}
              </div>
            )}
          </>
        )
      }

      default:
        return null
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      whileHover={{ scale: 1.02 }}
      onClick={() => onClick?.(service)}
      className={`
        border rounded-lg cursor-pointer transition-all overflow-hidden
        hover:shadow-md
        ${
          isSelected
            ? `border-2 shadow-md`
            : 'border-gray-200 hover:border-gray-300'
        }
      `}
      style={{
        borderColor: isSelected ? categoryColor : undefined,
        backgroundColor: isSelected ? `${categoryColor}08` : 'white',
      }}
    >
      <div className="flex gap-3">
        {/* Thumbnail Image */}
        {thumbnailUrl && (
          <div className="w-24 h-24 flex-shrink-0 bg-gray-100">
            <img
              src={thumbnailUrl}
              alt={service.name}
              className="w-full h-full object-cover"
              loading="lazy"
              onError={(e) => {
                e.currentTarget.style.display = 'none'
              }}
            />
          </div>
        )}

        {/* Content */}
        <div className="flex-1 p-3 min-w-0">
          {/* Header */}
          <div className="flex items-start justify-between gap-2 mb-2">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <div
                  className="w-2 h-2 rounded-full flex-shrink-0"
                  style={{ backgroundColor: categoryColor }}
                />
                <span
                  className="text-xs font-medium"
                  style={{ color: categoryColor }}
                >
                  {categoryLabel}
                </span>
              </div>
              <h3 className="font-semibold text-gray-900 leading-tight truncate">
                {service.name}
              </h3>
            </div>

            {/* Distance and Favorite */}
            <div className="flex items-center gap-1 flex-shrink-0">
              {service.distance !== undefined && (
                <div className="text-xs font-medium text-gray-700 bg-gray-100 px-2 py-1 rounded">
                  {formatDistance(service.distance)}
                </div>
              )}
              <button
                onClick={handleFavoriteClick}
                className={`p-1.5 rounded-full transition-all ${
                  favorite
                    ? 'text-red-500 hover:bg-red-50'
                    : 'text-gray-400 hover:bg-gray-100'
                }`}
                aria-label={favorite ? 'Remove from favorites' : 'Add to favorites'}
              >
                <Heart className={`h-4 w-4 ${favorite ? 'fill-current' : ''}`} />
              </button>
            </div>
          </div>

          {/* Address */}
          {service.address && (
            <div className="flex items-start gap-2 text-xs text-gray-600 mb-2">
              <MapPin className="h-3 w-3 mt-0.5 flex-shrink-0" />
              <span className="line-clamp-1">{service.address}</span>
            </div>
          )}

          {/* Service-specific details */}
          <div className="space-y-1">{renderServiceDetails()}</div>
        </div>
      </div>
    </motion.div>
  )
}

// Helper function to get thumbnail URL
function getThumbnailUrl(service: AnyService): string | null {
  const anyService = service as any
  return anyService.main_img || anyService.imgurl || null
}

// Memoize component to prevent unnecessary re-renders
const MemoizedServiceListItem = memo(ServiceListItem, (prevProps, nextProps) => {
  return (
    prevProps.service.id === nextProps.service.id &&
    prevProps.isSelected === nextProps.isSelected &&
    prevProps.service.distance === nextProps.service.distance
  )
})

MemoizedServiceListItem.displayName = 'ServiceListItem'

export default MemoizedServiceListItem
