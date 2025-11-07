/**
 * Kakao Maps Geocoding Service
 * Uses Kakao Maps SDK for address-to-coordinates conversion
 */

export interface GeocodeResult {
  success: boolean
  latitude: number
  longitude: number
  address?: string
  message?: string
}

/**
 * Check if Kakao SDK is loaded
 */
function isKakaoLoaded(): boolean {
  return typeof window !== 'undefined' && window.kakao && window.kakao.maps && window.kakao.maps.services
}

/**
 * Geocode address using Kakao Maps SDK
 * Converts address to coordinates (latitude, longitude)
 */
export async function geocodeAddress(address: string): Promise<GeocodeResult> {
  return new Promise((resolve, reject) => {
    if (!isKakaoLoaded()) {
      reject(new Error('Kakao Maps SDK not loaded'))
      return
    }

    const geocoder = new window.kakao.maps.services.Geocoder()

    geocoder.addressSearch(address, (result: any[], status: any) => {
      if (status === window.kakao.maps.services.Status.OK) {
        if (result && result.length > 0) {
          const { y, x, address_name } = result[0]
          resolve({
            success: true,
            latitude: parseFloat(y),
            longitude: parseFloat(x),
            address: address_name || address,
          })
        } else {
          reject(new Error('주소를 찾을 수 없습니다.'))
        }
      } else if (status === window.kakao.maps.services.Status.ZERO_RESULT) {
        reject(new Error('검색 결과가 없습니다. 주소를 확인해주세요.'))
      } else {
        reject(new Error('주소 검색에 실패했습니다.'))
      }
    })
  })
}

/**
 * Reverse geocode coordinates using Kakao Maps SDK
 * Converts coordinates to address
 */
export async function reverseGeocode(latitude: number, longitude: number): Promise<GeocodeResult> {
  return new Promise((resolve, reject) => {
    if (!isKakaoLoaded()) {
      reject(new Error('Kakao Maps SDK not loaded'))
      return
    }

    const geocoder = new window.kakao.maps.services.Geocoder()
    const coord = new window.kakao.maps.LatLng(latitude, longitude)

    geocoder.coord2Address(coord.getLng(), coord.getLat(), (result: any[], status: any) => {
      if (status === window.kakao.maps.services.Status.OK) {
        if (result && result.length > 0) {
          const address = result[0].road_address?.address_name || result[0].address?.address_name
          resolve({
            success: true,
            latitude,
            longitude,
            address,
          })
        } else {
          reject(new Error('좌표에 해당하는 주소를 찾을 수 없습니다.'))
        }
      } else {
        reject(new Error('주소 변환에 실패했습니다.'))
      }
    })
  })
}
