"""
Unit tests for Distance Service
"""

import pytest
import math
from app.core.services import distance_service


class TestHaversineDistance:
    """Haversine 거리 계산 테스트"""

    def test_same_point(self):
        """같은 지점의 거리는 0"""
        distance = distance_service.haversine_distance(37.5665, 126.9780, 37.5665, 126.9780)
        assert distance == 0.0

    def test_seoul_city_hall_to_namsan(self):
        """서울시청 → 남산타워 거리 (약 1.9km)"""
        distance = distance_service.haversine_distance(
            37.5665, 126.9780,  # 서울시청
            37.5511, 126.9882   # 남산타워
        )
        # 약 1.9km (1800~2000m 범위)
        assert 1800 < distance < 2000

    def test_seoul_city_hall_to_gangnam_station(self):
        """서울시청 → 강남역 거리 (약 8.8km)"""
        distance = distance_service.haversine_distance(
            37.5665, 126.9780,  # 서울시청
            37.4979, 127.0276   # 강남역
        )
        # 약 8.8km (8500~9000m 범위)
        assert 8500 < distance < 9000


class TestCalculateDistanceToPoint:
    """특정 지점으로부터의 거리 계산 테스트"""

    def test_valid_location(self):
        """유효한 위치 데이터"""
        location = {'latitude': 37.5665, 'longitude': 126.9780}
        distance = distance_service.calculate_distance_to_point(
            location, 37.5511, 126.9882
        )
        assert 1800 < distance < 2000

    def test_missing_coordinates(self):
        """좌표 없는 위치 → inf 반환"""
        location = {'name': 'Test'}
        distance = distance_service.calculate_distance_to_point(
            location, 37.5665, 126.9780
        )
        assert distance == float('inf')

    def test_custom_keys(self):
        """커스텀 필드명"""
        location = {'lat': 37.5665, 'lon': 126.9780}
        distance = distance_service.calculate_distance_to_point(
            location, 37.5511, 126.9882,
            lat_key='lat', lon_key='lon'
        )
        assert 1800 < distance < 2000


class TestFilterByRadius:
    """반경 내 위치 필터링 테스트"""

    @pytest.fixture
    def sample_locations(self):
        """테스트용 위치 데이터"""
        return [
            {'name': '서울시청', 'latitude': 37.5665, 'longitude': 126.9780},
            {'name': '남산타워', 'latitude': 37.5511, 'longitude': 126.9882},
            {'name': '강남역', 'latitude': 37.4979, 'longitude': 127.0276},
            {'name': '인천공항', 'latitude': 37.4601, 'longitude': 126.4406},
            {'name': '좌표없음', 'name_only': True}
        ]

    def test_filter_1km_radius(self, sample_locations):
        """1km 반경 필터링 (서울시청 기준)"""
        filtered = distance_service.filter_by_radius(
            sample_locations,
            center_lat=37.5665,
            center_lon=126.9780,
            radius_m=1000
        )
        # 서울시청만 포함 (자기 자신)
        assert len(filtered) == 1
        assert filtered[0]['name'] == '서울시청'
        assert 'distance' in filtered[0]
        assert filtered[0]['distance'] == 0.0

    def test_filter_2km_radius(self, sample_locations):
        """2km 반경 필터링"""
        filtered = distance_service.filter_by_radius(
            sample_locations,
            center_lat=37.5665,
            center_lon=126.9780,
            radius_m=2000
        )
        # 서울시청 + 남산타워
        assert len(filtered) == 2
        names = [loc['name'] for loc in filtered]
        assert '서울시청' in names
        assert '남산타워' in names

    def test_filter_excludes_missing_coords(self, sample_locations):
        """좌표 없는 위치 제외"""
        filtered = distance_service.filter_by_radius(
            sample_locations,
            center_lat=37.5665,
            center_lon=126.9780,
            radius_m=50000  # 50km
        )
        # '좌표없음' 항목은 제외되어야 함
        names = [loc['name'] for loc in filtered]
        assert '좌표없음' not in names


class TestSortByDistance:
    """거리순 정렬 테스트"""

    def test_sort_ascending(self):
        """가까운 순 정렬"""
        locations = [
            {'name': 'C', 'distance': 3000},
            {'name': 'A', 'distance': 1000},
            {'name': 'B', 'distance': 2000}
        ]
        sorted_locs = distance_service.sort_by_distance(locations, ascending=True)
        assert [loc['name'] for loc in sorted_locs] == ['A', 'B', 'C']

    def test_sort_descending(self):
        """먼 순 정렬"""
        locations = [
            {'name': 'A', 'distance': 1000},
            {'name': 'B', 'distance': 2000},
            {'name': 'C', 'distance': 3000}
        ]
        sorted_locs = distance_service.sort_by_distance(locations, ascending=False)
        assert [loc['name'] for loc in sorted_locs] == ['C', 'B', 'A']


class TestGetNearestLocations:
    """가장 가까운 N개 위치 조회 테스트"""

    @pytest.fixture
    def sample_locations(self):
        return [
            {'name': 'A', 'latitude': 37.5665, 'longitude': 126.9780},
            {'name': 'B', 'latitude': 37.5651, 'longitude': 126.9895},
            {'name': 'C', 'latitude': 37.5700, 'longitude': 126.9800},
            {'name': 'D', 'latitude': 37.5600, 'longitude': 126.9700}
        ]

    def test_get_nearest_3(self, sample_locations):
        """가장 가까운 3개 조회"""
        nearest = distance_service.get_nearest_locations(
            sample_locations,
            center_lat=37.5665,
            center_lon=126.9780,
            limit=3
        )
        assert len(nearest) == 3
        # 첫 번째는 A (거리 0)
        assert nearest[0]['name'] == 'A'
        assert nearest[0]['distance'] == 0.0

    def test_limit_exceeds_total(self, sample_locations):
        """limit이 전체 개수보다 큼"""
        nearest = distance_service.get_nearest_locations(
            sample_locations,
            center_lat=37.5665,
            center_lon=126.9780,
            limit=10
        )
        assert len(nearest) == 4  # 전체 개수만큼만


