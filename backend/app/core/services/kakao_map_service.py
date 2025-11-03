"""
Kakao Map API Service
Kakao Map Geocoding (주소 → 좌표 변환)
"""

import logging
from typing import Optional, Dict, Any, Tuple
import httpx
from functools import lru_cache

from app.core.config import settings

logger = logging.getLogger(__name__)


class KakaoMapService:
    """
    Kakao Map API 서비스

    Features:
    - 주소 → 좌표 변환 (Geocoding)
    - 좌표 → 주소 변환 (Reverse Geocoding)
    - 키워드 검색 (장소 검색)
    """

    BASE_URL = "https://dapi.kakao.com/v2"

    def __init__(self, api_key: Optional[str] = None):
        """
        Kakao Map API 클라이언트 초기화

        Args:
            api_key: Kakao REST API 키 (None이면 settings에서 가져옴)
        """
        self.api_key = api_key or settings.KAKAO_REST_API_KEY

        if not self.api_key:
            logger.warning("Kakao API key not configured")

        self.headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }

    async def address_to_coordinates(
        self,
        address: str
    ) -> Optional[Tuple[float, float]]:
        """
        주소 → 좌표 변환 (Geocoding)

        Args:
            address: 주소 (예: "서울시청", "강남역", "서울 중구 세종대로 110")

        Returns:
            (latitude, longitude) 튜플 또는 None

        Example:
            >>> service = KakaoMapService()
            >>> lat, lon = await service.address_to_coordinates("서울시청")
            >>> print(f"Lat: {lat}, Lon: {lon}")
        """
        if not self.api_key:
            logger.error("Kakao API key not configured")
            return None

        endpoint = f"{self.BASE_URL}/local/search/address.json"
        params = {"query": address}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()

                data = response.json()
                documents = data.get("documents", [])

                if not documents:
                    logger.warning(f"No results found for address: {address}")
                    return None

                # 첫 번째 결과 사용
                doc = documents[0]
                lon = float(doc.get("x"))
                lat = float(doc.get("y"))

                logger.info(f"Geocoded '{address}' → ({lat}, {lon})")
                return (lat, lon)

        except httpx.HTTPStatusError as e:
            logger.error(f"Kakao API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Geocoding error for '{address}': {e}")
            return None

    async def keyword_search(
        self,
        keyword: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: int = 2000
    ) -> Optional[Tuple[float, float]]:
        """
        키워드 검색 (장소 검색)

        Args:
            keyword: 검색 키워드 (예: "서울시청", "강남역")
            latitude: 중심 위도 (선택)
            longitude: 중심 경도 (선택)
            radius: 반경 (미터)

        Returns:
            (latitude, longitude) 튜플 또는 None
        """
        if not self.api_key:
            logger.error("Kakao API key not configured")
            return None

        endpoint = f"{self.BASE_URL}/local/search/keyword.json"
        params = {"query": keyword}

        # 중심 좌표 지정 시
        if latitude is not None and longitude is not None:
            params["x"] = longitude
            params["y"] = latitude
            params["radius"] = radius

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()

                data = response.json()
                documents = data.get("documents", [])

                if not documents:
                    logger.warning(f"No results found for keyword: {keyword}")
                    return None

                # 첫 번째 결과 사용
                doc = documents[0]
                lon = float(doc.get("x"))
                lat = float(doc.get("y"))
                place_name = doc.get("place_name")

                logger.info(f"Found '{place_name}' for keyword '{keyword}' → ({lat}, {lon})")
                return (lat, lon)

        except httpx.HTTPStatusError as e:
            logger.error(f"Kakao API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Keyword search error for '{keyword}': {e}")
            return None

    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[str]:
        """
        좌표 → 주소 변환 (Reverse Geocoding)

        Args:
            latitude: 위도
            longitude: 경도

        Returns:
            주소 문자열 또는 None
        """
        if not self.api_key:
            logger.error("Kakao API key not configured")
            return None

        endpoint = f"{self.BASE_URL}/local/geo/coord2address.json"
        params = {
            "x": longitude,
            "y": latitude
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()

                data = response.json()
                documents = data.get("documents", [])

                if not documents:
                    logger.warning(f"No address found for coordinates: ({latitude}, {longitude})")
                    return None

                # 도로명 주소 우선, 없으면 지번 주소
                doc = documents[0]
                road_address = doc.get("road_address")
                if road_address:
                    address = road_address.get("address_name")
                else:
                    address = doc.get("address", {}).get("address_name")

                logger.info(f"Reverse geocoded ({latitude}, {longitude}) → '{address}'")
                return address

        except httpx.HTTPStatusError as e:
            logger.error(f"Kakao API HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None

    async def get_place_info(
        self,
        keyword: str
    ) -> Optional[Dict[str, Any]]:
        """
        장소 상세 정보 조회

        Args:
            keyword: 장소명

        Returns:
            장소 정보 딕셔너리 또는 None
        """
        if not self.api_key:
            logger.error("Kakao API key not configured")
            return None

        endpoint = f"{self.BASE_URL}/local/search/keyword.json"
        params = {"query": keyword}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    endpoint,
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()

                data = response.json()
                documents = data.get("documents", [])

                if not documents:
                    return None

                # 첫 번째 결과 반환
                doc = documents[0]
                return {
                    "name": doc.get("place_name"),
                    "address": doc.get("address_name"),
                    "road_address": doc.get("road_address_name"),
                    "latitude": float(doc.get("y")),
                    "longitude": float(doc.get("x")),
                    "category": doc.get("category_name"),
                    "phone": doc.get("phone"),
                    "place_url": doc.get("place_url")
                }

        except Exception as e:
            logger.error(f"Get place info error for '{keyword}': {e}")
            return None


@lru_cache()
def get_kakao_map_service() -> KakaoMapService:
    """
    Kakao Map 서비스 싱글톤 인스턴스

    Returns:
        KakaoMapService 인스턴스
    """
    return KakaoMapService()


# Pre-initialize on module import
try:
    kakao_map_service = get_kakao_map_service()
    logger.info("Kakao Map service pre-initialized")
except Exception as e:
    logger.warning(f"Failed to pre-initialize Kakao Map service: {e}")
    kakao_map_service = None
