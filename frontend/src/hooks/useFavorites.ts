import { useState, useEffect, useCallback } from 'react'

const FAVORITES_KEY = 'seoul-services-favorites'

export interface Favorite {
  id: string
  name: string
  category: string
  addedAt: number
}

export function useFavorites() {
  const [favorites, setFavorites] = useState<Favorite[]>([])

  // Load favorites from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(FAVORITES_KEY)
      if (stored) {
        const parsed = JSON.parse(stored)
        setFavorites(parsed)
      }
    } catch (error) {
      console.error('Failed to load favorites:', error)
    }
  }, [])

  // Save favorites to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem(FAVORITES_KEY, JSON.stringify(favorites))
    } catch (error) {
      console.error('Failed to save favorites:', error)
    }
  }, [favorites])

  const isFavorite = useCallback(
    (serviceId: string): boolean => {
      return favorites.some((fav) => fav.id === serviceId)
    },
    [favorites]
  )

  const addFavorite = useCallback((serviceId: string, serviceName: string, category: string) => {
    setFavorites((prev) => {
      // Check if already exists
      if (prev.some((fav) => fav.id === serviceId)) {
        return prev
      }
      return [
        ...prev,
        {
          id: serviceId,
          name: serviceName,
          category,
          addedAt: Date.now(),
        },
      ]
    })
  }, [])

  const removeFavorite = useCallback((serviceId: string) => {
    setFavorites((prev) => prev.filter((fav) => fav.id !== serviceId))
  }, [])

  const toggleFavorite = useCallback(
    (serviceId: string, serviceName: string, category: string) => {
      if (isFavorite(serviceId)) {
        removeFavorite(serviceId)
      } else {
        addFavorite(serviceId, serviceName, category)
      }
    },
    [isFavorite, addFavorite, removeFavorite]
  )

  const clearFavorites = useCallback(() => {
    setFavorites([])
  }, [])

  return {
    favorites,
    isFavorite,
    addFavorite,
    removeFavorite,
    toggleFavorite,
    clearFavorites,
  }
}