class TestCalculateBoundingBox:
    """경계 상자 계산 테스트"""

    def test_bounding_box_1km(self):
        """1km 반경 경계 상자"""
        bbox = distance_service.calculate_bounding_box(
            center_lat=37.5665,
            center_lon=126.9780,
            radius_m=1000
        )
        min_lat, max_lat, min_lon, max_lon = bbox

        # 중심점이 경계 내에 있어야 함
        assert min_lat < 37.5665 < max_lat
        assert min_lon < 126.9780 < max_lon

        # 위도 차이 (약 0.009도 = 1km)
        lat_delta = max_lat - min_lat
        assert 0.015 < lat_delta < 0.020

    def test_bounding_box_symmetry(self):
        """경계 상자 대칭성"""
        bbox = distance_service.calculate_bounding_box(
            center_lat=37.5665,
            center_lon=126.9780,
            radius_m=1000
        )
        min_lat, max_lat, min_lon, max_lon = bbox

        # 중심에서 min/max까지의 거리가 같아야 함
        lat_center = (min_lat + max_lat) / 2
        lon_center = (min_lon + max_lon) / 2

        assert abs(lat_center - 37.5665) < 0.0001
        assert abs(lon_center - 126.9780) < 0.0001


class TestIsWithinBoundingBox:
    """경계 상자 내부 확인 테스트"""

    def test_point_inside(self):
        """경계 상자 내부 점"""
        bbox = (37.0, 38.0, 126.0, 128.0)
        assert distance_service.is_within_bounding_box(37.5, 127.0, bbox) is True

    def test_point_outside(self):
        """경계 상자 외부 점"""
        bbox = (37.0, 38.0, 126.0, 128.0)
        assert distance_service.is_within_bounding_box(36.5, 127.0, bbox) is False
        assert distance_service.is_within_bounding_box(37.5, 125.0, bbox) is False

    def test_point_on_boundary(self):
        """경계 상자 경계 위 점"""
        bbox = (37.0, 38.0, 126.0, 128.0)
        assert distance_service.is_within_bounding_box(37.0, 127.0, bbox) is True
        assert distance_service.is_within_bounding_box(38.0, 127.0, bbox) is True


class TestFilterByBoundingBox:
    """경계 상자로 위치 필터링 테스트"""

    @pytest.fixture
    def sample_locations(self):
        return [
            {'name': '서울', 'latitude': 37.5665, 'longitude': 126.9780},
            {'name': '부산', 'latitude': 35.1796, 'longitude': 129.0756},
            {'name': '제주', 'latitude': 33.4996, 'longitude': 126.5312}
        ]

    def test_filter_seoul_area(self, sample_locations):
        """서울 지역 경계 상자"""
        bbox = (37.0, 38.0, 126.0, 128.0)
        filtered = distance_service.filter_by_bounding_box(
            sample_locations, bbox
        )
        assert len(filtered) == 1
        assert filtered[0]['name'] == '서울'


class TestFormatDistance:
    """거리 포맷 테스트"""

    def test_format_meters(self):
        """미터 단위"""
        assert distance_service.format_distance(350) == "350m"
        assert distance_service.format_distance(999) == "999m"

    def test_format_kilometers(self):
        """킬로미터 단위"""
        assert distance_service.format_distance(1000) == "1.0km"
        assert distance_service.format_distance(1500) == "1.5km"
        assert distance_service.format_distance(12345) == "12.3km"


class TestFindNearbyLocations:
    """주변 위치 검색 통합 테스트"""

    @pytest.fixture
    def sample_locations(self):
        """서울 주요 지점"""
        return [
            {'name': '서울시청', 'latitude': 37.5665, 'longitude': 126.9780},
            {'name': '광화문', 'latitude': 37.5759, 'longitude': 126.9768},
            {'name': '남산타워', 'latitude': 37.5511, 'longitude': 126.9882},
            {'name': '강남역', 'latitude': 37.4979, 'longitude': 127.0276},
            {'name': '홍대입구', 'latitude': 37.5579, 'longitude': 126.9227}
        ]

    def test_find_nearby_2km(self, sample_locations):
        """2km 반경 검색"""
        results = distance_service.find_nearby_locations(
            sample_locations,
            center_lat=37.5665,
            center_lon=126.9780,
            radius_m=2000
        )
        # 서울시청, 광화문, 남산타워 (홍대입구, 강남역 제외)
        assert len(results) == 3
        # 첫 번째는 서울시청 (거리 0)
        assert results[0]['name'] == '서울시청'
        # distance_formatted 필드 존재
        assert all('distance_formatted' in loc for loc in results)

    def test_find_nearby_with_limit(self, sample_locations):
        """반경 + limit 조합"""
        results = distance_service.find_nearby_locations(
            sample_locations,
            center_lat=37.5665,
            center_lon=126.9780,
            radius_m=5000,
            limit=2
        )
        assert len(results) == 2
        # 가장 가까운 2개만
        assert results[0]['name'] == '서울시청'

    def test_find_nearby_sorted_by_distance(self, sample_locations):
        """거리순 정렬 확인"""
        results = distance_service.find_nearby_locations(
            sample_locations,
            center_lat=37.5665,
            center_lon=126.9780,
            radius_m=10000
        )
        # 거리가 증가하는 순서여야 함
        distances = [loc['distance'] for loc in results]
        assert distances == sorted(distances)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
