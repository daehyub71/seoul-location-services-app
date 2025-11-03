"""
Pydantic Models for Supabase Tables
Defines data schemas for all 5 tables
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date


# ============================================================================
# Cultural Events (문화행사)
# ============================================================================

class CulturalEventBase(BaseModel):
    """Base model for Cultural Events"""
    api_id: str
    title: str
    codename: Optional[str] = None
    guname: Optional[str] = None
    place: Optional[str] = None
    org_name: Optional[str] = None
    use_trgt: Optional[str] = None
    use_fee: Optional[str] = None
    player: Optional[str] = None
    program: Optional[str] = None
    etc_desc: Optional[str] = None
    org_link: Optional[str] = None
    main_img: Optional[str] = None
    rgst_date: Optional[date] = None
    ticket: Optional[str] = None
    strtdate: Optional[date] = None
    end_date: Optional[date] = None
    themecode: Optional[str] = None
    lot: Optional[float] = None  # Longitude
    lat: Optional[float] = None  # Latitude
    is_free: Optional[str] = None
    hmpg_addr: Optional[str] = None


class CulturalEvent(CulturalEventBase):
    """Cultural Events model with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CulturalEventCreate(CulturalEventBase):
    """Model for creating Cultural Events"""
    pass


class CulturalEventResponse(CulturalEvent):
    """Model for Cultural Events API response"""
    pass


# ============================================================================
# Libraries (도서관)
# ============================================================================

class LibraryBase(BaseModel):
    """Base model for Libraries"""
    api_id: str
    library_name: str
    library_type: str = Field(..., description="public or disabled")
    guname: Optional[str] = None
    address: Optional[str] = None
    tel: Optional[str] = None
    homepage: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    opertime: Optional[str] = None
    closing_day: Optional[str] = None
    book_count: Optional[int] = None
    seat_count: Optional[int] = None
    facilities: Optional[str] = None


class Library(LibraryBase):
    """Libraries model with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LibraryCreate(LibraryBase):
    """Model for creating Libraries"""
    pass


class LibraryResponse(Library):
    """Model for Libraries API response"""
    pass


# ============================================================================
# Cultural Spaces (문화공간)
# ============================================================================

class CulturalSpaceBase(BaseModel):
    """Base model for Cultural Spaces"""
    api_id: str
    fac_name: str
    guname: Optional[str] = None
    subjcode: Optional[str] = None
    fac_code: Optional[str] = None
    codename: Optional[str] = None
    addr: Optional[str] = None
    zipcode: Optional[str] = None
    telno: Optional[str] = None
    homepage: Optional[str] = None
    restroomyn: Optional[str] = None
    parking_info: Optional[str] = None
    main_purps: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class CulturalSpace(CulturalSpaceBase):
    """Cultural Spaces model with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CulturalSpaceCreate(CulturalSpaceBase):
    """Model for creating Cultural Spaces"""
    pass


class CulturalSpaceResponse(CulturalSpace):
    """Model for Cultural Spaces API response"""
    pass


# ============================================================================
# Future Heritages (미래유산)
# ============================================================================

class FutureHeritageBase(BaseModel):
    """Base model for Future Heritages"""
    api_id: str
    no: Optional[int] = None
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    name: str
    year_designated: Optional[int] = None
    gu_name: Optional[str] = None
    dong_name: Optional[str] = None
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    description: Optional[str] = None
    reason: Optional[str] = None
    main_img: Optional[str] = None


class FutureHeritage(FutureHeritageBase):
    """Future Heritages model with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FutureHeritageCreate(FutureHeritageBase):
    """Model for creating Future Heritages"""
    pass


class FutureHeritageResponse(FutureHeritage):
    """Model for Future Heritages API response"""
    pass


# ============================================================================
# Public Reservations (공공예약)
# ============================================================================

class PublicReservationBase(BaseModel):
    """Base model for Public Reservations"""
    api_id: str
    svc_id: Optional[str] = None
    minclassnm: Optional[str] = None
    svcstatnm: Optional[str] = None
    svcnm: str
    payatnm: Optional[str] = None
    placenm: Optional[str] = None
    usetgtinfo: Optional[str] = None
    svcurl: Optional[str] = None
    x_coord: Optional[float] = None  # Longitude
    y_coord: Optional[float] = None  # Latitude
    svcopnbgndt: Optional[date] = None
    svcopnenddt: Optional[date] = None
    rcptbgndt: Optional[datetime] = None
    rcptenddt: Optional[datetime] = None
    areanm: Optional[str] = None
    imgurl: Optional[str] = None
    dtlcont: Optional[str] = None
    telno: Optional[str] = None
    v_max: Optional[int] = None
    v_min: Optional[int] = None
    revstdday: Optional[str] = None
    revstddaynm: Optional[str] = None


class PublicReservation(PublicReservationBase):
    """Public Reservations model with database fields"""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublicReservationCreate(PublicReservationBase):
    """Model for creating Public Reservations"""
    pass


class PublicReservationResponse(PublicReservation):
    """Model for Public Reservations API response"""
    pass


# ============================================================================
# Common Response Models
# ============================================================================

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: list
    total: int
    page: int
    page_size: int
    total_pages: int


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    message: str
    details: Optional[dict] = None
