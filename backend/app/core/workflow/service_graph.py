"""
Service Search Workflow Graph
LangGraph 기반 3-에이전트 워크플로우
"""

import logging
from typing import Optional
from langgraph.graph import StateGraph, END
import uuid

from app.core.workflow.state import (
    WorkflowState,
    LocationQuery,
    AnalyzedLocation,
    SearchResults,
    FormattedResponse
)
from app.core.agents.location_analyzer import LocationAnalyzer
from app.core.agents.service_fetcher import ServiceFetcher
from app.core.agents.response_generator import ResponseGenerator

logger = logging.getLogger(__name__)


class ServiceSearchGraph:
    """
    서비스 검색 워크플로우 그래프

    Workflow:
    1. LocationAnalyzer: 위치 분석 (주소 → 좌표, 정규화)
    2. ServiceFetcher: 서비스 조회 (Supabase + Redis 캐싱)
    3. ResponseGenerator: 응답 생성 (Kakao Map 마커 + 메시지)
    """

    def __init__(self, use_llm: bool = False):
        """
        ServiceSearchGraph 초기화

        Args:
            use_llm: ResponseGenerator에서 LLM 사용 여부
        """
        self.use_llm = use_llm

        # 에이전트 초기화
        self.location_analyzer = LocationAnalyzer()
        self.service_fetcher = ServiceFetcher()
        self.response_generator = ResponseGenerator(use_llm=use_llm)

        # 그래프 빌드
        self.graph = self._build_graph()

        logger.info(f"ServiceSearchGraph initialized (use_llm={use_llm})")

    def _build_graph(self) -> StateGraph:
        """
        LangGraph StateGraph 구축

        Returns:
            Compiled StateGraph
        """
        # StateGraph 생성
        workflow = StateGraph(WorkflowState)

        # 노드 추가
        workflow.add_node("analyze_location", self._analyze_location_node)
        workflow.add_node("fetch_services", self._fetch_services_node)
        workflow.add_node("generate_response", self._generate_response_node)

        # 엣지 추가
        workflow.set_entry_point("analyze_location")
        workflow.add_edge("analyze_location", "fetch_services")
        workflow.add_edge("fetch_services", "generate_response")
        workflow.add_edge("generate_response", END)

        # 컴파일
        return workflow.compile()

    async def _analyze_location_node(self, state: WorkflowState) -> WorkflowState:
        """
        LocationAnalyzer 노드

        Args:
            state: 현재 워크플로우 상태

        Returns:
            업데이트된 상태
        """
        try:
            logger.info(f"[analyze_location] Starting for workflow {state.workflow_id}")

            # LocationAnalyzer 실행
            analyzed = await self.location_analyzer.analyze(state.query)

            if analyzed is None:
                error_msg = "Failed to analyze location"
                logger.error(f"[analyze_location] {error_msg}")
                state.errors.append(error_msg)
                return state

            # 상태 업데이트
            state.analyzed_location = analyzed

            logger.info(
                f"[analyze_location] Success: "
                f"({analyzed.latitude}, {analyzed.longitude}), "
                f"radius={analyzed.radius}m, category={analyzed.category}"
            )

            return state

        except Exception as e:
            error_msg = f"LocationAnalyzer error: {e}"
            logger.error(f"[analyze_location] {error_msg}")
            state.errors.append(error_msg)
            return state

    async def _fetch_services_node(self, state: WorkflowState) -> WorkflowState:
        """
        ServiceFetcher 노드

        Args:
            state: 현재 워크플로우 상태

        Returns:
            업데이트된 상태
        """
        try:
            # analyzed_location 체크
            if state.analyzed_location is None:
                error_msg = "No analyzed location available"
                logger.error(f"[fetch_services] {error_msg}")
                state.errors.append(error_msg)
                return state

            logger.info(f"[fetch_services] Starting for workflow {state.workflow_id}")

            # ServiceFetcher 실행
            results = await self.service_fetcher.fetch(
                state.analyzed_location,
                limit=50  # Default limit
            )

            if results is None:
                error_msg = "Failed to fetch services"
                logger.error(f"[fetch_services] {error_msg}")
                state.errors.append(error_msg)
                return state

            # 상태 업데이트
            state.search_results = results

            logger.info(
                f"[fetch_services] Success: "
                f"Found {results.total} locations, "
                f"execution_time={results.execution_time:.3f}s"
            )

            return state

        except Exception as e:
            error_msg = f"ServiceFetcher error: {e}"
            logger.error(f"[fetch_services] {error_msg}")
            state.errors.append(error_msg)
            return state

    async def _generate_response_node(self, state: WorkflowState) -> WorkflowState:
        """
        ResponseGenerator 노드

        Args:
            state: 현재 워크플로우 상태

        Returns:
            업데이트된 상태
        """
        try:
            # search_results 체크
            if state.search_results is None:
                error_msg = "No search results available"
                logger.error(f"[generate_response] {error_msg}")
                state.errors.append(error_msg)
                return state

            logger.info(f"[generate_response] Starting for workflow {state.workflow_id}")

            # ResponseGenerator 실행
            response = await self.response_generator.generate(
                state.search_results,
                state.analyzed_location
            )

            if response is None or not response.success:
                error_msg = "Failed to generate response"
                logger.error(f"[generate_response] {error_msg}")
                state.errors.append(error_msg)
                return state

            # 상태 업데이트
            state.response = response

            # 워크플로우 완료 시간 기록
            from datetime import datetime
            state.completed_at = datetime.now()

            logger.info(
                f"[generate_response] Success: "
                f"Generated response with {len(response.locations)} locations"
            )

            return state

        except Exception as e:
            error_msg = f"ResponseGenerator error: {e}"
            logger.error(f"[generate_response] {error_msg}")
            state.errors.append(error_msg)
            return state

    async def run(
        self,
        query: LocationQuery,
        workflow_id: Optional[str] = None
    ) -> WorkflowState:
        """
        워크플로우 실행

        Args:
            query: 사용자 위치 쿼리
            workflow_id: 워크플로우 ID (선택, 없으면 자동 생성)

        Returns:
            최종 WorkflowState
        """
        # 워크플로우 ID 생성
        if workflow_id is None:
            workflow_id = str(uuid.uuid4())

        # 초기 상태 생성
        initial_state = WorkflowState(
            query=query,
            workflow_id=workflow_id
        )

        logger.info(f"Starting workflow {workflow_id}")

        try:
            # 그래프 실행
            result = await self.graph.ainvoke(initial_state)

            # LangGraph ainvoke는 dict를 반환하므로 WorkflowState로 변환
            if isinstance(result, dict):
                try:
                    # dict를 WorkflowState로 변환
                    # nested Pydantic models도 자동으로 변환됨
                    final_state = WorkflowState.model_validate(result)
                except Exception as e:
                    logger.error(f"Failed to convert result dict to WorkflowState: {e}")
                    # 변환 실패 시 초기 상태에 에러 추가하고 반환
                    initial_state.errors.append(f"State conversion error: {e}")
                    return initial_state
            else:
                final_state = result

            # 에러 체크
            if final_state.errors:
                logger.warning(
                    f"Workflow {workflow_id} completed with errors: "
                    f"{', '.join(final_state.errors)}"
                )
            else:
                logger.info(f"Workflow {workflow_id} completed successfully")

            return final_state

        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {e}")
            initial_state.errors.append(f"Workflow execution error: {e}")
            return initial_state


