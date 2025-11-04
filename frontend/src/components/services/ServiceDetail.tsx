import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import type { AnyService } from '@/types/services'
import { CATEGORY_COLORS, CATEGORY_LABELS, ServiceCategory } from '@/types/services'
import { useFavorites } from '@/hooks/useFavorites'
import {
  MapPin,
  Phone,
  Globe,
  Clock,
  Calendar,
  Navigation,
  Share2,
  Heart,
  ExternalLink,
  ChevronLeft,
  ChevronRight,
  X,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export interface ServiceDetailProps {
  service: AnyService | null
  open: boolean
  onOpenChange: (open: boolean) => void
}

export default function ServiceDetail({
  service,
  open,
  onOpenChange,
}: ServiceDetailProps) {
  const [currentImageIndex, setCurrentImageIndex] = useState(0)
  const { isFavorite, toggleFavorite } = useFavorites()

  if (!service) return null

  const categoryColor = CATEGORY_COLORS[service.category]
  const categoryLabel = CATEGORY_LABELS[service.category]
  const favorite = isFavorite(service.id)

  // Get images for the service
  const images = getServiceImages(service)
  const hasImages = images.length > 0

  const handleShare = async () => {
    const shareData = {
      title: service.name,
      text: `${service.name} - ${categoryLabel}`,
      url: window.location.href,
    }

    if (navigator.share) {
      try {
        await navigator.share(shareData)
      } catch (error) {
        console.error('Share failed:', error)
      }
    } else {
      // Fallback: Copy to clipboard
      try {
        await navigator.clipboard.writeText(
          `${service.name}\n${service.address || ''}\n${window.location.href}`
        )
        alert('링크가 클립보드에 복사되었습니다!')
      } catch (error) {
        console.error('Copy failed:', error)
      }
    }
  }

  const handleDirections = () => {
    // Open Kakao Map with directions
    const kakaoMapUrl = `https://map.kakao.com/link/to/${encodeURIComponent(
      service.name
    )},${service.latitude},${service.longitude}`
    window.open(kakaoMapUrl, '_blank')
  }

  const handleToggleFavorite = () => {
    toggleFavorite(service.id, service.name, service.category)
  }

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % images.length)
  }

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Image Slider */}
        {hasImages && (
          <div className="relative -mx-6 -mt-6 mb-4">
            <div className="relative h-64 bg-gray-100">
              <AnimatePresence mode="wait">
                <motion.img
                  key={currentImageIndex}
                  src={images[currentImageIndex]}
                  alt={service.name}
                  className="w-full h-full object-cover"
                  loading="lazy"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                  onError={(e) => {
                    e.currentTarget.src = 'https://via.placeholder.com/800x400?text=No+Image'
                  }}
                />
              </AnimatePresence>

              {/* Image navigation */}
              {images.length > 1 && (
                <>
                  <button
                    onClick={prevImage}
                    className="absolute left-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white p-2 rounded-full shadow-lg transition-all"
                    aria-label="Previous image"
                  >
                    <ChevronLeft className="h-5 w-5" />
                  </button>
                  <button
                    onClick={nextImage}
                    className="absolute right-2 top-1/2 -translate-y-1/2 bg-white/80 hover:bg-white p-2 rounded-full shadow-lg transition-all"
                    aria-label="Next image"
                  >
                    <ChevronRight className="h-5 w-5" />
                  </button>

                  {/* Image indicator */}
                  <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex gap-2">
                    {images.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setCurrentImageIndex(index)}
                        className={`w-2 h-2 rounded-full transition-all ${
                          index === currentImageIndex
                            ? 'bg-white w-4'
                            : 'bg-white/50'
                        }`}
                        aria-label={`Go to image ${index + 1}`}
                      />
                    ))}
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* Header */}
        <DialogHeader>
          <div className="flex items-start justify-between gap-4">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-2">
                <div
                  className="px-2 py-1 rounded text-xs font-medium text-white"
                  style={{ backgroundColor: categoryColor }}
                >
                  {categoryLabel}
                </div>
                {service.distance !== undefined && (
                  <div className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                    {formatDistance(service.distance)}
                  </div>
                )}
              </div>
              <DialogTitle className="text-2xl">{service.name}</DialogTitle>
            </div>

            {/* Favorite button */}
            <button
              onClick={handleToggleFavorite}
              className={`p-2 rounded-full transition-all ${
                favorite
                  ? 'bg-red-50 text-red-500 hover:bg-red-100'
                  : 'bg-gray-100 text-gray-400 hover:bg-gray-200'
              }`}
              aria-label={favorite ? 'Remove from favorites' : 'Add to favorites'}
            >
              <Heart className={`h-5 w-5 ${favorite ? 'fill-current' : ''}`} />
            </button>
          </div>
        </DialogHeader>

        {/* Service Details */}
        <div className="space-y-4">
          {/* Address */}
          {service.address && (
            <div className="flex items-start gap-3">
              <MapPin className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
              <div>
                <p className="font-medium text-sm text-gray-500">주소</p>
                <p className="text-gray-900">{service.address}</p>
              </div>
            </div>
          )}

          {/* Service-specific details */}
          {renderServiceSpecificDetails(service)}

          {/* Action Buttons */}
          <div className="flex gap-2 pt-4">
            <Button
              onClick={handleDirections}
              className="flex-1"
              style={{ backgroundColor: categoryColor }}
            >
              <Navigation className="h-4 w-4 mr-2" />
              길찾기
            </Button>
            <Button onClick={handleShare} variant="outline" className="flex-1">
              <Share2 className="h-4 w-4 mr-2" />
              공유하기
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

