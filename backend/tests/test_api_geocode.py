"""
API Endpoint Tests for Geocoding
지오코딩 API 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from app.main import app


# Test Fixtures

@pytest.fixture
def client():
    """FastAPI Test Client"""
    return TestClient(app)


@pytest.fixture
def mock_kakao_service():
    """Mock Kakao Map Service"""
    with patch('app.api.v1.endpoints.geocode.get_kakao_map_service') as mock:
        service = Mock()

        # Default mock behaviors
        service.address_to_coordinates = AsyncMock(return_value=(37.5665, 126.9780))
        service.keyword_search = AsyncMock(return_value=(37.5665, 126.9780))
        service.reverse_geocode = AsyncMock(return_value="서울특별시 중구 세종대로 110")
        service.get_place_info = AsyncMock(return_value={
            'name': '서울시청',
            'address': '서울특별시 중구 세종대로 110',
            'road_address': '서울특별시 중구 세종대로 110',
            'latitude': 37.5665,
            'longitude': 126.9780,
            'category': 'public_office',
            'phone': '02-120'
        })

        mock.return_value = service
        yield service


# API Tests

class TestGeocodeEndpoint:
    """POST /api/v1/geocode 테스트 (주소 → 좌표)"""

    def test_geocode_with_landmark(self, client, mock_kakao_service):
        """랜드마크로 지오코딩 - 성공"""
        response = client.post(
            "/api/v1/geocode",
            json={'address': '서울시청'}
        )

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['address'] == '서울시청'
        assert data['latitude'] == 37.5665
        assert data['longitude'] == 126.9780
        assert data['source'] == 'kakao'

        # Verify Kakao service was called
        mock_kakao_service.address_to_coordinates.assert_called_once_with('서울시청')

    def test_geocode_with_full_address(self, client, mock_kakao_service):
        """전체 주소로 지오코딩"""
        response = client.post(
            "/api/v1/geocode",
            json={'address': '서울특별시 중구 세종대로 110'}
        )

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 37.0 <= data['latitude'] <= 38.0
        assert 126.0 <= data['longitude'] <= 128.0

    def test_geocode_with_keyword_fallback(self, client, mock_kakao_service):
        """주소 검색 실패 → 키워드 검색 폴백"""
        # Mock: address search fails, keyword search succeeds
        mock_kakao_service.address_to_coordinates = AsyncMock(return_value=None)
        mock_kakao_service.keyword_search = AsyncMock(return_value=(37.5665, 126.9780))

        response = client.post(
            "/api/v1/geocode",
            json={'address': '강남역'}
        )

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

        # Verify fallback was used
        mock_kakao_service.address_to_coordinates.assert_called_once()
        mock_kakao_service.keyword_search.assert_called_once()

    def test_geocode_not_found(self, client, mock_kakao_service):
        """지오코딩 실패 - 주소를 찾을 수 없음"""
        # Mock: both searches fail
        mock_kakao_service.address_to_coordinates = AsyncMock(return_value=None)
        mock_kakao_service.keyword_search = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/geocode",
            json={'address': '존재하지않는주소12345'}
        )

        # 검증
        assert response.status_code == 404
        data = response.json()
        assert 'detail' in data
        assert 'Could not geocode address' in data['detail']

    def test_geocode_missing_address(self, client):
        """주소 누락 - 에러"""
        response = client.post(
            "/api/v1/geocode",
            json={}
        )

        # 검증
        assert response.status_code == 422  # Validation error

    def test_geocode_empty_address(self, client):
        """빈 주소 - 에러"""
        response = client.post(
            "/api/v1/geocode",
            json={'address': ''}
        )

        # 검증
        assert response.status_code == 422  # Validation error

    def test_geocode_service_error(self, client, mock_kakao_service):
        """Kakao 서비스 에러"""
        # Mock service error
        mock_kakao_service.address_to_coordinates = AsyncMock(
            side_effect=Exception("Kakao API error")
        )

        response = client.post(
            "/api/v1/geocode",
            json={'address': '서울시청'}
        )

        # 검증
        assert response.status_code == 500


class TestReverseGeocodeEndpoint:
    """POST /api/v1/geocode/reverse 테스트 (좌표 → 주소)"""

    def test_reverse_geocode_success(self, client, mock_kakao_service):
        """역방향 지오코딩 - 성공"""
        response = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': 37.5665,
                'longitude': 126.9780
            }
        )

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['latitude'] == 37.5665
        assert data['longitude'] == 126.9780
        assert data['address'] == '서울특별시 중구 세종대로 110'

        # Check address type classification
        assert data['road_address'] is not None  # Contains "로"
        assert data['jibun_address'] is None  # Doesn't contain "동" or "가"

        # Verify service call
        mock_kakao_service.reverse_geocode.assert_called_once_with(37.5665, 126.9780)

    def test_reverse_geocode_jibun_address(self, client, mock_kakao_service):
        """역방향 지오코딩 - 지번 주소"""
        # Mock jibun address
        mock_kakao_service.reverse_geocode = AsyncMock(
            return_value="서울특별시 중구 태평로1가 31"
        )

        response = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': 37.5665,
                'longitude': 126.9780
            }
        )

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data['jibun_address'] is not None  # Contains "가"
        assert data['road_address'] is None

    def test_reverse_geocode_invalid_latitude(self, client):
        """잘못된 위도 - 범위 초과"""
        # Latitude > 90
        response = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': 95.0,
                'longitude': 126.9780
            }
        )
        assert response.status_code == 400

        # Latitude < -90
        response = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': -95.0,
                'longitude': 126.9780
            }
        )
        assert response.status_code == 400

    def test_reverse_geocode_invalid_longitude(self, client):
        """잘못된 경도 - 범위 초과"""
        # Longitude > 180
        response = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': 37.5665,
                'longitude': 185.0
            }
        )
        assert response.status_code == 400

        # Longitude < -180
        response = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': 37.5665,
                'longitude': -185.0
            }
        )
        assert response.status_code == 400

    def test_reverse_geocode_missing_coordinates(self, client):
        """좌표 누락 - 에러"""
        # Missing latitude
        response = client.post(
            "/api/v1/geocode/reverse",
            json={'longitude': 126.9780}
        )
        assert response.status_code == 422

        # Missing longitude
        response = client.post(
            "/api/v1/geocode/reverse",
            json={'latitude': 37.5665}
        )
        assert response.status_code == 422

    def test_reverse_geocode_not_found(self, client, mock_kakao_service):
        """역방향 지오코딩 실패 - 주소 없음"""
        # Mock: no address found
        mock_kakao_service.reverse_geocode = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': 37.5665,
                'longitude': 126.9780
            }
        )

        # 검증
        assert response.status_code == 404

    def test_reverse_geocode_ocean_coordinates(self, client, mock_kakao_service):
        """바다 좌표 - 주소 없음"""
        # Mock: ocean coordinates (no address)
        mock_kakao_service.reverse_geocode = AsyncMock(return_value=None)

        response = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': 35.0,
                'longitude': 129.0
            }
        )

        # 검증
        assert response.status_code == 404


class TestPlaceInfoEndpoint:
    """GET /api/v1/geocode/place/{place_name} 테스트"""

    def test_get_place_info_success(self, client, mock_kakao_service):
        """장소 정보 조회 - 성공"""
        response = client.get("/api/v1/geocode/place/서울시청")

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['name'] == '서울시청'
        assert data['address'] == '서울특별시 중구 세종대로 110'
        assert data['latitude'] == 37.5665
        assert data['longitude'] == 126.9780
        assert 'category' in data
        assert 'phone' in data

        # Verify service call
        mock_kakao_service.get_place_info.assert_called_once_with('서울시청')

    def test_get_place_info_with_spaces(self, client, mock_kakao_service):
        """공백 포함 장소명"""
        response = client.get("/api/v1/geocode/place/서울 시청")

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True

    def test_get_place_info_not_found(self, client, mock_kakao_service):
        """장소 정보 없음"""
        # Mock: place not found
        mock_kakao_service.get_place_info = AsyncMock(return_value=None)

        response = client.get("/api/v1/geocode/place/존재하지않는장소12345")

        # 검증
        assert response.status_code == 404

    def test_get_place_info_service_error(self, client, mock_kakao_service):
        """Kakao 서비스 에러"""
        # Mock service error
        mock_kakao_service.get_place_info = AsyncMock(
            side_effect=Exception("Kakao API error")
        )

        response = client.get("/api/v1/geocode/place/서울시청")

        # 검�
        assert response.status_code == 500


class TestGeocodeIntegrationScenarios:
    """지오코딩 통합 시나리오"""

    def test_full_geocode_workflow(self, client, mock_kakao_service):
        """전체 워크플로우: 주소 → 좌표 → 역방향 지오코딩"""
        # Step 1: Geocode address to coordinates
        response1 = client.post(
            "/api/v1/geocode",
            json={'address': '서울시청'}
        )
        assert response1.status_code == 200
        coords = response1.json()
        lat = coords['latitude']
        lon = coords['longitude']

        # Step 2: Reverse geocode back to address
        response2 = client.post(
            "/api/v1/geocode/reverse",
            json={
                'latitude': lat,
                'longitude': lon
            }
        )
        assert response2.status_code == 200
        address = response2.json()
        assert '서울' in address['address']

    def test_place_to_coordinates_workflow(self, client, mock_kakao_service):
        """장소 정보 조회 → 좌표 추출 워크플로우"""
        # Step 1: Get place info
        response = client.get("/api/v1/geocode/place/강남역")

        if response.status_code == 200:
            place = response.json()
            assert 'latitude' in place
            assert 'longitude' in place

            # Coordinates should be valid
            assert -90 <= place['latitude'] <= 90
            assert -180 <= place['longitude'] <= 180

    def test_multiple_geocode_requests(self, client, mock_kakao_service):
        """여러 주소 연속 지오코딩"""
        addresses = ['서울시청', '강남역', '광화문', '명동', '홍대입구']

        results = []
        for address in addresses:
            response = client.post(
                "/api/v1/geocode",
                json={'address': address}
            )
            if response.status_code == 200:
                results.append(response.json())

        # All should succeed (with mocked service)
        assert len(results) == len(addresses)

        # All should have valid coordinates
        for result in results:
            assert result['success'] is True
            assert 'latitude' in result
            assert 'longitude' in result


class TestGeocodeEdgeCases:
    """지오코딩 엣지 케이스"""

    def test_geocode_special_characters(self, client, mock_kakao_service):
        """특수문자 포함 주소"""
        response = client.post(
            "/api/v1/geocode",
            json={'address': '서울시청 (본관)'}
        )

        # Should handle gracefully
        assert response.status_code in [200, 404]

    def test_geocode_very_long_address(self, client, mock_kakao_service):
        """매우 긴 주소"""
        long_address = '서울특별시 ' * 50  # Very long

        response = client.post(
            "/api/v1/geocode",
            json={'address': long_address}
        )

        # Should handle gracefully (either succeed or fail gracefully)
        assert response.status_code in [200, 404, 422]

    def test_reverse_geocode_seoul_boundaries(self, client, mock_kakao_service):
        """서울 경계 좌표"""
        # North boundary
        response = client.post(
            "/api/v1/geocode/reverse",
            json={'latitude': 37.7, 'longitude': 127.0}
        )
        assert response.status_code in [200, 404]

        # South boundary
        response = client.post(
            "/api/v1/geocode/reverse",
            json={'latitude': 37.4, 'longitude': 127.0}
        )
        assert response.status_code in [200, 404]

    def test_reverse_geocode_exact_zero(self, client, mock_kakao_service):
        """정확히 0,0 좌표 (적도/본초자오선 교차점)"""
        response = client.post(
            "/api/v1/geocode/reverse",
            json={'latitude': 0.0, 'longitude': 0.0}
        )

        # Should be valid coordinates, but likely no address
        assert response.status_code in [200, 404]

    def test_geocode_korean_and_english_mixed(self, client, mock_kakao_service):
        """한글/영어 혼합 주소"""
        response = client.post(
            "/api/v1/geocode",
            json={'address': 'Seoul City Hall 서울시청'}
        )

        assert response.status_code in [200, 404]
