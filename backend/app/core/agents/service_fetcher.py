"""
ServiceFetcher Agent
서비스 조회 에이전트 - Supabase 데이터 조회 및 거리 계산
"""

import logging
from typing import Optional, List, Dict, Any
import time

from app.core.workflow.state import AnalyzedLocation, SearchResults
from app.db.supabase_client import get_supabase_client
from app.core.services.redis_service import get_redis_service
from app.core.services.distance_service import (
    calculate_distance_to_point,
    sort_by_distance,
    format_distance
)

logger = logging.getLogger(__name__)


class ServiceFetcher:
    """
    서비스 조회 에이전트

    기능:
    1. Redis 캐시 조회 (캐시 히트 시 즉시 반환)
    2. Supabase PostGIS 공간 쿼리
    3. Haversine 거리 계산 및 정렬
    4. Redis 캐시 저장 (TTL 5분)
    """

    # 테이블명 매핑
    TABLE_MAP = {
        'cultural_events': 'cultural_events',
        'libraries': 'libraries',
        'cultural_spaces': 'cultural_spaces',
        'future_heritages': 'future_heritages',
        'public_reservations': 'public_reservations'
    }

    def __init__(self):
        """ServiceFetcher 초기화"""
        self.supabase = get_supabase_client()
        self.redis = get_redis_service()
        logger.info("ServiceFetcher initialized")

    async def fetch(
        self,
        analyzed_location: AnalyzedLocation,
        limit: int = 20
    ) -> Optional[SearchResults]:
        """
        서비스 조회

        Args:
            analyzed_location: 분석된 위치
            limit: 최대 결과 개수

        Returns:
            SearchResults 또는 None
        """
        start_time = time.time()

        try:
            # 1. Redis 캐시 조회
            cached = await self._check_cache(analyzed_location)
            if cached:
                execution_time = time.time() - start_time
                logger.info(f"Cache HIT - Execution time: {execution_time:.3f}s")
                return SearchResults(
                    locations=cached,
                    total=len(cached),
                    category=analyzed_location.category,
                    search_center={
                        'latitude': analyzed_location.latitude,
                        'longitude': analyzed_location.longitude
                    },
                    search_radius=analyzed_location.radius,
                    execution_time=execution_time
                )

            # 2. Supabase 쿼리
            locations = await self._fetch_from_supabase(
                analyzed_location,
                limit
            )

            if not locations:
                logger.warning("No locations found")
                return SearchResults(
                    locations=[],
                    total=0,
                    category=analyzed_location.category,
                    search_center={
                        'latitude': analyzed_location.latitude,
                        'longitude': analyzed_location.longitude
                    },
                    search_radius=analyzed_location.radius,
                    execution_time=time.time() - start_time
                )

            # 3. 거리 계산 및 정렬
            locations_with_distance = self._add_distances(
                locations,
                analyzed_location.latitude,
                analyzed_location.longitude
            )

            # 4. 반경 내 필터링
            filtered = [
                loc for loc in locations_with_distance
                if loc.get('distance') is not None and loc.get('distance') <= analyzed_location.radius
            ]

            # 5. 거리순 정렬
            sorted_locations = sort_by_distance(filtered, ascending=True)

            # 6. Limit 적용
            final_locations = sorted_locations[:limit]

            # 7. Redis 캐시 저장
            await self._save_cache(analyzed_location, final_locations)

            execution_time = time.time() - start_time
            logger.info(
                f"Fetched {len(final_locations)} locations "
                f"in {execution_time:.3f}s"
            )

            return SearchResults(
                locations=final_locations,
                total=len(final_locations),
                category=analyzed_location.category,
                search_center={
                    'latitude': analyzed_location.latitude,
                    'longitude': analyzed_location.longitude
                },
                search_radius=analyzed_location.radius,
                execution_time=execution_time
            )

        except Exception as e:
            logger.error(f"Service fetch failed: {e}")
            return None

    async def _check_cache(
        self,
        analyzed_location: AnalyzedLocation
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Redis 캐시 조회

        Args:
            analyzed_location: 분석된 위치

        Returns:
            캐시된 위치 리스트 또는 None
        """
        if not self.redis.enabled:
            return None

        # 캐시 키 생성
        cache_key = self.redis.generate_cache_key(
            analyzed_location.latitude,
            analyzed_location.longitude,
            analyzed_location.radius,
            analyzed_location.category
        )

        # 캐시 조회
        cached = self.redis.get(cache_key)
        return cached

    async def _save_cache(
        self,
        analyzed_location: AnalyzedLocation,
        locations: List[Dict[str, Any]]
    ) -> bool:
        """
        Redis 캐시 저장

        Args:
            analyzed_location: 분석된 위치
            locations: 위치 리스트

        Returns:
            성공 여부
        """
        if not self.redis.enabled:
            return False

        # 캐시 키 생성
        cache_key = self.redis.generate_cache_key(
            analyzed_location.latitude,
            analyzed_location.longitude,
            analyzed_location.radius,
            analyzed_location.category
        )

        # 캐시 저장 (TTL 5분)
        return self.redis.set(cache_key, locations, ttl=300)

    async def _fetch_from_supabase(
        self,
        analyzed_location: AnalyzedLocation,
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Supabase에서 데이터 조회

        Args:
            analyzed_location: 분석된 위치
            limit: 최대 결과 개수

        Returns:
            위치 리스트
        """
        # 카테고리 결정
        if analyzed_location.category:
            tables = [self.TABLE_MAP.get(analyzed_location.category)]
        else:
            # 전체 테이블 조회
            tables = list(self.TABLE_MAP.values())

        all_locations = []

        for table in tables:
            if not table:
                continue

            try:
                # PostGIS 공간 쿼리는 복잡하므로 전체 조회 후 필터링
                # (Supabase Python 클라이언트는 ST_DWithin 직접 지원 안 함)
                logger.debug(f"Querying table: {table}")

                response = self.supabase.table(table).select('*').execute()

                if response.data:
                    # 테이블명 추가
                    for item in response.data:
                        item['_table'] = table
                    all_locations.extend(response.data)

            except Exception as e:
                logger.error(f"Supabase query failed for table {table}: {e}")
                continue

        logger.info(f"Fetched {len(all_locations)} raw locations from Supabase")
        return all_locations

    def _add_distances(
        self,
        locations: List[Dict[str, Any]],
        center_lat: float,
        center_lon: float
    ) -> List[Dict[str, Any]]:
        """
        위치 리스트에 거리 추가

        Args:
            locations: 위치 리스트
            center_lat: 중심 위도
            center_lon: 중심 경도

        Returns:
            거리가 추가된 위치 리스트
        """
        for location in locations:
            # 테이블별 좌표 필드명이 다름
            table = location.get('_table')

            if table == 'public_reservations':
                lat_key, lon_key = 'y_coord', 'x_coord'
            elif table == 'cultural_events':
                lat_key, lon_key = 'lat', 'lot'
            else:
                lat_key, lon_key = 'latitude', 'longitude'

            try:
                distance = calculate_distance_to_point(
                    location,
                    center_lat,
                    center_lon,
                    lat_key=lat_key,
                    lon_key=lon_key
                )

                location['distance'] = round(distance, 2) if distance != float('inf') else None
                location['distance_formatted'] = format_distance(distance) if distance != float('inf') else None
            except Exception as e:
                logger.warning(f"Failed to calculate distance for location {location.get('id')}: {e}")
                location['distance'] = None
                location['distance_formatted'] = None

        return locations

    async def fetch_by_category(
        self,
        analyzed_location: AnalyzedLocation,
        categories: List[str],
        limit_per_category: int = 10
    ) -> Dict[str, SearchResults]:
        """
        카테고리별 조회

        Args:
            analyzed_location: 분석된 위치
            categories: 카테고리 리스트
            limit_per_category: 카테고리당 최대 개수

        Returns:
            {category: SearchResults} 딕셔너리
        """
        results = {}

        for category in categories:
            # 임시 AnalyzedLocation 생성
            temp_location = AnalyzedLocation(
                latitude=analyzed_location.latitude,
                longitude=analyzed_location.longitude,
                address=analyzed_location.address,
                radius=analyzed_location.radius,
                category=category,
                source=analyzed_location.source,
                confidence=analyzed_location.confidence
            )

            result = await self.fetch(temp_location, limit=limit_per_category)
            if result:
                results[category] = result

        return results


# Convenience function

async def fetch_services(
    latitude: float,
    longitude: float,
    radius: int = 2000,
    category: Optional[str] = None,
    limit: int = 20
) -> Optional[SearchResults]:
    """
    서비스 조회 (편의 함수)

    Args:
        latitude: 위도
        longitude: 경도
        radius: 반경 (미터)
        category: 카테고리
        limit: 최대 결과 개수

    Returns:
        SearchResults 또는 None

    Example:
        >>> results = await fetch_services(37.5665, 126.9780, radius=1000, category="libraries")
        >>> print(f"Found {results.total} libraries")
    """
    fetcher = ServiceFetcher()

    analyzed_location = AnalyzedLocation(
        latitude=latitude,
        longitude=longitude,
        radius=radius,
        category=category,
        source="coordinates"
    )

    return await fetcher.fetch(analyzed_location, limit=limit)