// Helper function to get images from service
function getServiceImages(service: AnyService): string[] {
  const images: string[] = []

  // Check for main image
  if ((service as any).main_img) {
    images.push((service as any).main_img)
  }
  if ((service as any).imgurl) {
    images.push((service as any).imgurl)
  }

  return images
}

// Helper function to format distance
function formatDistance(distanceInMeters: number): string {
  if (distanceInMeters < 1000) {
    return `${Math.round(distanceInMeters)}m`
  }
  return `${(distanceInMeters / 1000).toFixed(1)}km`
}

// Render service-specific details
function renderServiceSpecificDetails(service: AnyService) {
  const details: JSX.Element[] = []

  switch (service.category) {
    case ServiceCategory.LIBRARY: {
      const lib = service as any
      if (lib.tel_no) {
        details.push(
          <div key="tel" className="flex items-start gap-3">
            <Phone className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">전화번호</p>
              <a
                href={`tel:${lib.tel_no}`}
                className="text-blue-600 hover:underline"
              >
                {lib.tel_no}
              </a>
            </div>
          </div>
        )
      }
      if (lib.operTime || lib.close_day) {
        details.push(
          <div key="hours" className="flex items-start gap-3">
            <Clock className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">운영시간</p>
              {lib.operTime && <p className="text-gray-900">{lib.operTime}</p>}
              {lib.close_day && (
                <p className="text-sm text-red-600">휴관일: {lib.close_day}</p>
              )}
            </div>
          </div>
        )
      }
      if (lib.homepage) {
        details.push(
          <div key="web" className="flex items-start gap-3">
            <Globe className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">홈페이지</p>
              <a
                href={lib.homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline flex items-center gap-1"
              >
                방문하기 <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        )
      }
      break
    }

    case ServiceCategory.CULTURAL_EVENT: {
      const event = service as any
      if (event.event_period || (event.strtdate && event.end_date)) {
        const period = event.event_period || `${event.strtdate} ~ ${event.end_date}`
        details.push(
          <div key="period" className="flex items-start gap-3">
            <Calendar className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">행사 기간</p>
              <p className="text-gray-900">{period}</p>
            </div>
          </div>
        )
      }
      if (event.use_fee || event.is_free) {
        details.push(
          <div key="fee" className="flex items-start gap-3">
            <span className="text-lg mt-0.5">💰</span>
            <div>
              <p className="font-medium text-sm text-gray-500">이용료</p>
              <p className="text-gray-900">{event.use_fee || event.is_free}</p>
            </div>
          </div>
        )
      }
      if (event.program) {
        details.push(
          <div key="program" className="flex items-start gap-3">
            <span className="text-lg mt-0.5">📋</span>
            <div>
              <p className="font-medium text-sm text-gray-500">프로그램 정보</p>
              <p className="text-gray-900 text-sm leading-relaxed">{event.program}</p>
            </div>
          </div>
        )
      }
      if (event.hmpg_addr || event.org_link) {
        details.push(
          <div key="web" className="flex items-start gap-3">
            <Globe className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">홈페이지</p>
              <a
                href={event.hmpg_addr || event.org_link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline flex items-center gap-1"
              >
                자세히 보기 <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        )
      }
      break
    }

    case ServiceCategory.CULTURAL_SPACE: {
      const space = service as any
      if (space.tel_no) {
        details.push(
          <div key="tel" className="flex items-start gap-3">
            <Phone className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">전화번호</p>
              <a
                href={`tel:${space.tel_no}`}
                className="text-blue-600 hover:underline"
              >
                {space.tel_no}
              </a>
            </div>
          </div>
        )
      }
      if (space.openTime) {
        details.push(
          <div key="hours" className="flex items-start gap-3">
            <Clock className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">운영시간</p>
              <p className="text-gray-900">{space.openTime}</p>
            </div>
          </div>
        )
      }
      if (space.homepage) {
        details.push(
          <div key="web" className="flex items-start gap-3">
            <Globe className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">홈페이지</p>
              <a
                href={space.homepage}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline flex items-center gap-1"
              >
                방문하기 <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        )
      }
      break
    }

    case ServiceCategory.PUBLIC_RESERVATION: {
      const reservation = service as any
      if (reservation.usetgtinfo) {
        details.push(
          <div key="target" className="flex items-start gap-3">
            <span className="text-lg mt-0.5">👥</span>
            <div>
              <p className="font-medium text-sm text-gray-500">이용대상</p>
              <p className="text-gray-900">{reservation.usetgtinfo}</p>
            </div>
          </div>
        )
      }
      if (reservation.rcptbgndt && reservation.rcptenddt) {
        details.push(
          <div key="period" className="flex items-start gap-3">
            <Calendar className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">접수 기간</p>
              <p className="text-gray-900">
                {reservation.rcptbgndt} ~ {reservation.rcptenddt}
              </p>
            </div>
          </div>
        )
      }
      if (reservation.svcurl) {
        details.push(
          <div key="web" className="flex items-start gap-3">
            <Globe className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">예약하기</p>
              <a
                href={reservation.svcurl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline flex items-center gap-1"
              >
                예약 페이지 바로가기 <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>
        )
      }
      break
    }

    case ServiceCategory.FUTURE_HERITAGE: {
      const heritage = service as any
      if (heritage.category_name) {
        details.push(
          <div key="category" className="flex items-start gap-3">
            <span className="text-lg mt-0.5">🏛️</span>
            <div>
              <p className="font-medium text-sm text-gray-500">분류</p>
              <p className="text-gray-900">{heritage.category_name}</p>
            </div>
          </div>
        )
      }
      if (heritage.year_designated) {
        details.push(
          <div key="year" className="flex items-start gap-3">
            <Calendar className="h-5 w-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="font-medium text-sm text-gray-500">지정 연도</p>
              <p className="text-gray-900">{heritage.year_designated}</p>
            </div>
          </div>
        )
      }
      if (heritage.description) {
        details.push(
          <div key="desc" className="flex items-start gap-3">
            <span className="text-lg mt-0.5">📝</span>
            <div>
              <p className="font-medium text-sm text-gray-500">설명</p>
              <p className="text-gray-900 text-sm leading-relaxed">
                {heritage.description}
              </p>
            </div>
          </div>
        )
      }
      break
    }
  }

  return details.length > 0 ? <div className="space-y-4">{details}</div> : null
}
