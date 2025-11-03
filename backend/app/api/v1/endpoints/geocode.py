"""
Geocode API Endpoints
지오코딩 API 엔드포인트
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.services.kakao_map_service import get_kakao_map_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/geocode", tags=["geocode"])


# Request/Response Schemas

class GeocodeRequest(BaseModel):
    """지오코딩 요청"""
    address: str = Field(..., description="주소 (예: 서울시청, 서울 중구 세종대로 110)")


class ReverseGeocodeRequest(BaseModel):
    """역방향 지오코딩 요청"""
    latitude: float = Field(..., description="위도 (WGS84)")
    longitude: float = Field(..., description="경도 (WGS84)")


class GeocodeResponse(BaseModel):
    """지오코딩 응답"""
    success: bool = True
    address: str
    latitude: float
    longitude: float
    source: str = Field("kakao", description="지오코딩 소스")


class ReverseGeocodeResponse(BaseModel):
    """역방향 지오코딩 응답"""
    success: bool = True
    latitude: float
    longitude: float
    address: str
    road_address: Optional[str] = None
    jibun_address: Optional[str] = None


class ErrorResponse(BaseModel):
    """에러 응답"""
    success: bool = False
    error: str
    details: Optional[str] = None


# Endpoints

@router.post(
    "",
    response_model=GeocodeResponse,
    summary="주소 → 좌표 변환",
    description="주소 문자열을 받아 WGS84 좌표로 변환합니다."
)
async def geocode(request: GeocodeRequest):
    """
    주소 → 좌표 변환 (Geocoding)

    **입력**:
    - address: 주소 (예: "서울시청", "강남역", "서울 중구 세종대로 110")

    **응답**:
    - latitude: 위도 (WGS84)
    - longitude: 경도 (WGS84)
    - address: 입력 주소

    **사용 예시**:
    ```json
    {
      "address": "서울시청"
    }
    ```

    **응답 예시**:
    ```json
    {
      "success": true,
      "address": "서울시청",
      "latitude": 37.5665,
      "longitude": 126.9780,
      "source": "kakao"
    }
    ```
    """
    try:
        logger.info(f"[geocode] Request: address='{request.address}'")

        # Kakao Map Service 사용
        kakao_service = get_kakao_map_service()

        # 주소 검색 시도
        coords = await kakao_service.address_to_coordinates(request.address)

        # 주소 검색 실패 시 키워드 검색
        if not coords:
            logger.info(f"[geocode] Address search failed, trying keyword search")
            coords = await kakao_service.keyword_search(request.address)

        if not coords:
            raise HTTPException(
                status_code=404,
                detail=f"Could not geocode address: {request.address}"
            )

        latitude, longitude = coords

        logger.info(
            f"[geocode] Success: '{request.address}' → "
            f"({latitude}, {longitude})"
        )

        return GeocodeResponse(
            address=request.address,
            latitude=latitude,
            longitude=longitude
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[geocode] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Geocoding failed: {str(e)}"
        )


@router.post(
    "/reverse",
    response_model=ReverseGeocodeResponse,
    summary="좌표 → 주소 변환",
    description="WGS84 좌표를 받아 주소로 변환합니다."
)
async def reverse_geocode(request: ReverseGeocodeRequest):
    """
    좌표 → 주소 변환 (Reverse Geocoding)

    **입력**:
    - latitude: 위도 (WGS84)
    - longitude: 경도 (WGS84)

    **응답**:
    - address: 주소 (도로명 주소 우선, 없으면 지번 주소)
    - road_address: 도로명 주소
    - jibun_address: 지번 주소

    **사용 예시**:
    ```json
    {
      "latitude": 37.5665,
      "longitude": 126.9780
    }
    ```

    **응답 예시**:
    ```json
    {
      "success": true,
      "latitude": 37.5665,
      "longitude": 126.9780,
      "address": "서울특별시 중구 세종대로 110",
      "road_address": "서울특별시 중구 세종대로 110",
      "jibun_address": "서울특별시 중구 태평로1가 31"
    }
    ```
    """
    try:
        logger.info(
            f"[reverse_geocode] Request: "
            f"({request.latitude}, {request.longitude})"
        )

        # 좌표 검증
        if not (-90 <= request.latitude <= 90):
            raise HTTPException(
                status_code=400,
                detail="Latitude must be between -90 and 90"
            )

        if not (-180 <= request.longitude <= 180):
            raise HTTPException(
                status_code=400,
                detail="Longitude must be between -180 and 180"
            )

        # Kakao Map Service 사용
        kakao_service = get_kakao_map_service()

        # 역방향 지오코딩
        address = await kakao_service.reverse_geocode(
            request.latitude,
            request.longitude
        )

        if not address:
            raise HTTPException(
                status_code=404,
                detail=f"Could not find address for coordinates: ({request.latitude}, {request.longitude})"
            )

        logger.info(
            f"[reverse_geocode] Success: "
            f"({request.latitude}, {request.longitude}) → '{address}'"
        )

        return ReverseGeocodeResponse(
            latitude=request.latitude,
            longitude=request.longitude,
            address=address,
            road_address=address if "로" in address or "길" in address else None,
            jibun_address=address if "동" in address or "가" in address else None
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[reverse_geocode] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Reverse geocoding failed: {str(e)}"
        )


@router.get(
    "/place/{place_name}",
    summary="장소 정보 조회",
    description="장소명으로 상세 정보를 조회합니다."
)
async def get_place_info(place_name: str):
    """
    장소 정보 조회

    **입력**:
    - place_name: 장소명 (예: "서울시청", "강남역")

    **응답**:
    - 장소명, 주소, 좌표, 카테고리, 전화번호 등
    """
    try:
        logger.info(f"[place_info] Request: place_name='{place_name}'")

        # Kakao Map Service 사용
        kakao_service = get_kakao_map_service()

        # 장소 정보 조회
        place_info = await kakao_service.get_place_info(place_name)

        if not place_info:
            raise HTTPException(
                status_code=404,
                detail=f"Place not found: {place_name}"
            )

        logger.info(
            f"[place_info] Success: '{place_name}' → "
            f"{place_info.get('name')}"
        )

        return {
            "success": True,
            **place_info
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[place_info] Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Place info retrieval failed: {str(e)}"
        )
