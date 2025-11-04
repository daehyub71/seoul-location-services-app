import { Button } from '@/components/ui/button'
import { useLocation } from '@/hooks/useLocation'
import { Locate, Loader2, AlertCircle } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

export interface CurrentLocationProps {
  onLocationChange?: (latitude: number, longitude: number) => void
  className?: string
}

export default function CurrentLocation({
  onLocationChange,
  className = '',
}: CurrentLocationProps) {
  const { location, loading, error, requestLocation, clearError, permissionStatus } =
    useLocation()

  const handleLocationRequest = () => {
    clearError()
    requestLocation()

    // Notify parent component when location is updated
    if (location && onLocationChange) {
      onLocationChange(location.latitude, location.longitude)
    }
  }

  const getButtonText = () => {
    if (loading) return '위치 확인 중...'
    if (permissionStatus === 'denied') return '위치 권한 거부됨'
    if (location) return '현재 위치 갱신'
    return '현재 위치 찾기'
  }

  const getButtonVariant = () => {
    if (error) return 'destructive'
    if (location) return 'outline'
    return 'default'
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <Button
        onClick={handleLocationRequest}
        disabled={loading || permissionStatus === 'denied'}
        variant={getButtonVariant() as any}
        className="w-full"
      >
        {loading ? (
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
        ) : (
          <Locate className="mr-2 h-4 w-4" />
        )}
        {getButtonText()}
      </Button>

      <AnimatePresence mode="wait">
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-800"
          >
            <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium">위치 확인 실패</p>
              <p className="text-xs mt-1">{error.message}</p>
              {permissionStatus === 'denied' && (
                <p className="text-xs mt-2">
                  브라우저 설정에서 위치 권한을 허용해주세요.
                </p>
              )}
            </div>
          </motion.div>
        )}

        {location && !error && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm text-blue-800"
          >
            <Locate className="h-4 w-4 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium">현재 위치</p>
              <p className="text-xs mt-1 font-mono">
                위도: {location.latitude.toFixed(6)}, 경도: {location.longitude.toFixed(6)}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {permissionStatus === 'prompt' && !location && !loading && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-xs text-gray-500 text-center"
        >
          위치 기반 서비스를 이용하려면 위치 권한을 허용해주세요.
        </motion.p>
      )}
    </div>
  )
}
