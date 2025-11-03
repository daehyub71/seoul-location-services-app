"""
Integration Tests for LangGraph Agents
LocationAnalyzer → ServiceFetcher → ResponseGenerator 통합 테스트
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any

from app.core.workflow.state import LocationQuery, AnalyzedLocation, SearchResults
from app.core.agents.location_analyzer import LocationAnalyzer
from app.core.agents.service_fetcher import ServiceFetcher
from app.core.agents.response_generator import ResponseGenerator


# Test Data Fixtures

@pytest.fixture
def sample_locations() -> List[Dict[str, Any]]:
    """샘플 위치 데이터"""
    return [
        {
            'id': '1',
            '_table': 'libraries',
            'library_name': '서울시립 중앙도서관',
            'latitude': 37.5665,
            'longitude': 126.9780,
            'address': '서울시 중구 세종대로 110',
            'distance': 150.5,
            'distance_formatted': '150m'
        },
        {
            'id': '2',
            '_table': 'cultural_events',
            'title': '서울 문화 축제',
            'lat': 37.5700,
            'lot': 126.9800,
            'place': '서울광장',
            'distance': 500.3,
            'distance_formatted': '500m'
        },
        {
            'id': '3',
            '_table': 'public_reservations',
            'service_name': '서울시청 회의실',
            'y_coord': 37.5663,
            'x_coord': 126.9779,
            'place_name': '서울시청',
            'distance': 25.8,
            'distance_formatted': '26m'
        }
    ]


@pytest.fixture
def mock_kakao_service():
    """Mock Kakao Map Service"""
    with patch('app.core.agents.location_analyzer.get_kakao_map_service') as mock:
        service = Mock()
        service.address_to_coordinates = AsyncMock(return_value=(37.5665, 126.9780))
        service.keyword_search = AsyncMock(return_value=(37.5665, 126.9780))
        service.reverse_geocode = AsyncMock(return_value="서울시 중구 세종대로 110")
        mock.return_value = service
        yield service


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase Client"""
    with patch('app.core.agents.service_fetcher.get_supabase_client') as mock:
        client = Mock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_redis_service():
    """Mock Redis Service"""
    with patch('app.core.agents.service_fetcher.get_redis_service') as mock:
        service = Mock()
        service.enabled = True
        service.get = Mock(return_value=None)  # Cache miss
        service.set = Mock(return_value=True)
        service.generate_cache_key = Mock(return_value="test:cache:key")
        mock.return_value = service
        yield service


# Integration Tests

