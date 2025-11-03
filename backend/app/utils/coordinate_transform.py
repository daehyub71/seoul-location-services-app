"""
좌표 변환 유틸리티
TM 좌표계 <-> WGS84 좌표계 변환
"""

import logging
from typing import Tuple, Optional
from pyproj import Transformer, CRS

from app.core.config import settings

logger = logging.getLogger(__name__)


class CoordinateTransformer:
    """
    좌표 변환 클래스

    Features:
    - TM 좌표 → WGS84 (위도/경도)
    - WGS84 → TM 좌표
    - 서울시 범위 검증
    """

    # 서울시 경계 (settings에서 가져옴)
    @property
    def SEOUL_BOUNDS(self):
        return settings.SEOUL_BOUNDS

    # 좌표계 정의
    CRS_WGS84 = "EPSG:4326"      # WGS84 (위도/경도)
    CRS_TM_CENTRAL = "EPSG:2097" # TM 중부원점 (서울 포함)
    CRS_TM_EAST = "EPSG:5186"    # TM 동부원점
    CRS_TM_WEST = "EPSG:5185"    # TM 서부원점

    def __init__(self):
        """
        Transformer 초기화
        """
        # TM 중부원점 → WGS84 (가장 많이 사용)
        self.tm_to_wgs84 = Transformer.from_crs(
            self.CRS_TM_CENTRAL,
            self.CRS_WGS84,
            always_xy=True
        )

        # WGS84 → TM 중부원점
        self.wgs84_to_tm = Transformer.from_crs(
            self.CRS_WGS84,
            self.CRS_TM_CENTRAL,
            always_xy=True
        )

        logger.info("CoordinateTransformer initialized")

    def tm_to_wgs84_coords(self, x: float, y: float) -> Tuple[float, float]:
        """
        TM 좌표 → WGS84 좌표 변환

        Args:
            x: TM X 좌표 (동쪽 방향)
            y: TM Y 좌표 (북쪽 방향)

        Returns:
            (경도, 위도) 튜플

        Example:
            >>> transformer = CoordinateTransformer()
            >>> lon, lat = transformer.tm_to_wgs84_coords(200000, 450000)
            >>> print(f"위도: {lat}, 경도: {lon}")
        """
        try:
            lon, lat = self.tm_to_wgs84.transform(x, y)
            logger.debug(f"TM ({x}, {y}) → WGS84 ({lon:.6f}, {lat:.6f})")
            return lon, lat
        except Exception as e:
            logger.error(f"TM to WGS84 conversion failed: {e}")
            raise ValueError(f"Invalid TM coordinates: ({x}, {y})")

    def wgs84_to_tm_coords(self, lon: float, lat: float) -> Tuple[float, float]:
        """
        WGS84 좌표 → TM 좌표 변환

        Args:
            lon: 경도 (longitude)
            lat: 위도 (latitude)

        Returns:
            (TM X, TM Y) 튜플

        Example:
            >>> transformer = CoordinateTransformer()
            >>> x, y = transformer.wgs84_to_tm_coords(126.9780, 37.5665)
            >>> print(f"TM X: {x}, TM Y: {y}")
        """
        try:
            x, y = self.wgs84_to_tm.transform(lon, lat)
            logger.debug(f"WGS84 ({lon:.6f}, {lat:.6f}) → TM ({x:.2f}, {y:.2f})")
            return x, y
        except Exception as e:
            logger.error(f"WGS84 to TM conversion failed: {e}")
            raise ValueError(f"Invalid WGS84 coordinates: ({lon}, {lat})")

    @staticmethod
    def is_in_seoul(lat: float, lon: float) -> bool:
        """
        좌표가 서울시 범위 내에 있는지 확인

        Args:
            lat: 위도
            lon: 경도

        Returns:
            서울시 내 위치 여부
        """
        bounds = settings.SEOUL_BOUNDS
        return (
            bounds['min_latitude'] <= lat <= bounds['max_latitude'] and
            bounds['min_longitude'] <= lon <= bounds['max_longitude']
        )

    @classmethod
    def validate_wgs84(cls, lat: float, lon: float, strict: bool = False) -> bool:
        """
        WGS84 좌표 유효성 검증

        Args:
            lat: 위도 (-90 ~ 90)
            lon: 경도 (-180 ~ 180)
            strict: True이면 서울시 범위 내 여부까지 확인

        Returns:
            유효 여부
        """
        # 기본 범위 확인
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            logger.warning(f"Invalid WGS84 range: lat={lat}, lon={lon}")
            return False

        # 서울시 범위 확인 (strict 모드)
        if strict and not cls.is_in_seoul(lat, lon):
            logger.warning(f"Coordinates outside Seoul: lat={lat}, lon={lon}")
            return False

        return True

    def smart_convert(
        self,
        coord1: float,
        coord2: float,
        guess_type: bool = True
    ) -> Tuple[float, float]:
        """
        좌표계 자동 감지 및 변환

        Args:
            coord1: 첫 번째 좌표
            coord2: 두 번째 좌표
            guess_type: True이면 좌표계 자동 추론

        Returns:
            (경도, 위도) 튜플 (항상 WGS84로 반환)

        Logic:
        - coord1, coord2가 모두 -180~180 범위면 WGS84로 간주
        - 그 외에는 TM 좌표로 간주하고 변환
        """
        if guess_type:
            # WGS84 범위 확인
            if (-180 <= coord1 <= 180 and -90 <= coord2 <= 90):
                # 이미 WGS84로 추정
                logger.debug(f"Detected WGS84: ({coord1}, {coord2})")
                return coord1, coord2
            else:
                # TM 좌표로 추정하고 변환
                logger.debug(f"Detected TM, converting: ({coord1}, {coord2})")
                return self.tm_to_wgs84_coords(coord1, coord2)
        else:
            # 변환 없이 그대로 반환
            return coord1, coord2


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Haversine 공식을 이용한 두 지점 간 거리 계산 (미터)

    Args:
        lat1: 첫 번째 지점 위도
        lon1: 첫 번째 지점 경도
        lat2: 두 번째 지점 위도
        lon2: 두 번째 지점 경도

    Returns:
        거리 (미터)

    Example:
        >>> # 서울시청 ↔ 남산타워
        >>> distance = haversine_distance(37.5665, 126.9780, 37.5511, 126.9882)
        >>> print(f"거리: {distance:.0f}m")
    """
    from math import radians, sin, cos, sqrt, atan2

    # 지구 반지름 (미터)
    R = 6371000

    # 라디안 변환
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # 차이
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Haversine 공식
    a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


def format_coordinates(lat: float, lon: float, precision: int = 6) -> str:
    """
    좌표를 포맷팅된 문자열로 변환

    Args:
        lat: 위도
        lon: 경도
        precision: 소수점 자릿수

    Returns:
        포맷팅된 문자열 (예: "37.566500, 126.978000")
    """
    return f"{lat:.{precision}f}, {lon:.{precision}f}"


def main():
    """테스트용 메인 함수"""
    print("\n" + "="*60)
    print("좌표 변환 유틸리티 테스트")
    print("="*60)

    transformer = CoordinateTransformer()

    # 테스트 1: 서울시청 좌표
    print("\n1. 서울시청 (WGS84)")
    seoul_lat, seoul_lon = 37.5665, 126.9780
    print(f"   위도: {seoul_lat}, 경도: {seoul_lon}")
    print(f"   서울시 내: {CoordinateTransformer.is_in_seoul(seoul_lat, seoul_lon)}")
    print(f"   유효성: {CoordinateTransformer.validate_wgs84(seoul_lat, seoul_lon, strict=True)}")

    # 테스트 2: WGS84 → TM
    print("\n2. WGS84 → TM 변환")
    tm_x, tm_y = transformer.wgs84_to_tm_coords(seoul_lon, seoul_lat)
    print(f"   TM X: {tm_x:.2f}, TM Y: {tm_y:.2f}")

    # 테스트 3: TM → WGS84 (역변환)
    print("\n3. TM → WGS84 역변환")
    lon_back, lat_back = transformer.tm_to_wgs84_coords(tm_x, tm_y)
    print(f"   위도: {lat_back:.6f}, 경도: {lon_back:.6f}")
    print(f"   오차: {abs(seoul_lat - lat_back):.10f}, {abs(seoul_lon - lon_back):.10f}")

    # 테스트 4: 거리 계산
    print("\n4. 거리 계산 (서울시청 ↔ 남산타워)")
    namsan_lat, namsan_lon = 37.5511, 126.9882
    distance = haversine_distance(seoul_lat, seoul_lon, namsan_lat, namsan_lon)
    print(f"   거리: {distance:.0f}m ({distance/1000:.2f}km)")

    # 테스트 5: Smart Convert
    print("\n5. Smart Convert (자동 감지)")
    test_coords = [
        (37.5665, 126.9780),  # WGS84
        (200000, 450000),     # TM
    ]

    for c1, c2 in test_coords:
        lon, lat = transformer.smart_convert(c1, c2)
        print(f"   입력: ({c1}, {c2}) → WGS84: ({lon:.6f}, {lat:.6f})")

    print("\n" + "="*60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    main()
