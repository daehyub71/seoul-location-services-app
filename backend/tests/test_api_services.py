"""
API Endpoint Tests for Services
서비스 검색 API 엔드포인트 테스트
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from app.main import app
from app.core.workflow.state import WorkflowState, LocationQuery, AnalyzedLocation, SearchResults, FormattedResponse


# Test Fixtures

@pytest.fixture
def client():
    """FastAPI Test Client"""
    return TestClient(app)


@pytest.fixture
def sample_workflow_state():
    """샘플 워크플로우 상태 (성공 케이스)"""
    return WorkflowState(
        query=LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000, category='libraries'),
        workflow_id='test-workflow-123',
        analyzed_location=AnalyzedLocation(
            latitude=37.5665,
            longitude=126.9780,
            address='서울시청',
            radius=2000,
            category='libraries',
            source='coordinates'
        ),
        search_results=SearchResults(
            locations=[
                {
                    'id': '1',
                    'library_name': '서울시립 중앙도서관',
                    'latitude': 37.5665,
                    'longitude': 126.9780,
                    'address': '서울시 중구 세종대로 110',
                    'distance': 150.5,
                    'distance_formatted': '150m',
                    '_table': 'libraries'
                },
                {
                    'id': '2',
                    'library_name': '강남도서관',
                    'latitude': 37.5170,
                    'longitude': 127.0470,
                    'address': '서울시 강남구 도곡로 401',
                    'distance': 1500.2,
                    'distance_formatted': '1.5km',
                    '_table': 'libraries'
                }
            ],
            total=2,
            category='libraries',
            search_center={'latitude': 37.5665, 'longitude': 126.9780},
            search_radius=2000,
            execution_time=0.234
        ),
        response=FormattedResponse(
            success=True,
            message='서울시청 주변 2.0km 내 도서관 2개를 찾았습니다.',
            locations=[
                {
                    'id': '1',
                    'library_name': '서울시립 중앙도서관',
                    'latitude': 37.5665,
                    'longitude': 126.9780,
                    'distance': 150.5,
                    'distance_formatted': '150m'
                },
                {
                    'id': '2',
                    'library_name': '강남도서관',
                    'latitude': 37.5170,
                    'longitude': 127.0470,
                    'distance': 1500.2,
                    'distance_formatted': '1.5km'
                }
            ],
            summary={
                'total_count': 2,
                'category_counts': {'libraries': 2},
                'search_center': {'latitude': 37.5665, 'longitude': 126.9780},
                'search_radius': 2000,
                'kakao_markers': [
                    {
                        'id': '1',
                        'lat': 37.5665,
                        'lon': 126.9780,
                        'title': '서울시립 중앙도서관',
                        'category': '도서관',
                        'distance': 150.5
                    }
                ]
            },
            workflow_id='test-workflow-123'
        )
    )


# API Tests

class TestNearbySearchEndpoint:
    """GET /api/v1/services/nearby 테스트"""

    def test_search_nearby_with_coordinates(self, client, sample_workflow_state):
        """좌표로 근처 검색 - 성공 케이스"""
        with patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:
            # Mock workflow execution
            mock_instance = Mock()
            mock_instance.run = AsyncMock(return_value=sample_workflow_state)
            mock_graph.return_value = mock_instance

            # API 요청
            response = client.get(
                "/api/v1/services/nearby",
                params={
                    'lat': 37.5665,
                    'lon': 126.9780,
                    'radius': 2000,
                    'category': 'libraries',
                    'limit': 50
                }
            )

            # 검증
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['message'] == '서울시청 주변 2.0km 내 도서관 2개를 찾았습니다.'
            assert len(data['locations']) == 2
            assert data['workflow_id'] == 'test-workflow-123'
            assert 'summary' in data
            assert data['summary']['total_count'] == 2

    def test_search_nearby_with_address(self, client, sample_workflow_state):
        """주소로 근처 검색 - 성공 케이스"""
        with patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:
            # Mock workflow execution
            mock_instance = Mock()
            mock_instance.run = AsyncMock(return_value=sample_workflow_state)
            mock_graph.return_value = mock_instance

            # API 요청
            response = client.get(
                "/api/v1/services/nearby",
                params={
                    'address': '서울시청',
                    'radius': 2000,
                    'limit': 50
                }
            )

            # 검증
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['locations']) == 2

    def test_search_nearby_missing_location(self, client):
        """위치 정보 없음 - 에러 케이스"""
        response = client.get(
            "/api/v1/services/nearby",
            params={
                'radius': 2000
            }
        )

        # 검증
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert 'detail' in data

    def test_search_nearby_partial_coordinates(self, client):
        """좌표 일부만 제공 - 에러 케이스"""
        response = client.get(
            "/api/v1/services/nearby",
            params={
                'lat': 37.5665,
                # lon missing
                'radius': 2000
            }
        )

        # 검증
        assert response.status_code == 422  # Validation error

    def test_search_nearby_invalid_radius(self, client):
        """반경 범위 초과 - 에러 케이스"""
        response = client.get(
            "/api/v1/services/nearby",
            params={
                'lat': 37.5665,
                'lon': 126.9780,
                'radius': 20000  # Max is 10000
            }
        )

        # 검증
        assert response.status_code == 422  # Validation error

    def test_search_nearby_invalid_category(self, client):
        """잘못된 카테고리 - 에러 케이스"""
        response = client.get(
            "/api/v1/services/nearby",
            params={
                'lat': 37.5665,
                'lon': 126.9780,
                'category': 'invalid_category',
                'radius': 2000
            }
        )

        # 검증
        assert response.status_code == 422  # Validation error

    def test_search_nearby_no_results(self, client):
        """결과 없음 시나리오"""
        with patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:
            # Mock workflow with no results
            no_results_state = WorkflowState(
                query=LocationQuery(latitude=37.5665, longitude=126.9780, radius=100),
                workflow_id='test-workflow-empty',
                analyzed_location=AnalyzedLocation(
                    latitude=37.5665,
                    longitude=126.9780,
                    radius=100,
                    source='coordinates'
                ),
                search_results=SearchResults(locations=[], total=0),
                response=FormattedResponse(
                    success=True,
                    message='검색 결과가 없습니다.',
                    locations=[],
                    summary={'total_count': 0}
                )
            )
            mock_instance = Mock()
            mock_instance.run = AsyncMock(return_value=no_results_state)
            mock_graph.return_value = mock_instance

            # API 요청
            response = client.get(
                "/api/v1/services/nearby",
                params={
                    'lat': 37.5665,
                    'lon': 126.9780,
                    'radius': 100
                }
            )

            # 검증
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert len(data['locations']) == 0


class TestCategorySearchEndpoint:
    """GET /api/v1/services/{category} 테스트"""

    def test_search_category_libraries(self, client, sample_workflow_state):
        """카테고리별 검색 - 도서관"""
        with patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:
            # Mock workflow execution
            mock_instance = Mock()
            mock_instance.run = AsyncMock(return_value=sample_workflow_state)
            mock_graph.return_value = mock_instance

            # API 요청
            response = client.get(
                "/api/v1/services/libraries",
                params={
                    'lat': 37.5665,
                    'lon': 126.9780,
                    'radius': 2000,
                    'limit': 50,
                    'sort_by': 'distance'
                }
            )

            # 검증
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['summary']['category_counts']['libraries'] == 2

    def test_search_category_cultural_events(self, client):
        """카테고리별 검색 - 문화행사"""
        with patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:
            # Mock workflow
            cultural_state = WorkflowState(
                query=LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000, category='cultural_events'),
                workflow_id='test-cultural',
                analyzed_location=AnalyzedLocation(
                    latitude=37.5665,
                    longitude=126.9780,
                    radius=2000,
                    category='cultural_events',
                    source='coordinates'
                ),
                search_results=SearchResults(
                    locations=[
                        {
                            'id': '1',
                            'title': '서울 문화 축제',
                            'lat': 37.5700,
                            'lot': 126.9800,
                            'distance': 500.0,
                            '_table': 'cultural_events'
                        }
                    ],
                    total=1,
                    category='cultural_events'
                ),
                response=FormattedResponse(
                    success=True,
                    message='문화행사 1개를 찾았습니다.',
                    locations=[{'id': '1', 'title': '서울 문화 축제'}],
                    summary={'total_count': 1}
                )
            )
            mock_instance = Mock()
            mock_instance.run = AsyncMock(return_value=cultural_state)
            mock_graph.return_value = mock_instance

            # API 요청
            response = client.get(
                "/api/v1/services/cultural_events",
                params={'lat': 37.5665, 'lon': 126.9780, 'radius': 2000}
            )

            # 검증
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True

    def test_search_category_invalid(self, client):
        """잘못된 카테고리"""
        response = client.get(
            "/api/v1/services/invalid_category",
            params={'lat': 37.5665, 'lon': 126.9780, 'radius': 2000}
        )

        # 검증
        assert response.status_code == 422  # Validation error

    def test_search_category_sorting(self, client, sample_workflow_state):
        """정렬 옵션 테스트"""
        with patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:
            mock_instance = Mock()
            mock_instance.run = AsyncMock(return_value=sample_workflow_state)
            mock_graph.return_value = mock_instance

            # Sort by distance
            response = client.get(
                "/api/v1/services/libraries",
                params={'lat': 37.5665, 'lon': 126.9780, 'radius': 2000, 'sort_by': 'distance'}
            )
            assert response.status_code == 200

            # Sort by name
            response = client.get(
                "/api/v1/services/libraries",
                params={'lat': 37.5665, 'lon': 126.9780, 'radius': 2000, 'sort_by': 'name'}
            )
            assert response.status_code == 200


class TestCategoriesListEndpoint:
    """GET /api/v1/services/categories/list 테스트"""

    def test_list_categories(self, client):
        """카테고리 목록 조회"""
        response = client.get("/api/v1/services/categories/list")

        # 검증
        assert response.status_code == 200
        data = response.json()
        assert 'categories' in data
        assert len(data['categories']) == 5

        # Check category structure
        categories = data['categories']
        for category in categories:
            assert 'id' in category
            assert 'name' in category
            assert 'name_en' in category
            assert 'description' in category
            assert 'icon' in category

        # Check specific categories exist
        category_ids = [c['id'] for c in categories]
        assert 'libraries' in category_ids
        assert 'cultural_events' in category_ids
        assert 'cultural_spaces' in category_ids
        assert 'future_heritages' in category_ids
        assert 'public_reservations' in category_ids


class TestServiceDetailEndpoint:
    """GET /api/v1/services/{category}/{item_id} 테스트"""

    def test_get_service_detail_success(self, client):
        """서비스 상세 조회 - 성공"""
        with patch('app.api.v1.endpoints.services.get_supabase_client') as mock_supabase, \
             patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:

            # Mock Supabase response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.data = [
                {
                    'id': '1',
                    'library_name': '서울시립 중앙도서관',
                    'latitude': 37.5665,
                    'longitude': 126.9780,
                    'address': '서울시 중구 세종대로 110',
                    'phone': '02-123-4567'
                }
            ]
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
            mock_supabase.return_value = mock_client

            # Mock workflow for nearby search
            nearby_state = WorkflowState(
                query=LocationQuery(latitude=37.5665, longitude=126.9780, radius=500, category='libraries'),
                workflow_id='nearby-123',
                response=FormattedResponse(
                    success=True,
                    message='Nearby libraries found',
                    locations=[
                        {
                            'id': '2',
                            'library_name': '다른 도서관',
                            'distance': 300.0
                        }
                    ],
                    summary={'total_count': 1}
                )
            )
            mock_graph_instance = Mock()
            mock_graph_instance.run = AsyncMock(return_value=nearby_state)
            mock_graph.return_value = mock_graph_instance

            # API 요청
            response = client.get("/api/v1/services/libraries/1")

            # 검증
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True
            assert data['item']['id'] == '1'
            assert data['item']['library_name'] == '서울시립 중앙도서관'
            assert 'nearby_services' in data
            assert len(data['nearby_services']) == 1

    def test_get_service_detail_not_found(self, client):
        """서비스 상세 조회 - 없는 항목"""
        with patch('app.api.v1.endpoints.services.get_supabase_client') as mock_supabase:
            # Mock empty response
            mock_client = Mock()
            mock_response = Mock()
            mock_response.data = []
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
            mock_supabase.return_value = mock_client

            # API 요청
            response = client.get("/api/v1/services/libraries/999")

            # 검증
            assert response.status_code == 404

    def test_get_service_detail_invalid_category(self, client):
        """서비스 상세 조회 - 잘못된 카테고리"""
        response = client.get("/api/v1/services/invalid_category/1")

        # 검증
        assert response.status_code == 404 or response.status_code == 422

    def test_get_service_detail_with_custom_radius(self, client):
        """서비스 상세 조회 - 커스텀 반경"""
        with patch('app.api.v1.endpoints.services.get_supabase_client') as mock_supabase, \
             patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:

            # Mock Supabase
            mock_client = Mock()
            mock_response = Mock()
            mock_response.data = [
                {
                    'id': '1',
                    'library_name': '도서관',
                    'latitude': 37.5665,
                    'longitude': 126.9780
                }
            ]
            mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
            mock_supabase.return_value = mock_client

            # Mock workflow
            mock_graph_instance = Mock()
            mock_graph_instance.run = AsyncMock(return_value=WorkflowState(
                query=LocationQuery(latitude=37.5665, longitude=126.9780, radius=1000),
                workflow_id='test',
                response=FormattedResponse(success=True, message='OK', locations=[], summary={})
            ))
            mock_graph.return_value = mock_graph_instance

            # API 요청
            response = client.get(
                "/api/v1/services/libraries/1",
                params={'nearby_radius': 1000}
            )

            # 검증
            assert response.status_code == 200
            data = response.json()
            assert data['success'] is True


class TestWorkflowErrors:
    """워크플로우 에러 시나리오 테스트"""

    def test_workflow_execution_error(self, client):
        """워크플로우 실행 중 에러"""
        with patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:
            # Mock workflow error
            mock_instance = Mock()
            mock_instance.run = AsyncMock(side_effect=Exception("Database connection failed"))
            mock_graph.return_value = mock_instance

            # API 요청
            response = client.get(
                "/api/v1/services/nearby",
                params={'lat': 37.5665, 'lon': 126.9780, 'radius': 2000}
            )

            # 검증
            assert response.status_code == 500

    def test_workflow_with_errors_list(self, client):
        """워크플로우 에러 리스트 반환"""
        with patch('app.api.v1.endpoints.services.get_service_graph') as mock_graph:
            # Mock workflow with errors
            error_state = WorkflowState(
                query=LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000),
                workflow_id='error-test',
                errors=['Failed to geocode address', 'Cache unavailable'],
                response=FormattedResponse(
                    success=True,
                    message='Partial results',
                    locations=[],
                    summary={'total_count': 0}
                )
            )
            mock_instance = Mock()
            mock_instance.run = AsyncMock(return_value=error_state)
            mock_graph.return_value = mock_instance

            # API 요청
            response = client.get(
                "/api/v1/services/nearby",
                params={'address': '존재하지않는주소', 'radius': 2000}
            )

            # 검증
            assert response.status_code == 200
            data = response.json()
            assert 'errors' in data
            assert len(data['errors']) == 2
