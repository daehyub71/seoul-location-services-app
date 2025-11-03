"""
LocationAnalyzer Agent
위치 분석 에이전트 - 사용자 입력 파싱 및 좌표 추출
"""

import logging
from typing import Optional, Dict, Any
import uuid

from app.core.workflow.state import LocationQuery, AnalyzedLocation
from app.core.services.kakao_map_service import get_kakao_map_service
from app.utils.coordinate_transform import CoordinateTransformer

logger = logging.getLogger(__name__)


class LocationAnalyzer:
    """
    위치 분석 에이전트

    기능:
    1. 사용자 입력 분석 (좌표 vs 주소)
    2. 주소 → 좌표 변환 (Kakao Geocoding)
    3. 좌표 정규화 (소수점 6자리)
    4. 서울 범위 검증
    5. 반경 및 카테고리 설정
    """

    def __init__(self):
        """LocationAnalyzer 초기화"""
        self.kakao_service = get_kakao_map_service()
        self.coord_transformer = CoordinateTransformer()
        logger.info("LocationAnalyzer initialized")

    async def analyze(
        self,
        query: LocationQuery
    ) -> Optional[AnalyzedLocation]:
        """
        위치 쿼리 분석

        Args:
            query: 사용자 위치 쿼리

        Returns:
            AnalyzedLocation 또는 None (실패 시)

        Logic:
        1. 좌표가 주어진 경우 → 검증 후 사용
        2. 주소가 주어진 경우 → Kakao Geocoding
        3. 둘 다 없는 경우 → 에러
        """
        try:
            # Case 1: 좌표가 주어진 경우
            if query.latitude is not None and query.longitude is not None:
                logger.info(f"Analyzing coordinates: ({query.latitude}, {query.longitude})")
                return await self._analyze_coordinates(
                    query.latitude,
                    query.longitude,
                    query.address,
                    query.radius,
                    query.category
                )

            # Case 2: 주소가 주어진 경우
            elif query.address:
                logger.info(f"Analyzing address: {query.address}")
                return await self._analyze_address(
                    query.address,
                    query.radius,
                    query.category
                )

            # Case 3: 둘 다 없는 경우
            else:
                logger.error("Neither coordinates nor address provided")
                return None

        except Exception as e:
            logger.error(f"Location analysis failed: {e}")
            return None

    async def _analyze_coordinates(
        self,
        latitude: float,
        longitude: float,
        address: Optional[str],
        radius: int,
        category: Optional[str]
    ) -> Optional[AnalyzedLocation]:
        """
        좌표 기반 분석

        Args:
            latitude: 위도
            longitude: 경도
            address: 주소 (선택)
            radius: 반경
            category: 카테고리

        Returns:
            AnalyzedLocation 또는 None
        """
        # 1. 좌표 정규화 (소수점 6자리)
        normalized_lat = round(latitude, 6)
        normalized_lon = round(longitude, 6)

        logger.debug(f"Normalized: ({normalized_lat}, {normalized_lon})")

        # 2. 서울 범위 검증
        if not self.coord_transformer.is_in_seoul(normalized_lat, normalized_lon):
            logger.warning(
                f"Coordinates ({normalized_lat}, {normalized_lon}) "
                "outside Seoul bounds"
            )
            # 서울 외곽도 허용 (경고만)

        # 3. 주소 조회 (없으면 Reverse Geocoding)
        final_address = address
        if not final_address:
            try:
                final_address = await self.kakao_service.reverse_geocode(
                    normalized_lat,
                    normalized_lon
                )
            except Exception as e:
                logger.warning(f"Reverse geocoding failed: {e}")
                final_address = None

        # 4. AnalyzedLocation 생성
        return AnalyzedLocation(
            latitude=normalized_lat,
            longitude=normalized_lon,
            address=final_address,
            radius=radius,
            category=category,
            source="coordinates",
            confidence=1.0
        )

    async def _analyze_address(
        self,
        address: str,
        radius: int,
        category: Optional[str]
    ) -> Optional[AnalyzedLocation]:
        """
        주소 기반 분석

        Args:
            address: 주소
            radius: 반경
            category: 카테고리

        Returns:
            AnalyzedLocation 또는 None
        """
        # 1. 주소 → 좌표 변환 (Kakao Geocoding)
        try:
            # 먼저 주소 검색 시도
            coords = await self.kakao_service.address_to_coordinates(address)

            # 주소 검색 실패 시 키워드 검색 시도
            if not coords:
                logger.info(f"Address search failed, trying keyword search for '{address}'")
                coords = await self.kakao_service.keyword_search(address)

            if not coords:
                logger.error(f"Failed to geocode address: {address}")
                return None

            latitude, longitude = coords

        except Exception as e:
            logger.error(f"Geocoding failed for '{address}': {e}")
            return None

        # 2. 좌표 정규화
        normalized_lat = round(latitude, 6)
        normalized_lon = round(longitude, 6)

        logger.info(f"Geocoded '{address}' → ({normalized_lat}, {normalized_lon})")

        # 3. 서울 범위 검증
        if not self.coord_transformer.is_in_seoul(normalized_lat, normalized_lon):
            logger.warning(f"Geocoded address '{address}' is outside Seoul bounds")

        # 4. AnalyzedLocation 생성
        return AnalyzedLocation(
            latitude=normalized_lat,
            longitude=normalized_lon,
            address=address,
            radius=radius,
            category=category,
            source="address",
            confidence=0.9  # 주소 변환은 약간 낮은 신뢰도
        )

    def validate_location(
        self,
        analyzed: AnalyzedLocation
    ) -> bool:
        """
        분석된 위치 검증

        Args:
            analyzed: 분석된 위치

        Returns:
            유효 여부
        """
        # 1. 좌표 범위 검증 (-90~90, -180~180)
        if not (-90 <= analyzed.latitude <= 90):
            logger.error(f"Invalid latitude: {analyzed.latitude}")
            return False

        if not (-180 <= analyzed.longitude <= 180):
            logger.error(f"Invalid longitude: {analyzed.longitude}")
            return False

        # 2. 반경 검증 (100m ~ 10km)
        if not (100 <= analyzed.radius <= 10000):
            logger.warning(f"Radius {analyzed.radius}m outside recommended range (100-10000m)")
            # 경고만, 차단하지 않음

        # 3. 신뢰도 검증
        if analyzed.confidence < 0.5:
            logger.warning(f"Low confidence: {analyzed.confidence}")

        return True

    async def analyze_batch(
        self,
        queries: list[LocationQuery]
    ) -> list[Optional[AnalyzedLocation]]:
        """
        배치 분석

        Args:
            queries: 위치 쿼리 리스트

        Returns:
            AnalyzedLocation 리스트
        """
        results = []
        for query in queries:
            result = await self.analyze(query)
            results.append(result)
        return results


