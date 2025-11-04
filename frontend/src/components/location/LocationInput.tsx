import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Search, MapPin, X } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { useGeocode } from '@/hooks/useServices'

declare global {
  interface Window {
    daum: any
  }
}

export interface LocationInputProps {
  onLocationSelect?: (address: string, latitude: number, longitude: number) => void
  placeholder?: string
  className?: string
}

export default function LocationInput({
  onLocationSelect,
  placeholder = '주소를 검색하세요',
  className = '',
}: LocationInputProps) {
  const [inputValue, setInputValue] = useState('')
  const [selectedAddress, setSelectedAddress] = useState<string | null>(null)
  const [postcodeLoaded, setPostcodeLoaded] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const geocodeMutation = useGeocode()

  // Load Kakao Postcode script
  useEffect(() => {
    // Check if script is already loaded
    if (window.daum && window.daum.Postcode) {
      setPostcodeLoaded(true)
      return
    }

    // Check if script tag already exists
    const existingScript = document.querySelector(
      'script[src*="postcode"]'
    )
    if (existingScript) {
      existingScript.addEventListener('load', () => {
        setPostcodeLoaded(true)
      })
      return
    }

    const script = document.createElement('script')
    script.src = '//t1.daumcdn.net/mapjsapi/bundle/postcode/prod/postcode.v2.js'
    script.async = true
    script.onload = () => {
      setPostcodeLoaded(true)
    }
    script.onerror = () => {
      console.error('Failed to load Kakao Postcode script')
    }
    document.head.appendChild(script)

    return () => {
      // Don't remove script on unmount to allow reuse
    }
  }, [])

  const handleAddressSearch = () => {
    if (!window.daum || !window.daum.Postcode) {
      alert('주소 검색 서비스를 불러오는 중입니다. 잠시 후 다시 시도해주세요.')
      return
    }

    new window.daum.Postcode({
      oncomplete: function (data: any) {
        // 사용자가 선택한 주소
        const address = data.roadAddress || data.jibunAddress
        setInputValue(address)
        setSelectedAddress(address)

        // Geocode address to get coordinates
        geocodeMutation.mutate(
          { address },
          {
            onSuccess: (response) => {
              if (response.success) {
                const { latitude, longitude } = response
                if (onLocationSelect) {
                  onLocationSelect(address, latitude, longitude)
                }
              }
            },
            onError: (error) => {
              console.error('Geocoding failed:', error)
              alert('주소를 좌표로 변환하는데 실패했습니다.')
            },
          }
        )
      },
      width: '100%',
      height: '100%',
    }).open()
  }

  const handleManualSearch = () => {
    if (!inputValue.trim()) return

    setSelectedAddress(inputValue)
    geocodeMutation.mutate(
      { address: inputValue },
      {
        onSuccess: (response) => {
          if (response.success) {
            const { latitude, longitude } = response
            if (onLocationSelect) {
              onLocationSelect(inputValue, latitude, longitude)
            }
          }
        },
        onError: (error) => {
          console.error('Geocoding failed:', error)
          alert('주소를 찾을 수 없습니다. 다시 확인해주세요.')
        },
      }
    )
  }

  const handleClear = () => {
    setInputValue('')
    setSelectedAddress(null)
    inputRef.current?.focus()
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleManualSearch()
    }
  }

  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex gap-2">
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all"
          />
          {inputValue && (
            <button
              onClick={handleClear}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Clear input"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <Button
          onClick={handleAddressSearch}
          variant="outline"
          className="flex-shrink-0"
          title={postcodeLoaded ? "주소 검색" : "로딩 중..."}
          disabled={!postcodeLoaded}
        >
          <MapPin className="h-4 w-4 mr-2" />
          {postcodeLoaded ? '주소 찾기' : '로딩...'}
        </Button>

        <Button
          onClick={handleManualSearch}
          disabled={!inputValue.trim() || geocodeMutation.isPending}
          className="flex-shrink-0"
          title="입력한 주소로 검색"
        >
          <Search className="h-4 w-4 mr-2" />
          검색
        </Button>
      </div>

      <AnimatePresence mode="wait">
        {geocodeMutation.isPending && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-sm text-gray-600 flex items-center gap-2 p-2"
          >
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
            주소를 찾는 중...
          </motion.div>
        )}

        {geocodeMutation.isError && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="text-sm text-red-600 p-2 bg-red-50 border border-red-200 rounded-lg"
          >
            주소를 찾을 수 없습니다. 다시 확인해주세요.
          </motion.div>
        )}

        {geocodeMutation.isSuccess && geocodeMutation.data && selectedAddress && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-start gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-sm text-green-800"
          >
            <MapPin className="h-4 w-4 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <p className="font-medium">선택된 주소</p>
              <p className="text-xs mt-1">{selectedAddress}</p>
              <p className="text-xs mt-1 font-mono">
                위도: {geocodeMutation.data.latitude.toFixed(6)}, 경도:{' '}
                {geocodeMutation.data.longitude.toFixed(6)}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <p className="text-xs text-gray-500">
        💡 "주소 찾기" 버튼으로 정확한 주소를 검색하거나, 직접 입력 후 검색할 수 있습니다.
      </p>
    </div>
  )
}
