import { describe, it, expect } from 'vitest'
import { calculateDistance, formatDistance } from '../useLocation'

describe('useLocation utilities', () => {
  describe('calculateDistance', () => {
    it('should calculate distance between Seoul City Hall and Gangnam Station', () => {
      // Seoul City Hall
      const lat1 = 37.5665
      const lon1 = 126.978

      // Gangnam Station
      const lat2 = 37.498
      const lon2 = 127.0276

      const distance = calculateDistance(lat1, lon1, lat2, lon2)

      // Expected distance: ~8.5km
      expect(distance).toBeGreaterThan(8000)
      expect(distance).toBeLessThan(9000)
    })

    it('should return 0 for same location', () => {
      const lat = 37.5665
      const lon = 126.978

      const distance = calculateDistance(lat, lon, lat, lon)

      expect(distance).toBe(0)
    })

    it('should calculate distance correctly for small distances', () => {
      // Two points ~100m apart
      const lat1 = 37.5665
      const lon1 = 126.978
      const lat2 = 37.5675
      const lon2 = 126.978

      const distance = calculateDistance(lat1, lon1, lat2, lon2)

      // Expected: ~111m
      expect(distance).toBeGreaterThan(100)
      expect(distance).toBeLessThan(150)
    })
  })

  describe('formatDistance', () => {
    it('should format meters for distances < 1km', () => {
      expect(formatDistance(100)).toBe('100m')
      expect(formatDistance(500)).toBe('500m')
      expect(formatDistance(999)).toBe('999m')
    })

    it('should format kilometers for distances >= 1km', () => {
      expect(formatDistance(1000)).toBe('1.0km')
      expect(formatDistance(1500)).toBe('1.5km')
      expect(formatDistance(2345)).toBe('2.3km')
      expect(formatDistance(10000)).toBe('10.0km')
    })

    it('should round meters to nearest integer', () => {
      expect(formatDistance(123.4)).toBe('123m')
      expect(formatDistance(123.6)).toBe('124m')
    })

    it('should format kilometers to 1 decimal place', () => {
      expect(formatDistance(1234)).toBe('1.2km')
      expect(formatDistance(1289)).toBe('1.3km')
    })
  })
})