# Convenience functions

async def analyze_location(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    address: Optional[str] = None,
    radius: int = 2000,
    category: Optional[str] = None
) -> Optional[AnalyzedLocation]:
    """
    위치 분석 (편의 함수)

    Args:
        latitude: 위도
        longitude: 경도
        address: 주소
        radius: 반경 (미터)
        category: 카테고리

    Returns:
        AnalyzedLocation 또는 None

    Example:
        >>> result = await analyze_location(latitude=37.5665, longitude=126.9780)
        >>> print(result.address)

        >>> result = await analyze_location(address="서울시청")
        >>> print(result.latitude, result.longitude)
    """
    analyzer = LocationAnalyzer()
    query = LocationQuery(
        latitude=latitude,
        longitude=longitude,
        address=address,
        radius=radius,
        category=category
    )
    return await analyzer.analyze(query)


def create_location_query(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    address: Optional[str] = None,
    radius: int = 2000,
    category: Optional[str] = None,
    category_priority: Optional[list[str]] = None
) -> LocationQuery:
    """
    LocationQuery 생성 (편의 함수)

    Args:
        latitude: 위도
        longitude: 경도
        address: 주소
        radius: 반경
        category: 카테고리
        category_priority: 카테고리 우선순위

    Returns:
        LocationQuery
    """
    return LocationQuery(
        latitude=latitude,
        longitude=longitude,
        address=address,
        radius=radius,
        category=category,
        category_priority=category_priority
    )
