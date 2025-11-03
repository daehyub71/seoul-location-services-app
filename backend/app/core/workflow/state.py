"""
LangGraph Workflow State Definitions
워크플로우 상태 정의
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class AnalyzedLocation(BaseModel):
    """
    분석된 위치 정보

    LocationAnalyzer 에이전트의 출력
    """
    latitude: float = Field(..., description="위도 (WGS84)")
    longitude: float = Field(..., description="경도 (WGS84)")
    address: Optional[str] = Field(None, description="주소 (원본)")
    radius: int = Field(2000, description="검색 반경 (미터)")
    category: Optional[str] = Field(None, description="카테고리 (cultural_events, libraries, etc.)")

    # 메타데이터
    source: str = Field(..., description="입력 소스 (coordinates, address)")
    confidence: float = Field(1.0, description="신뢰도 (0.0 ~ 1.0)")
    timestamp: datetime = Field(default_factory=datetime.now)


class LocationQuery(BaseModel):
    """
    사용자 위치 쿼리

    입력:
    - 좌표 (lat, lon)
    - 주소 (address)
    - 반경 (radius)
    - 카테고리 (category)
    """
    # 좌표 입력
    latitude: Optional[float] = Field(None, description="위도")
    longitude: Optional[float] = Field(None, description="경도")

    # 주소 입력
    address: Optional[str] = Field(None, description="주소 (예: 서울시청, 강남역)")

    # 검색 조건
    radius: int = Field(2000, description="검색 반경 (미터)")
    category: Optional[str] = Field(None, description="카테고리 필터")

    # 우선순위 설정
    category_priority: Optional[List[str]] = Field(
        None,
        description="카테고리 우선순위 (예: ['libraries', 'cultural_spaces'])"
    )


class SearchResults(BaseModel):
    """
    검색 결과

    DataRetriever 에이전트의 출력
    """
    locations: List[Dict[str, Any]] = Field(default_factory=list, description="검색된 위치 리스트")
    total: int = Field(0, description="총 개수")
    category: Optional[str] = Field(None, description="검색된 카테고리")

    # 검색 메타데이터
    search_center: Optional[Dict[str, float]] = Field(None, description="검색 중심 좌표")
    search_radius: Optional[int] = Field(None, description="검색 반경")
    execution_time: Optional[float] = Field(None, description="실행 시간 (초)")


class FormattedResponse(BaseModel):
    """
    최종 응답

    ResponseFormatter 에이전트의 출력
    """
    message: str = Field(..., description="사용자에게 보여질 메시지")
    locations: List[Dict[str, Any]] = Field(default_factory=list, description="위치 리스트")
    summary: Optional[Dict[str, Any]] = Field(None, description="요약 정보")

    # 응답 메타데이터
    success: bool = Field(True, description="성공 여부")
    error: Optional[str] = Field(None, description="에러 메시지")


class WorkflowState(BaseModel):
    """
    전체 워크플로우 상태

    모든 에이전트가 공유하는 상태
    """
    # 입력
    query: LocationQuery

    # 중간 상태
    analyzed_location: Optional[AnalyzedLocation] = None
    search_results: Optional[SearchResults] = None

    # 출력
    response: Optional[FormattedResponse] = None

    # 에러 핸들링
    errors: List[str] = Field(default_factory=list)

    # 메타데이터
    workflow_id: str = Field(..., description="워크플로우 ID")
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class AgentConfig(BaseModel):
    """에이전트 설정"""
    name: str
    enabled: bool = True
    timeout: Optional[int] = None  # seconds
    retry_count: int = 3

    class Config:
        arbitrary_types_allowed = True
