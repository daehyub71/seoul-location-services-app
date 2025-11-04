import { create } from 'zustand'

export interface Location {
  latitude: number
  longitude: number
}

interface LocationState {
  // Current user location
  userLocation: Location | null
  setUserLocation: (location: Location | null) => void

  // Selected location on map
  selectedLocation: Location | null
  setSelectedLocation: (location: Location | null) => void

  // Search radius (in meters)
  searchRadius: number
  setSearchRadius: (radius: number) => void

  // Selected categories
  selectedCategories: string[]
  setSelectedCategories: (categories: string[]) => void
  toggleCategory: (category: string) => void

  // Map center
  mapCenter: Location
  setMapCenter: (location: Location) => void

  // Map zoom level
  zoomLevel: number
  setZoomLevel: (level: number) => void
}

// Seoul City Hall coordinates as default
const DEFAULT_LOCATION: Location = {
  latitude: 37.5665,
  longitude: 126.9780,
}

export const useLocationStore = create<LocationState>((set) => ({
  userLocation: null,
  setUserLocation: (location) => set({ userLocation: location }),

  selectedLocation: null,
  setSelectedLocation: (location) => set({ selectedLocation: location }),

  searchRadius: 2000, // 2km default
  setSearchRadius: (radius) => set({ searchRadius: radius }),

  selectedCategories: [],
  setSelectedCategories: (categories) => set({ selectedCategories: categories }),
  toggleCategory: (category) =>
    set((state) => ({
      selectedCategories: state.selectedCategories.includes(category)
        ? state.selectedCategories.filter((c) => c !== category)
        : [...state.selectedCategories, category],
    })),

  mapCenter: DEFAULT_LOCATION,
  setMapCenter: (location) => set({ mapCenter: location }),

  zoomLevel: 14, // Default zoom level for Seoul
  setZoomLevel: (level) => set({ zoomLevel: level }),
}))