# Singleton instance
_graph_instance: Optional[ServiceSearchGraph] = None


def get_service_graph(use_llm: bool = False) -> ServiceSearchGraph:
    """
    ServiceSearchGraph 싱글톤 인스턴스

    Args:
        use_llm: ResponseGenerator에서 LLM 사용 여부

    Returns:
        ServiceSearchGraph 인스턴스
    """
    global _graph_instance

    if _graph_instance is None:
        _graph_instance = ServiceSearchGraph(use_llm=use_llm)

    return _graph_instance


# Convenience function
async def search_services(
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    address: Optional[str] = None,
    radius: int = 2000,
    category: Optional[str] = None,
    use_llm: bool = False
) -> WorkflowState:
    """
    서비스 검색 (편의 함수)

    Args:
        latitude: 위도
        longitude: 경도
        address: 주소
        radius: 반경 (미터)
        category: 카테고리
        use_llm: LLM 사용 여부

    Returns:
        최종 WorkflowState

    Example:
        >>> state = await search_services(
        ...     latitude=37.5665,
        ...     longitude=126.9780,
        ...     radius=2000,
        ...     category='libraries'
        ... )
        >>> print(state.response.message)
    """
    # LocationQuery 생성
    query = LocationQuery(
        latitude=latitude,
        longitude=longitude,
        address=address,
        radius=radius,
        category=category
    )

    # 그래프 실행
    graph = get_service_graph(use_llm=use_llm)
    return await graph.run(query)
