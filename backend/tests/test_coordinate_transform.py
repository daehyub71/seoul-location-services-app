"""
좌표 변환 유틸리티 단위 테스트
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.utils.coordinate_transform import (
    CoordinateTransformer,
    haversine_distance,
    format_coordinates
)


class TestCoordinateTransformer:
    """CoordinateTransformer 테스트"""

    @pytest.fixture
    def transformer(self):
        """테스트용 transformer 인스턴스"""
        return CoordinateTransformer()

    def test_init(self, transformer):
        """초기화 테스트"""
        assert transformer.tm_to_wgs84 is not None
        assert transformer.wgs84_to_tm is not None

    def test_wgs84_to_tm_seoul_city_hall(self, transformer):
        """서울시청 WGS84 → TM 변환 테스트"""
        # 서울시청 좌표 (WGS84)
        lon, lat = 126.9780, 37.5665

        # TM 좌표로 변환
        x, y = transformer.wgs84_to_tm_coords(lon, lat)

        # 대략적인 TM 좌표 범위 확인
        assert 190000 < x < 210000  # 서울 중심부 X 좌표 범위
        assert 440000 < y < 460000  # 서울 중심부 Y 좌표 범위

    def test_tm_to_wgs84_seoul_city_hall(self, transformer):
        """서울시청 TM → WGS84 변환 테스트"""
        # 서울시청 근처 TM 좌표
        x, y = 198242.07, 451579.79

        # WGS84 좌표로 변환
        lon, lat = transformer.tm_to_wgs84_coords(x, y)

        # 서울시청 근처 좌표인지 확인
        assert 126.9 < lon < 127.0
        assert 37.5 < lat < 37.6

    def test_round_trip_conversion(self, transformer):
        """WGS84 → TM → WGS84 왕복 변환 테스트"""
        # 원본 WGS84 좌표
        original_lon, original_lat = 126.9780, 37.5665

        # WGS84 → TM
        x, y = transformer.wgs84_to_tm_coords(original_lon, original_lat)

        # TM → WGS84
        converted_lon, converted_lat = transformer.tm_to_wgs84_coords(x, y)

        # 오차 범위 확인 (< 0.0001도 = 약 11m)
        assert abs(original_lon - converted_lon) < 0.0001
        assert abs(original_lat - converted_lat) < 0.0001

    def test_is_in_seoul_true(self):
        """서울시 내 좌표 확인 테스트 (True)"""
        # 서울시청
        assert CoordinateTransformer.is_in_seoul(37.5665, 126.9780) is True

        # 강남역
        assert CoordinateTransformer.is_in_seoul(37.4979, 127.0276) is True

        # 광화문
        assert CoordinateTransformer.is_in_seoul(37.5760, 126.9769) is True

    def test_is_in_seoul_false(self):
        """서울시 외 좌표 확인 테스트 (False)"""
        # 부산
        assert CoordinateTransformer.is_in_seoul(35.1796, 129.0756) is False

        # 제주도
        assert CoordinateTransformer.is_in_seoul(33.4996, 126.5312) is False

        # 뉴욕
        assert CoordinateTransformer.is_in_seoul(40.7128, -74.0060) is False

    def test_validate_wgs84_basic(self):
        """기본 WGS84 좌표 유효성 검증 테스트"""
        # 유효한 좌표
        assert CoordinateTransformer.validate_wgs84(37.5665, 126.9780) is True
        assert CoordinateTransformer.validate_wgs84(0.0, 0.0) is True
        assert CoordinateTransformer.validate_wgs84(-90, -180) is True
        assert CoordinateTransformer.validate_wgs84(90, 180) is True

        # 유효하지 않은 좌표
        assert CoordinateTransformer.validate_wgs84(91, 0) is False  # 위도 범위 초과
        assert CoordinateTransformer.validate_wgs84(-91, 0) is False
        assert CoordinateTransformer.validate_wgs84(0, 181) is False  # 경도 범위 초과
        assert CoordinateTransformer.validate_wgs84(0, -181) is False

    def test_validate_wgs84_strict_mode(self):
        """Strict 모드 WGS84 좌표 유효성 검증 테스트"""
        # 서울 내 좌표 (strict=True)
        assert CoordinateTransformer.validate_wgs84(37.5665, 126.9780, strict=True) is True

        # 유효한 좌표지만 서울 외 (strict=True)
        assert CoordinateTransformer.validate_wgs84(35.1796, 129.0756, strict=True) is False

        # 유효하지 않은 좌표 (strict=True)
        assert CoordinateTransformer.validate_wgs84(91, 0, strict=True) is False

    def test_smart_convert_wgs84_input(self, transformer):
        """Smart Convert - WGS84 입력 테스트"""
        # WGS84 좌표 입력 (lon, lat 순서)
        lon, lat = 126.9780, 37.5665

        # 그대로 반환되어야 함
        result_lon, result_lat = transformer.smart_convert(lon, lat, guess_type=True)

        assert result_lon == lon
        assert result_lat == lat

    def test_smart_convert_tm_input(self, transformer):
        """Smart Convert - TM 입력 테스트"""
        # TM 좌표 입력
        coord1, coord2 = 200000, 450000

        # WGS84로 변환되어야 함
        result_lon, result_lat = transformer.smart_convert(coord1, coord2, guess_type=True)

        # 서울 근처 좌표인지 확인
        assert 126.0 < result_lon < 128.0
        assert 37.0 < result_lat < 38.0

    def test_smart_convert_no_guess(self, transformer):
        """Smart Convert - guess_type=False 테스트"""
        # guess_type=False이면 변환 없이 그대로 반환
        coord1, coord2 = 200000, 450000

        result1, result2 = transformer.smart_convert(coord1, coord2, guess_type=False)

        assert result1 == coord1
        assert result2 == coord2

    def test_seoul_bounds_constants(self):
        """서울시 경계 상수 테스트"""
        from app.core.config import settings
        bounds = settings.SEOUL_BOUNDS

        assert bounds['min_latitude'] == 37.0
        assert bounds['max_latitude'] == 38.0
        assert bounds['min_longitude'] == 126.0
        assert bounds['max_longitude'] == 128.0

    def test_crs_constants(self):
        """좌표계 상수 테스트"""
        assert CoordinateTransformer.CRS_WGS84 == "EPSG:4326"
        assert CoordinateTransformer.CRS_TM_CENTRAL == "EPSG:2097"
        assert CoordinateTransformer.CRS_TM_EAST == "EPSG:5186"
        assert CoordinateTransformer.CRS_TM_WEST == "EPSG:5185"


class TestHaversineDistance:
    """Haversine 거리 계산 테스트"""

    def test_zero_distance(self):
        """동일 좌표 거리 테스트 (0m)"""
        lat, lon = 37.5665, 126.9780
        distance = haversine_distance(lat, lon, lat, lon)

        assert distance == 0.0

    def test_seoul_city_hall_to_namsan_tower(self):
        """서울시청 ↔ 남산타워 거리 테스트 (약 1.93km)"""
        # 서울시청
        lat1, lon1 = 37.5665, 126.9780

        # 남산타워
        lat2, lon2 = 37.5511, 126.9882

        distance = haversine_distance(lat1, lon1, lat2, lon2)

        # 실제 거리는 약 1.93km
        assert 1900 < distance < 2000  # 1900m ~ 2000m

    def test_seoul_city_hall_to_gangnam_station(self):
        """서울시청 ↔ 강남역 거리 테스트 (약 8.8km)"""
        # 서울시청
        lat1, lon1 = 37.5665, 126.9780

        # 강남역
        lat2, lon2 = 37.4979, 127.0276

        distance = haversine_distance(lat1, lon1, lat2, lon2)

        # 실제 거리는 약 8.8km
        assert 8700 < distance < 8900  # 8700m ~ 8900m

    def test_large_distance(self):
        """장거리 테스트 (서울 ↔ 부산, 약 326km)"""
        # 서울
        lat1, lon1 = 37.5665, 126.9780

        # 부산
        lat2, lon2 = 35.1796, 129.0756

        distance = haversine_distance(lat1, lon1, lat2, lon2)

        # 실제 거리는 약 326km
        assert 320000 < distance < 330000  # 320km ~ 330km

    def test_symmetry(self):
        """거리 계산 대칭성 테스트 (A→B = B→A)"""
        lat1, lon1 = 37.5665, 126.9780
        lat2, lon2 = 37.4979, 127.0276

        distance1 = haversine_distance(lat1, lon1, lat2, lon2)
        distance2 = haversine_distance(lat2, lon2, lat1, lon1)

        assert distance1 == distance2

    def test_negative_coordinates(self):
        """음수 좌표 테스트"""
        # 남반구, 서반구 좌표도 정상 작동해야 함
        lat1, lon1 = -33.8688, 151.2093  # 시드니
        lat2, lon2 = -37.8136, 144.9631  # 멜버른

        distance = haversine_distance(lat1, lon1, lat2, lon2)

        # 시드니-멜버른 거리는 약 714km
        assert 700000 < distance < 730000


class TestFormatCoordinates:
    """좌표 포맷팅 테스트"""

    def test_default_precision(self):
        """기본 정밀도 테스트 (6자리)"""
        formatted = format_coordinates(37.5665, 126.9780)

        assert formatted == "37.566500, 126.978000"

    def test_custom_precision(self):
        """커스텀 정밀도 테스트"""
        # 2자리
        formatted = format_coordinates(37.5665, 126.9780, precision=2)
        assert formatted == "37.57, 126.98"

        # 4자리
        formatted = format_coordinates(37.5665, 126.9780, precision=4)
        assert formatted == "37.5665, 126.9780"

        # 8자리
        formatted = format_coordinates(37.5665, 126.9780, precision=8)
        assert formatted == "37.56650000, 126.97800000"

    def test_zero_precision(self):
        """0 정밀도 테스트 (정수)"""
        formatted = format_coordinates(37.5665, 126.9780, precision=0)

        assert formatted == "38, 127"

    def test_negative_coordinates(self):
        """음수 좌표 포맷팅 테스트"""
        formatted = format_coordinates(-33.8688, -151.2093, precision=4)

        assert formatted == "-33.8688, -151.2093"

    def test_zero_coordinates(self):
        """0 좌표 포맷팅 테스트"""
        formatted = format_coordinates(0.0, 0.0, precision=2)

        assert formatted == "0.00, 0.00"


# Edge cases and error handling
class TestEdgeCases:
    """엣지 케이스 및 에러 처리 테스트"""

    @pytest.fixture
    def transformer(self):
        return CoordinateTransformer()

    def test_extreme_tm_coordinates(self, transformer):
        """극단적인 TM 좌표 테스트"""
        # 매우 큰 TM 좌표는 변환은 되지만 서울 범위를 벗어남
        lon, lat = transformer.tm_to_wgs84_coords(9999999, 9999999)

        # 결과는 서울시 범위를 벗어남
        assert not CoordinateTransformer.is_in_seoul(lat, lon)

    def test_extreme_wgs84_coordinates(self, transformer):
        """극단적인 WGS84 좌표 테스트"""
        # 범위를 벗어난 WGS84 좌표는 validate_wgs84에서 False 반환
        assert CoordinateTransformer.validate_wgs84(200, 300) is False

    def test_boundary_coordinates_seoul(self):
        """서울시 경계 좌표 테스트"""
        # 경계 좌표 (경계 내부)
        assert CoordinateTransformer.is_in_seoul(37.0, 126.0) is True
        assert CoordinateTransformer.is_in_seoul(38.0, 128.0) is True

        # 경계 밖
        assert CoordinateTransformer.is_in_seoul(36.9999, 126.0) is False
        assert CoordinateTransformer.is_in_seoul(37.0, 125.9999) is False
