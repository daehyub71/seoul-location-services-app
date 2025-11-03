"""
Service API Schemas
Pydantic 모델 정의 - API 요청/응답
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime


# Request Schemas

class NearbySearchRequest(BaseModel):
    """근처 서비스 검색 요청"""
    latitude: Optional[float] = Field(None, description="위도 (WGS84)")
    longitude: Optional[float] = Field(None, description="경도 (WGS84)")
    address: Optional[str] = Field(None, description="주소 (예: 서울시청, 강남역)")
    radius: int = Field(2000, ge=100, le=10000, description="검색 반경 (미터, 100-10000)")
    category: Optional[str] = Field(None, description="카테고리 필터")
    limit: int = Field(50, ge=1, le=200, description="최대 결과 개수 (1-200)")

    @field_validator('latitude')
    @classmethod
    def validate_latitude(cls, v):
        if v is not None and not (-90 <= v <= 90):
            raise ValueError('Latitude must be between -90 and 90')
        return v

    @field_validator('longitude')
    @classmethod
    def validate_longitude(cls, v):
        if v is not None and not (-180 <= v <= 180):
            raise ValueError('Longitude must be between -180 and 180')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        if v is not None:
            allowed = ['cultural_events', 'libraries', 'cultural_spaces', 'future_heritages', 'public_reservations']
            if v not in allowed:
                raise ValueError(f'Category must be one of {allowed}')
        return v

    def validate_input(self):
        """좌표 또는 주소 중 하나는 필수"""
        if self.latitude is None and self.longitude is None and self.address is None:
            raise ValueError("Either coordinates (lat/lon) or address is required")
        if (self.latitude is not None and self.longitude is None) or (self.latitude is None and self.longitude is not None):
            raise ValueError("Both latitude and longitude must be provided together")


class CategorySearchRequest(BaseModel):
    """카테고리별 검색 요청"""
    latitude: float = Field(..., description="위도 (WGS84)")
    longitude: float = Field(..., description="경도 (WGS84)")
    radius: int = Field(2000, ge=100, le=10000, description="검색 반경 (미터)")
    limit: int = Field(50, ge=1, le=200, description="최대 결과 개수")
    sort_by: str = Field("distance", description="정렬 기준 (distance, name, date)")

    @field_validator('sort_by')
    @classmethod
    def validate_sort_by(cls, v):
        allowed = ['distance', 'name', 'date']
        if v not in allowed:
            raise ValueError(f'sort_by must be one of {allowed}')
        return v


# Response Schemas

class LocationInfo(BaseModel):
    """위치 정보"""
    id: str
    title: str
    category: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    distance: Optional[float] = None
    distance_formatted: Optional[str] = None
    address: Optional[str] = None
    info: Dict[str, Any] = Field(default_factory=dict)


class KakaoMarker(BaseModel):
    """Kakao Map 마커 데이터"""
    id: str
    lat: float
    lon: float
    title: str
    category: str
    distance: Optional[float] = None
    distance_formatted: Optional[str] = None
    info: Dict[str, Any] = Field(default_factory=dict)


class SearchSummary(BaseModel):
    """검색 요약 정보"""
    total_count: int
    category_counts: Dict[str, int] = Field(default_factory=dict)
    search_center: Optional[Dict[str, float]] = None
    search_radius: Optional[int] = None
    search_radius_km: Optional[float] = None
    search_address: Optional[str] = None
    average_distance: Optional[float] = None
    average_distance_km: Optional[float] = None
    min_distance: Optional[float] = None
    max_distance: Optional[float] = None
    execution_time: Optional[float] = None
    grouped_by_category: Optional[Dict[str, List[Dict[str, Any]]]] = None
    kakao_markers: List[KakaoMarker] = Field(default_factory=list)


class ServiceSearchResponse(BaseModel):
    """서비스 검색 응답"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    success: bool = True
    message: str
    locations: List[Dict[str, Any]] = Field(default_factory=list)
    summary: Optional[SearchSummary] = None
    workflow_id: Optional[str] = None
    errors: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class CategoryListResponse(BaseModel):
    """카테고리 목록 응답"""
    categories: List[Dict[str, str]]


class ErrorResponse(BaseModel):
    """에러 응답"""
    model_config = ConfigDict(json_encoders={datetime: lambda v: v.isoformat()})

    success: bool = False
    error: str
    details: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)


# Category metadata
CATEGORY_METADATA = {
    'cultural_events': {
        'name': '문화행사',
        'name_en': 'Cultural Events',
        'description': '서울시 문화행사 정보',
        'icon': '🎭'
    },
    'libraries': {
        'name': '도서관',
        'name_en': 'Libraries',
        'description': '서울시 도서관 정보',
        'icon': '📚'
    },
    'cultural_spaces': {
        'name': '문화공간',
        'name_en': 'Cultural Spaces',
        'description': '서울시 문화공간 정보',
        'icon': '🏛️'
    },
    'future_heritages': {
        'name': '미래유산',
        'name_en': 'Future Heritages',
        'description': '서울시 미래유산 정보',
        'icon': '🏺'
    },
    'public_reservations': {
        'name': '공공시설 예약',
        'name_en': 'Public Reservations',
        'description': '서울시 공공시설 예약 정보',
        'icon': '🏢'
    }
}
