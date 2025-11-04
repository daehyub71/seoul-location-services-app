// Service Categories
export enum ServiceCategory {
  CULTURAL_EVENT = 'cultural_events',
  LIBRARY = 'libraries',
  CULTURAL_SPACE = 'cultural_spaces',
  PUBLIC_RESERVATION = 'public_reservations',
  FUTURE_HERITAGE = 'future_heritage',
}

export const CATEGORY_LABELS: Record<ServiceCategory, string> = {
  [ServiceCategory.CULTURAL_EVENT]: '문화행사',
  [ServiceCategory.LIBRARY]: '도서관',
  [ServiceCategory.CULTURAL_SPACE]: '문화공간',
  [ServiceCategory.PUBLIC_RESERVATION]: '공공예약',
  [ServiceCategory.FUTURE_HERITAGE]: '미래유산',
}

export const CATEGORY_COLORS: Record<ServiceCategory, string> = {
  [ServiceCategory.CULTURAL_EVENT]: '#E03131',
  [ServiceCategory.LIBRARY]: '#1971C2',
  [ServiceCategory.CULTURAL_SPACE]: '#2F9E44',
  [ServiceCategory.PUBLIC_RESERVATION]: '#F76707',
  [ServiceCategory.FUTURE_HERITAGE]: '#7048E8',
}

// Base Service Interface
export interface Service {
  id: string
  category: ServiceCategory
  name: string
  latitude: number
  longitude: number
  address?: string
  distance?: number
}

// Cultural Event
export interface CulturalEvent extends Service {
  category: ServiceCategory.CULTURAL_EVENT
  codename: string
  guname: string
  title: string
  date: string
  place: string
  org_name: string
  use_trgt: string
  use_fee: string
  player: string
  program: string
  etc_desc: string
  rgstdate: string
  ticket: string
  strtdate: string
  end_date: string
  themecode: string
  lot: number
  lat: number
  is_free: string
  hmpg_addr: string
  main_img?: string
}

// Library
export interface Library extends Service {
  category: ServiceCategory.LIBRARY
  lbrry_name: string
  code_value: string
  adres: string
  tel_no: string
  fxnum: string
  homepage: string
  close_day: string
  book_co: number
  pblictn_co: number
  nonebook_co: number
  data_stdde: string
  instt_code: string
  instt_nm: string
  latitude: number
  longitude: number
  operTime?: string
}

// Cultural Space
export interface CulturalSpace extends Service {
  category: ServiceCategory.CULTURAL_SPACE
  fac_name: string
  subjcode: string
  codename: string
  region: string
  adres: string
  tel_no: string
  homepage: string
  openTime?: string
}

// Public Reservation
export interface PublicReservation extends Service {
  category: ServiceCategory.PUBLIC_RESERVATION
  svcid: string
  svcnm: string
  svcstatnm: string
  svcurl: string
  placenm: string
  usetgtinfo: string
  x: number
  y: number
  svcopnbgndt: string
  svcopnenddt: string
  rcptbgndt: string
  rcptenddt: string
  areanm: string
  imgurl: string
  dtlcont?: string
  telno?: string
  payatnm?: string
}

// Future Heritage
export interface FutureHeritage extends Service {
  category: ServiceCategory.FUTURE_HERITAGE
  number: number
  name: string
  category_name: string
  address: string
  latitude: number
  longitude: number
  main_category: string
  description?: string
}

// Union type for all services
export type AnyService =
  | CulturalEvent
  | Library
  | CulturalSpace
  | PublicReservation
  | FutureHeritage

// API Request/Response Types
export interface NearbyServicesRequest {
  latitude: number
  longitude: number
  radius: number
  categories?: ServiceCategory[]
  limit?: number
}

export interface NearbyServicesResponse {
  success: boolean
  data: {
    services: AnyService[]
    total: number
    query: {
      latitude: number
      longitude: number
      radius: number
      categories: string[]
    }
  }
  message?: string
}

export interface ServiceDetailRequest {
  category: ServiceCategory
  id: string
}

export interface ServiceDetailResponse {
  success: boolean
  data: AnyService
  message?: string
}

export interface GeocodeRequest {
  address: string
}

export interface GeocodeResponse {
  success: boolean
  address: string
  latitude: number
  longitude: number
  source?: string
  sido?: string
  sigungu?: string
  dong?: string
  message?: string
}

export interface ReverseGeocodeRequest {
  latitude: number
  longitude: number
}

export interface ReverseGeocodeResponse {
  success: boolean
  data: {
    address: string
    sido: string
    sigungu: string
    dong: string
    latitude: number
    longitude: number
  }
  message?: string
}

// Error Response
export interface ApiErrorResponse {
  success: false
  message: string
  error?: string
  details?: unknown
}
