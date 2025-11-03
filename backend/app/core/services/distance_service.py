"""
Distance Calculation Service
Haversine 공식 기반 거리 계산 및 필터링
"""

import math
import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

# Earth radius in meters
EARTH_RADIUS_M = 6371000


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Haversine 공식을 사용한 두 지점 간 거리 계산

    Args:
        lat1: 지점1 위도 (degrees)
        lon1: 지점1 경도 (degrees)
        lat2: 지점2 위도 (degrees)
        lon2: 지점2 경도 (degrees)

    Returns:
        거리 (미터)

    Example:
        >>> haversine_distance(37.5665, 126.9780, 37.5651, 126.9895)
        897.42
    """
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine formula
    a = math.sin(dlat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))

    # Distance in meters
    distance = EARTH_RADIUS_M * c

    return distance


def calculate_distance_to_point(
    location: Dict[str, Any],
    target_lat: float,
    target_lon: float,
    lat_key: str = 'latitude',
    lon_key: str = 'longitude'
) -> float:
    """
    특정 지점으로부터의 거리 계산

    Args:
        location: 위치 데이터 딕셔너리
        target_lat: 목표 지점 위도
        target_lon: 목표 지점 경도
        lat_key: 위도 필드명
        lon_key: 경도 필드명

    Returns:
        거리 (미터), 좌표 없으면 float('inf')
    """
    lat = location.get(lat_key)
    lon = location.get(lon_key)

    if lat is None or lon is None:
        return float('inf')

    return haversine_distance(target_lat, target_lon, lat, lon)


def filter_by_radius(
    locations: List[Dict[str, Any]],
    center_lat: float,
    center_lon: float,
    radius_m: int,
    lat_key: str = 'latitude',
    lon_key: str = 'longitude'
) -> List[Dict[str, Any]]:
    """
    반경 내 위치 필터링

    Args:
        locations: 위치 데이터 리스트
        center_lat: 중심점 위도
        center_lon: 중심점 경도
        radius_m: 반경 (미터)
        lat_key: 위도 필드명
        lon_key: 경도 필드명

    Returns:
        반경 내 위치 리스트 (distance 필드 추가)

    Example:
        >>> locations = [
        ...     {"name": "A", "latitude": 37.5665, "longitude": 126.9780},
        ...     {"name": "B", "latitude": 37.5651, "longitude": 126.9895}
        ... ]
        >>> filtered = filter_by_radius(locations, 37.5665, 126.9780, 1000)
        >>> len(filtered)
        2
    """
    filtered = []

    for location in locations:
        distance = calculate_distance_to_point(
            location,
            center_lat,
            center_lon,
            lat_key,
            lon_key
        )

        # 좌표가 없거나 반경 밖이면 제외
        if distance == float('inf') or distance > radius_m:
            continue

        # distance 필드 추가
        location['distance'] = round(distance, 2)
        filtered.append(location)

    logger.debug(
        f"Filtered {len(filtered)}/{len(locations)} locations "
        f"within {radius_m}m radius"
    )

    return filtered


def sort_by_distance(
    locations: List[Dict[str, Any]],
    ascending: bool = True
) -> List[Dict[str, Any]]:
    """
    거리순 정렬

    Args:
        locations: 위치 데이터 리스트 (distance 필드 필요)
        ascending: True면 가까운 순, False면 먼 순

    Returns:
        정렬된 위치 리스트
    """
    return sorted(
        locations,
        key=lambda x: x.get('distance', float('inf')),
        reverse=not ascending
    )


def get_nearest_locations(
    locations: List[Dict[str, Any]],
    center_lat: float,
    center_lon: float,
    limit: int = 10,
    lat_key: str = 'latitude',
    lon_key: str = 'longitude'
) -> List[Dict[str, Any]]:
    """
    가장 가까운 N개 위치 조회

    Args:
        locations: 위치 데이터 리스트
        center_lat: 중심점 위도
        center_lon: 중심점 경도
        limit: 반환할 최대 개수
        lat_key: 위도 필드명
        lon_key: 경도 필드명

    Returns:
        가까운 순서로 정렬된 위치 리스트 (최대 limit개)
    """
    # 모든 위치에 distance 추가
    locations_with_distance = []
    for location in locations:
        distance = calculate_distance_to_point(
            location,
            center_lat,
            center_lon,
            lat_key,
            lon_key
        )
        if distance != float('inf'):
            location['distance'] = round(distance, 2)
            locations_with_distance.append(location)

    # 거리순 정렬
    sorted_locations = sort_by_distance(locations_with_distance, ascending=True)

    # limit 적용
    return sorted_locations[:limit]


def calculate_bounding_box(
    center_lat: float,
    center_lon: float,
    radius_m: int
) -> Tuple[float, float, float, float]:
    """
    중심점과 반경으로부터 경계 상자 (bounding box) 계산

    Args:
        center_lat: 중심점 위도
        center_lon: 중심점 경도
        radius_m: 반경 (미터)

    Returns:
        (min_lat, max_lat, min_lon, max_lon)

    Note:
        Haversine보다 빠른 사전 필터링용
        정확도는 약간 떨어지지만 큰 데이터셋에서 유용
    """
    # 위도 1도 = 약 111km
    # 경도 1도 = 약 111km * cos(latitude)
    lat_degree_km = 111.0
    lon_degree_km = 111.0 * math.cos(math.radians(center_lat))

    # 반경을 km로 변환
    radius_km = radius_m / 1000.0

    # 위도/경도 델타 계산
    lat_delta = radius_km / lat_degree_km
    lon_delta = radius_km / lon_degree_km

    # 경계 상자
    min_lat = center_lat - lat_delta
    max_lat = center_lat + lat_delta
    min_lon = center_lon - lon_delta
    max_lon = center_lon + lon_delta

    return (min_lat, max_lat, min_lon, max_lon)


def is_within_bounding_box(
    lat: float,
    lon: float,
    bbox: Tuple[float, float, float, float]
) -> bool:
    """
    좌표가 경계 상자 내부에 있는지 확인

    Args:
        lat: 위도
        lon: 경도
        bbox: (min_lat, max_lat, min_lon, max_lon)

    Returns:
        True if inside, False otherwise
    """
    min_lat, max_lat, min_lon, max_lon = bbox
    return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon


def filter_by_bounding_box(
    locations: List[Dict[str, Any]],
    bbox: Tuple[float, float, float, float],
    lat_key: str = 'latitude',
    lon_key: str = 'longitude'
) -> List[Dict[str, Any]]:
    """
    경계 상자로 위치 필터링 (빠른 사전 필터링)

    Args:
        locations: 위치 데이터 리스트
        bbox: (min_lat, max_lat, min_lon, max_lon)
        lat_key: 위도 필드명
        lon_key: 경도 필드명

    Returns:
        경계 상자 내 위치 리스트
    """
    filtered = []

    for location in locations:
        lat = location.get(lat_key)
        lon = location.get(lon_key)

        if lat is None or lon is None:
            continue

        if is_within_bounding_box(lat, lon, bbox):
            filtered.append(location)

    logger.debug(
        f"BBox filtered {len(filtered)}/{len(locations)} locations"
    )

    return filtered


def format_distance(distance_m: float) -> str:
    """
    거리를 읽기 쉬운 형태로 포맷

    Args:
        distance_m: 거리 (미터)

    Returns:
        포맷된 문자열 (예: "1.2km", "350m")
    """
    if distance_m >= 1000:
        return f"{distance_m / 1000:.1f}km"
    else:
        return f"{int(distance_m)}m"


# Convenience function for common use case
def find_nearby_locations(
    locations: List[Dict[str, Any]],
    center_lat: float,
    center_lon: float,
    radius_m: int = 1000,
    limit: Optional[int] = None,
    lat_key: str = 'latitude',
    lon_key: str = 'longitude'
) -> List[Dict[str, Any]]:
    """
    주변 위치 검색 (통합 함수)

    Args:
        locations: 위치 데이터 리스트
        center_lat: 중심점 위도
        center_lon: 중심점 경도
        radius_m: 반경 (미터)
        limit: 최대 반환 개수 (None이면 전체)
        lat_key: 위도 필드명
        lon_key: 경도 필드명

    Returns:
        반경 내 위치 리스트 (거리순 정렬, distance 필드 포함)
    """
    # 1. 경계 상자로 빠른 사전 필터링
    bbox = calculate_bounding_box(center_lat, center_lon, radius_m)
    pre_filtered = filter_by_bounding_box(locations, bbox, lat_key, lon_key)

    # 2. Haversine으로 정확한 거리 계산 및 필터링
    filtered = filter_by_radius(
        pre_filtered,
        center_lat,
        center_lon,
        radius_m,
        lat_key,
        lon_key
    )

    # 3. 거리순 정렬
    sorted_locations = sort_by_distance(filtered, ascending=True)

    # 4. limit 적용
    if limit:
        sorted_locations = sorted_locations[:limit]

    # 5. distance 포맷 추가
    for location in sorted_locations:
        if 'distance' in location:
            location['distance_formatted'] = format_distance(location['distance'])

    return sorted_locations
