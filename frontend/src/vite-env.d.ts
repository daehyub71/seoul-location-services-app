/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_KAKAO_MAP_API_KEY: string
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_DEFAULT_LAT: string
  readonly VITE_DEFAULT_LON: string
  readonly VITE_DEFAULT_ZOOM: string
  readonly VITE_ENABLE_DARK_MODE: string
  readonly VITE_ENABLE_LLM_RECOMMENDATIONS: string
  readonly VITE_ENABLE_ANALYTICS: string
  readonly VITE_SENTRY_DSN?: string
  readonly VITE_GA_TRACKING_ID?: string
  readonly DEV: boolean
  readonly PROD: boolean
  readonly MODE: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
