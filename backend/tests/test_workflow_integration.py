"""
LangGraph Workflow Integration Tests
전체 워크플로우 통합 테스트 (service_graph.py)
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import uuid

from app.core.workflow.state import WorkflowState, LocationQuery, AnalyzedLocation, SearchResults, FormattedResponse
from app.core.workflow.service_graph import ServiceSearchGraph, get_service_graph, search_services


# Test Fixtures

@pytest.fixture
def mock_kakao_service():
    """Mock Kakao Map Service"""
    with patch('app.core.agents.location_analyzer.get_kakao_map_service') as mock:
        service = Mock()
        service.address_to_coordinates = AsyncMock(return_value=(37.5665, 126.9780))
        service.keyword_search = AsyncMock(return_value=(37.5665, 126.9780))
        service.reverse_geocode = AsyncMock(return_value="서울특별시 중구 세종대로 110")
        mock.return_value = service
        yield service


@pytest.fixture
def mock_supabase_client():
    """Mock Supabase Client"""
    with patch('app.core.agents.service_fetcher.get_supabase_client') as mock:
        client = Mock()

        # Default mock response
        mock_response = Mock()
        mock_response.data = [
            {
                'id': '1',
                'library_name': '서울시립 중앙도서관',
                'latitude': 37.5665,
                'longitude': 126.9780,
                'address': '서울시 중구 세종대로 110',
                '_table': 'libraries'
            },
            {
                'id': '2',
                'library_name': '강남도서관',
                'latitude': 37.5170,
                'longitude': 127.0470,
                'address': '서울시 강남구 도곡로 401',
                '_table': 'libraries'
            }
        ]
        client.table.return_value.select.return_value.execute.return_value = mock_response

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


# Workflow Graph Tests

class TestServiceSearchGraph:
    """ServiceSearchGraph 클래스 테스트"""

    def test_graph_initialization(self):
        """그래프 초기화"""
        graph = ServiceSearchGraph(use_llm=False)

        assert graph is not None
        assert graph.use_llm is False
        assert graph.location_analyzer is not None
        assert graph.service_fetcher is not None
        assert graph.response_generator is not None
        assert graph.graph is not None

    def test_graph_initialization_with_llm(self):
        """그래프 초기화 (LLM 사용)"""
        graph = ServiceSearchGraph(use_llm=True)

        assert graph.use_llm is True
        assert graph.response_generator.use_llm is True

    @pytest.mark.asyncio
    async def test_full_workflow_with_coordinates(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """전체 워크플로우: 좌표 → 분석 → 조회 → 응답"""
        # Create query
        query = LocationQuery(
            latitude=37.5665,
            longitude=126.9780,
            radius=2000,
            category='libraries'
        )

        # Execute workflow
        graph = ServiceSearchGraph(use_llm=False)
        final_state = await graph.run(query)

        # Verify workflow completed successfully
        assert final_state is not None
        assert final_state.workflow_id is not None
        assert len(final_state.errors) == 0

        # Verify analyzed location
        assert final_state.analyzed_location is not None
        assert final_state.analyzed_location.latitude == 37.5665
        assert final_state.analyzed_location.longitude == 126.9780
        assert final_state.analyzed_location.source == 'coordinates'

        # Verify search results
        assert final_state.search_results is not None
        assert final_state.search_results.total >= 0
        assert final_state.search_results.category == 'libraries'

        # Verify response
        assert final_state.response is not None
        assert final_state.response.success is True
        assert isinstance(final_state.response.locations, list)
        assert final_state.response.summary is not None

    @pytest.mark.asyncio
    async def test_full_workflow_with_address(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """전체 워크플로우: 주소 → 분석 → 조회 → 응답"""
        # Create query
        query = LocationQuery(
            address='서울시청',
            radius=1000,
            category='cultural_events'
        )

        # Mock cultural events data
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

        # Execute workflow
        graph = ServiceSearchGraph(use_llm=False)
        final_state = await graph.run(query)

        # Verify
        assert final_state is not None
        assert len(final_state.errors) == 0
        assert final_state.analyzed_location is not None
        assert final_state.analyzed_location.source == 'address'
        assert final_state.response.success is True

    @pytest.mark.asyncio
    async def test_workflow_with_custom_workflow_id(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """커스텀 workflow_id 사용"""
        query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000)
        custom_id = 'custom-workflow-12345'

        graph = ServiceSearchGraph(use_llm=False)
        final_state = await graph.run(query, workflow_id=custom_id)

        assert final_state.workflow_id == custom_id

    @pytest.mark.asyncio
    async def test_workflow_generates_uuid_if_not_provided(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """workflow_id 미제공 시 자동 생성"""
        query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000)

        graph = ServiceSearchGraph(use_llm=False)
        final_state = await graph.run(query, workflow_id=None)

        assert final_state.workflow_id is not None
        # Should be a valid UUID
        try:
            uuid.UUID(final_state.workflow_id)
            assert True
        except ValueError:
            assert False, "workflow_id should be a valid UUID"


class TestWorkflowNodeExecution:
    """개별 노드 실행 테스트"""

    @pytest.mark.asyncio
    async def test_analyze_location_node(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """LocationAnalyzer 노드 실행"""
        query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000)
        state = WorkflowState(query=query, workflow_id='test-123')

        graph = ServiceSearchGraph(use_llm=False)
        updated_state = await graph._analyze_location_node(state)

        assert updated_state.analyzed_location is not None
        assert updated_state.analyzed_location.latitude == 37.5665
        assert updated_state.analyzed_location.longitude == 126.9780
        assert len(updated_state.errors) == 0

    @pytest.mark.asyncio
    async def test_fetch_services_node(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """ServiceFetcher 노드 실행"""
        query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000, category='libraries')
        state = WorkflowState(
            query=query,
            workflow_id='test-123',
            analyzed_location=AnalyzedLocation(
                latitude=37.5665,
                longitude=126.9780,
                radius=2000,
                category='libraries',
                source='coordinates'
            )
        )

        graph = ServiceSearchGraph(use_llm=False)
        updated_state = await graph._fetch_services_node(state)

        assert updated_state.search_results is not None
        assert updated_state.search_results.total >= 0
        assert len(updated_state.errors) == 0

    @pytest.mark.asyncio
    async def test_generate_response_node(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """ResponseGenerator 노드 실행"""
        query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000)
        state = WorkflowState(
            query=query,
            workflow_id='test-123',
            analyzed_location=AnalyzedLocation(
                latitude=37.5665,
                longitude=126.9780,
                radius=2000,
                source='coordinates'
            ),
            search_results=SearchResults(
                locations=[
                    {
                        'id': '1',
                        'library_name': '도서관',
                        'latitude': 37.5665,
                        'longitude': 126.9780,
                        'distance': 100.0,
                        '_table': 'libraries'
                    }
                ],
                total=1
            )
        )

        graph = ServiceSearchGraph(use_llm=False)
        updated_state = await graph._generate_response_node(state)

        assert updated_state.response is not None
        assert updated_state.response.success is True
        assert len(updated_state.response.locations) > 0
        assert updated_state.completed_at is not None
        assert len(updated_state.errors) == 0


class TestWorkflowErrorHandling:
    """워크플로우 에러 처리 테스트"""

    @pytest.mark.asyncio
    async def test_analyze_location_error(self, mock_kakao_service):
        """LocationAnalyzer 에러 처리"""
        # Mock geocoding failure
        mock_kakao_service.address_to_coordinates = AsyncMock(return_value=None)
        mock_kakao_service.keyword_search = AsyncMock(return_value=None)

        query = LocationQuery(address='존재하지않는주소')
        state = WorkflowState(query=query, workflow_id='test-error')

        graph = ServiceSearchGraph(use_llm=False)
        updated_state = await graph._analyze_location_node(state)

        # Should handle error gracefully
        assert updated_state.analyzed_location is None
        assert len(updated_state.errors) > 0

    @pytest.mark.asyncio
    async def test_fetch_services_without_analyzed_location(self):
        """ServiceFetcher: analyzed_location 없음 에러"""
        query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000)
        state = WorkflowState(query=query, workflow_id='test-error')
        # analyzed_location is None

        graph = ServiceSearchGraph(use_llm=False)
        updated_state = await graph._fetch_services_node(state)

        # Should handle error gracefully
        assert len(updated_state.errors) > 0
        assert 'No analyzed location' in updated_state.errors[0]

    @pytest.mark.asyncio
    async def test_generate_response_without_search_results(self):
        """ResponseGenerator: search_results 없음 에러"""
        query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000)
        state = WorkflowState(
            query=query,
            workflow_id='test-error',
            analyzed_location=AnalyzedLocation(
                latitude=37.5665,
                longitude=126.9780,
                radius=2000,
                source='coordinates'
            )
            # search_results is None
        )

        graph = ServiceSearchGraph(use_llm=False)
        updated_state = await graph._generate_response_node(state)

        # Should handle error gracefully
        assert len(updated_state.errors) > 0
        assert 'No search results' in updated_state.errors[0]

    @pytest.mark.asyncio
    async def test_workflow_exception_handling(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """워크플로우 예외 처리"""
        # Mock exception in service fetcher
        with patch('app.core.agents.service_fetcher.ServiceFetcher.fetch') as mock_fetch:
            mock_fetch.side_effect = Exception("Database connection failed")

            query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000)
            graph = ServiceSearchGraph(use_llm=False)
            final_state = await graph.run(query)

            # Should handle exception gracefully
            assert len(final_state.errors) > 0


class TestSingletonAndConvenienceFunctions:
    """싱글톤 및 편의 함수 테스트"""

    def test_get_service_graph_singleton(self):
        """get_service_graph 싱글톤 패턴"""
        graph1 = get_service_graph(use_llm=False)
        graph2 = get_service_graph(use_llm=False)

        # Should return same instance
        assert graph1 is graph2

    @pytest.mark.asyncio
    async def test_search_services_convenience_function(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """search_services 편의 함수"""
        # Test with coordinates
        state = await search_services(
            latitude=37.5665,
            longitude=126.9780,
            radius=2000,
            category='libraries',
            use_llm=False
        )

        assert state is not None
        assert state.workflow_id is not None
        assert state.response is not None

    @pytest.mark.asyncio
    async def test_search_services_with_address(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """search_services 편의 함수 (주소)"""
        state = await search_services(
            address='서울시청',
            radius=1000,
            use_llm=False
        )

        assert state is not None
        assert state.analyzed_location.source == 'address'


class TestWorkflowPerformance:
    """워크플로우 성능 테스트"""

    @pytest.mark.asyncio
    async def test_workflow_execution_time(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """워크플로우 실행 시간 측정"""
        import time

        query = LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000)
        graph = ServiceSearchGraph(use_llm=False)

        start_time = time.time()
        final_state = await graph.run(query)
        execution_time = time.time() - start_time

        # Should complete quickly with mocked services
        assert execution_time < 5.0  # 5 seconds max
        assert final_state.search_results.execution_time is not None

    @pytest.mark.asyncio
    async def test_multiple_concurrent_workflows(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """여러 워크플로우 동시 실행"""
        import asyncio

        queries = [
            LocationQuery(latitude=37.5665, longitude=126.9780, radius=2000),
            LocationQuery(latitude=37.5170, longitude=127.0470, radius=1000),
            LocationQuery(address='서울시청', radius=1500),
        ]

        graph = ServiceSearchGraph(use_llm=False)

        # Execute concurrently
        tasks = [graph.run(q) for q in queries]
        results = await asyncio.gather(*tasks)

        # All should complete successfully
        assert len(results) == 3
        for result in results:
            assert result is not None
            assert result.workflow_id is not None


class TestCategorySpecificWorkflows:
    """카테고리별 워크플로우 테스트"""

    @pytest.mark.asyncio
    async def test_libraries_workflow(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """도서관 카테고리 워크플로우"""
        query = LocationQuery(
            latitude=37.5665,
            longitude=126.9780,
            radius=2000,
            category='libraries'
        )

        graph = ServiceSearchGraph(use_llm=False)
        final_state = await graph.run(query)

        assert final_state.search_results.category == 'libraries'

    @pytest.mark.asyncio
    async def test_cultural_events_workflow(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """문화행사 카테고리 워크플로우"""
        # Mock cultural events data
        mock_response = Mock()
        mock_response.data = [
            {
                'id': '1',
                'title': '문화행사',
                'lat': 37.5700,
                'lot': 126.9800,
                '_table': 'cultural_events'
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

        query = LocationQuery(
            latitude=37.5665,
            longitude=126.9780,
            radius=2000,
            category='cultural_events'
        )

        graph = ServiceSearchGraph(use_llm=False)
        final_state = await graph.run(query)

        assert final_state.search_results.category == 'cultural_events'

    @pytest.mark.asyncio
    async def test_all_categories_workflow(
        self,
        mock_kakao_service,
        mock_supabase_client,
        mock_redis_service
    ):
        """전체 카테고리 검색 (category=None)"""
        query = LocationQuery(
            latitude=37.5665,
            longitude=126.9780,
            radius=2000,
            category=None  # All categories
        )

        graph = ServiceSearchGraph(use_llm=False)
        final_state = await graph.run(query)

        assert final_state.search_results.category is None
        # Should aggregate results from all categories
        assert final_state.response.success is True
