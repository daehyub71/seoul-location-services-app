"""
Application Configuration
Loads environment variables and provides settings
"""

from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    ENVIRONMENT: str = "development"
    API_VERSION: str = "v1"
    LOG_LEVEL: str = "INFO"

    # Supabase Configuration
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_SERVICE_ROLE_KEY: str
    SUPABASE_DATABASE_URL: str

    # Upstash Redis Configuration
    UPSTASH_URL: str
    UPSTASH_TOKEN: str
    REDIS_URL: Optional[str] = None  # Computed from UPSTASH_URL

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set REDIS_URL from UPSTASH_URL if not explicitly provided
        if self.REDIS_URL is None and hasattr(self, 'UPSTASH_URL'):
            self.REDIS_URL = self.UPSTASH_URL

    # Seoul Open API Configuration
    SEOUL_API_KEY: str
    SEOUL_API_BASE_URL: str = "http://openapi.seoul.go.kr:8088"

    # Kakao API Configuration
    KAKAO_REST_API_KEY: Optional[str] = None

    # Firebase Configuration (Optional)
    FIREBASE_DATABASE_URL: Optional[str] = None
    FIREBASE_ADMIN_SDK_PATH: Optional[str] = None

    # Ollama Configuration (Optional)
    OLLAMA_BASE_URL: Optional[str] = "http://localhost:11434"
    OLLAMA_LLM_MODEL: Optional[str] = "llama3.1:8b"
    OLLAMA_EMBED_MODEL: Optional[str] = "bge-m3"

    # Cache Configuration
    REDIS_CACHE_TTL: int = 300  # 5 minutes
    CACHE_ENABLED: bool = True

    # Data Collection Configuration
    COLLECTION_SCHEDULE_ENABLED: bool = True
    COLLECTION_RETRY_COUNT: int = 3
    COLLECTION_TIMEOUT: int = 30  # seconds

    # API Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 100

    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8501",
        "https://seoul-location-services.vercel.app",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ]

    # Optional: Allow custom CORS origins from environment
    CORS_ORIGINS_EXTRA: Optional[str] = None  # Comma-separated list

    def get_cors_origins(self) -> List[str]:
        """Get all CORS origins including environment extras"""
        origins = self.CORS_ORIGINS.copy()
        if self.CORS_ORIGINS_EXTRA:
            extras = [origin.strip() for origin in self.CORS_ORIGINS_EXTRA.split(',')]
            origins.extend(extras)
        return origins

    # Spatial Query Defaults
    DEFAULT_SEARCH_RADIUS: int = 2000  # meters
    MAX_SEARCH_RADIUS: int = 10000  # meters
    DEFAULT_RESULTS_LIMIT: int = 50
    MAX_RESULTS_LIMIT: int = 200

    # Seoul City Bounds (for coordinate validation)
    SEOUL_LAT_MIN: float = 37.0
    SEOUL_LAT_MAX: float = 38.0
    SEOUL_LON_MIN: float = 126.0
    SEOUL_LON_MAX: float = 128.0

    # Seoul City Hall (default center)
    DEFAULT_CENTER_LAT: float = 37.5665
    DEFAULT_CENTER_LON: float = 126.9780

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT.lower() == "production"

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT.lower() == "development"

    @property
    def SEOUL_BOUNDS(self) -> dict:
        """Get Seoul city bounds as dictionary"""
        return {
            'min_latitude': self.SEOUL_LAT_MIN,
            'max_latitude': self.SEOUL_LAT_MAX,
            'min_longitude': self.SEOUL_LON_MIN,
            'max_longitude': self.SEOUL_LON_MAX
        }

    def validate_coordinates(self, lat: float, lon: float) -> bool:
        """Validate if coordinates are within Seoul bounds"""
        return (
            self.SEOUL_LAT_MIN <= lat <= self.SEOUL_LAT_MAX and
            self.SEOUL_LON_MIN <= lon <= self.SEOUL_LON_MAX
        )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()