class TestAgentWorkflow:
    """전체 에이전트 워크플로우 통합 테스트"""

    @pytest.mark.asyncio
    async def test_full_workflow_with_coordinates(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service,
        sample_locations
    ):
        """좌표 입력 → 전체 워크플로우 테스트"""
        # Setup
        query = LocationQuery(
            latitude=37.5665,
            longitude=126.9780,
            radius=2000,
            category='libraries'
        )

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = [
            {
                'id': '1',
                'library_name': '서울시립 중앙도서관',
                'latitude': 37.5665,
                'longitude': 126.9780,
                'address': '서울시 중구 세종대로 110',
                '_table': 'libraries'
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

        # Step 1: LocationAnalyzer
        analyzer = LocationAnalyzer()
        analyzed = await analyzer.analyze(query)

        assert analyzed is not None
        assert analyzed.latitude == 37.5665
        assert analyzed.longitude == 126.9780
        assert analyzed.source == "coordinates"

        # Step 2: ServiceFetcher
        fetcher = ServiceFetcher()
        results = await fetcher.fetch(analyzed, limit=20)

        assert results is not None
        assert results.total > 0
        assert results.category == 'libraries'

        # Step 3: ResponseGenerator
        generator = ResponseGenerator(use_llm=False)
        response = await generator.generate(results, analyzed)

        assert response.success is True
        assert len(response.locations) > 0
        assert '도서관' in response.message or 'Library' in response.message
        assert response.summary is not None

    @pytest.mark.asyncio
    async def test_full_workflow_with_address(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service,
        sample_locations
    ):
        """주소 입력 → 전체 워크플로우 테스트"""
        # Setup
        query = LocationQuery(
            address="서울시청",
            radius=1000,
            category='cultural_events'
        )

        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = [
            {
                'id': '1',
                'title': '서울 문화 축제',
                'lat': 37.5700,
                'lot': 126.9800,
                'place': '서울광장',
                '_table': 'cultural_events'
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

        # Step 1: LocationAnalyzer (주소 → 좌표 변환)
        analyzer = LocationAnalyzer()
        analyzed = await analyzer.analyze(query)

        assert analyzed is not None
        assert analyzed.latitude == 37.5665
        assert analyzed.longitude == 126.9780
        assert analyzed.source == "address"

        # Step 2: ServiceFetcher
        fetcher = ServiceFetcher()
        results = await fetcher.fetch(analyzed, limit=20)

        assert results is not None

        # Step 3: ResponseGenerator
        generator = ResponseGenerator(use_llm=False)
        response = await generator.generate(results, analyzed)

        assert response.success is True

    @pytest.mark.asyncio
    async def test_workflow_with_no_results(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """결과 없음 시나리오 테스트"""
        # Setup
        query = LocationQuery(
            latitude=37.5665,
            longitude=126.9780,
            radius=100  # 매우 작은 반경
        )

        # Mock empty Supabase response
        mock_response = Mock()
        mock_response.data = []
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

        # Execute workflow
        analyzer = LocationAnalyzer()
        analyzed = await analyzer.analyze(query)

        fetcher = ServiceFetcher()
        results = await fetcher.fetch(analyzed, limit=20)

        generator = ResponseGenerator(use_llm=False)
        response = await generator.generate(results, analyzed)

        # Verify
        assert response.success is True
        assert response.summary['total_count'] == 0
        assert '찾을 수 없습니다' in response.message or 'no results' in response.message.lower()


class TestCacheScenarios:
    """Redis 캐시 시나리오 테스트"""

    @pytest.mark.asyncio
    async def test_cache_miss_then_hit(
        self,
        mock_kakao_service,
        mock_supabase_client,
        sample_locations
    ):
        """캐시 미스 → 캐시 히트 시나리오"""
        with patch('app.core.agents.service_fetcher.get_redis_service') as mock_redis:
            # Setup Redis mock
            redis_service = Mock()
            redis_service.enabled = True

            # First call: cache miss
            call_count = {'get': 0}

            def mock_get(key):
                call_count['get'] += 1
                if call_count['get'] == 1:
                    return None  # First call: cache miss
                else:
                    return sample_locations  # Second call: cache hit

            redis_service.get = mock_get
            redis_service.set = Mock(return_value=True)
            redis_service.generate_cache_key = Mock(return_value="test:cache:key")
            mock_redis.return_value = redis_service

            # Mock Supabase response
            mock_response = Mock()
            mock_response.data = sample_locations
            mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

            # Setup
            analyzed = AnalyzedLocation(
                latitude=37.5665,
                longitude=126.9780,
                radius=2000,
                category='libraries',
                source='coordinates'
            )

            fetcher = ServiceFetcher()

            # First call: cache miss → Supabase query
            results1 = await fetcher.fetch(analyzed, limit=20)
            assert results1 is not None

            # Second call: cache hit → no Supabase query
            results2 = await fetcher.fetch(analyzed, limit=20)
            assert results2 is not None

            # Verify cache was used
            assert call_count['get'] == 2

    @pytest.mark.asyncio
    async def test_cache_disabled(
        self,
        mock_kakao_service,
        mock_supabase_client,
        sample_locations
    ):
        """캐시 비활성화 시나리오"""
        with patch('app.core.agents.service_fetcher.get_redis_service') as mock_redis:
            # Setup Redis mock (disabled)
            redis_service = Mock()
            redis_service.enabled = False
            mock_redis.return_value = redis_service

            # Mock Supabase response
            mock_response = Mock()
            mock_response.data = sample_locations
            mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

            # Setup
            analyzed = AnalyzedLocation(
                latitude=37.5665,
                longitude=126.9780,
                radius=2000,
                source='coordinates'
            )

            # Execute
            fetcher = ServiceFetcher()
            results = await fetcher.fetch(analyzed, limit=20)

            # Verify - should work without cache
            assert results is not None
            assert results.total > 0


class TestDistanceCalculation:
    """거리 계산 정확도 검증"""

    @pytest.mark.asyncio
    async def test_distance_sorting(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """거리순 정렬 검증"""
        # Mock Supabase response with multiple locations
        mock_response = Mock()
        mock_response.data = [
            {
                'id': '1',
                'library_name': 'Far Library',
                'latitude': 37.5800,  # ~1.5km away
                'longitude': 126.9900,
                '_table': 'libraries'
            },
            {
                'id': '2',
                'library_name': 'Near Library',
                'latitude': 37.5665,  # Very close
                'longitude': 126.9780,
                '_table': 'libraries'
            },
            {
                'id': '3',
                'library_name': 'Medium Library',
                'latitude': 37.5700,  # ~400m away
                'longitude': 126.9800,
                '_table': 'libraries'
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

        # Setup
        analyzed = AnalyzedLocation(
            latitude=37.5665,
            longitude=126.9780,
            radius=5000,  # 5km
            category='libraries',  # Specify category to match mock data
            source='coordinates'
        )

        # Execute
        fetcher = ServiceFetcher()
        results = await fetcher.fetch(analyzed, limit=20)

        # Verify sorting
        assert results is not None
        assert len(results.locations) == 3

        # Check distances are in ascending order
        distances = [loc['distance'] for loc in results.locations]
        assert distances == sorted(distances)

        # Nearest should be "Near Library"
        assert results.locations[0]['library_name'] == 'Near Library'

    @pytest.mark.asyncio
    async def test_radius_filtering(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """반경 필터링 검증"""
        # Mock Supabase response
        mock_response = Mock()
        mock_response.data = [
            {
                'id': '1',
                'library_name': 'Within Radius',
                'latitude': 37.5700,  # ~400m away
                'longitude': 126.9800,
                '_table': 'libraries'
            },
            {
                'id': '2',
                'library_name': 'Outside Radius',
                'latitude': 37.5900,  # ~2.7km away
                'longitude': 127.0000,
                '_table': 'libraries'
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

        # Setup - 1km radius
        analyzed = AnalyzedLocation(
            latitude=37.5665,
            longitude=126.9780,
            radius=1000,  # 1km only
            source='coordinates'
        )

        # Execute
        fetcher = ServiceFetcher()
        results = await fetcher.fetch(analyzed, limit=20)

        # Verify - only locations within 1km
        assert results is not None
        assert all(loc['distance'] <= 1000 for loc in results.locations)


class TestResponseGeneration:
    """응답 생성 테스트"""

    @pytest.mark.asyncio
    async def test_template_response_generation(self, sample_locations):
        """템플릿 기반 응답 생성"""
        # Setup
        search_results = SearchResults(
            locations=sample_locations,
            total=3,
            category='libraries',
            search_center={'latitude': 37.5665, 'longitude': 126.9780},
            search_radius=2000,
            execution_time=0.123
        )

        analyzed = AnalyzedLocation(
            latitude=37.5665,
            longitude=126.9780,
            address='서울시청',
            radius=2000,
            source='address'
        )

        # Execute
        generator = ResponseGenerator(use_llm=False)
        response = await generator.generate(search_results, analyzed)

        # Verify
        assert response.success is True
        assert '서울시청' in response.message
        assert '3개' in response.message
        assert response.summary is not None
        assert 'kakao_markers' in response.summary
        assert len(response.summary['kakao_markers']) == 3

    @pytest.mark.asyncio
    async def test_category_grouping(self, sample_locations):
        """카테고리별 그룹화 검증"""
        # Setup
        search_results = SearchResults(
            locations=sample_locations,
            total=3,
            search_center={'latitude': 37.5665, 'longitude': 126.9780},
            search_radius=2000
        )

        # Execute
        generator = ResponseGenerator(use_llm=False)
        response = await generator.generate(search_results)

        # Verify grouping
        grouped = response.summary['grouped_by_category']
        assert 'libraries' in grouped
        assert 'cultural_events' in grouped
        assert 'public_reservations' in grouped
        assert len(grouped['libraries']) == 1
        assert len(grouped['cultural_events']) == 1
        assert len(grouped['public_reservations']) == 1

    @pytest.mark.asyncio
    async def test_kakao_marker_generation(self, sample_locations):
        """Kakao Map 마커 데이터 생성 검증"""
        # Setup
        search_results = SearchResults(
            locations=sample_locations,
            total=3
        )

        # Execute
        generator = ResponseGenerator(use_llm=False)
        response = await generator.generate(search_results)

        # Verify markers
        markers = response.summary['kakao_markers']
        assert len(markers) == 3

        # Check marker structure
        for marker in markers:
            assert 'id' in marker
            assert 'lat' in marker
            assert 'lon' in marker
            assert 'title' in marker
            assert 'category' in marker
            assert 'distance' in marker

        # Check coordinate extraction for different tables
        lib_marker = next(m for m in markers if m['category'] == '도서관')
        assert lib_marker['lat'] == 37.5665
        assert lib_marker['lon'] == 126.9780

        event_marker = next(m for m in markers if m['category'] == '문화행사')
        assert event_marker['lat'] == 37.5700
        assert event_marker['lon'] == 126.9800

        reservation_marker = next(m for m in markers if m['category'] == '공공시설 예약')
        assert reservation_marker['lat'] == 37.5663
        assert reservation_marker['lon'] == 126.9779
