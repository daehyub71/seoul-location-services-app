"""
Service API Endpoints
서비스 검색 API 엔드포인트
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.api.v1.schemas.service_schemas import (
    ServiceSearchResponse,
    CategoryListResponse,
    ErrorResponse,
    SearchSummary,
    CATEGORY_METADATA
)
from app.core.workflow.service_graph import get_service_graph
from app.core.workflow.state import LocationQuery

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/services", tags=["services"])


@router.get(
    "/nearby",
    response_model=ServiceSearchResponse,
    summary="근처 서비스 검색",
    description="좌표 또는 주소 기반으로 주변 서비스를 검색합니다."
)
async def search_nearby(
    lat: Optional[float] = Query(None, description="위도 (WGS84)"),
    lon: Optional[float] = Query(None, description="경도 (WGS84)"),
    address: Optional[str] = Query(None, description="주소 (예: 서울시청, 강남역)"),
    radius: int = Query(2000, ge=100, le=10000, description="검색 반경 (미터)"),
    category: Optional[str] = Query(None, description="카테고리 필터"),
    limit: int = Query(50, ge=1, le=200, description="최대 결과 개수"),
    use_llm: bool = Query(False, description="LLM 기반 응답 생성 사용")
):
    """
    근처 서비스 검색

    **입력 방식 (둘 중 하나 필수)**:
    - 좌표: lat + lon
    - 주소: address (Kakao Map Geocoding 사용)

    **카테고리**:
    - cultural_events: 문화행사
    - libraries: 도서관
    - cultural_spaces: 문화공간
    - future_heritages: 미래유산
    - public_reservations: 공공시설 예약

    **응답**:
    - locations: 검색된 위치 리스트 (거리순 정렬)
    - summary: 요약 정보 (총 개수, 평균 거리, Kakao Map 마커 등)
    - workflow_id: 워크플로우 추적 ID
    """
    try:
        # 입력 검증
        if lat is None and lon is None and address is None:
            raise HTTPException(
                status_code=400,
                detail="Either coordinates (lat/lon) or address is required"
            )

        if (lat is not None and lon is None) or (lat is None and lon is not None):
            raise HTTPException(
                status_code=400,
                detail="Both latitude and longitude must be provided together"
            )

        # 카테고리 검증
        if category is not None:
            allowed_categories = list(CATEGORY_METADATA.keys())
            if category not in allowed_categories:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category. Must be one of {allowed_categories}"
                )

        logger.info(
            f"[nearby] Request: lat={lat}, lon={lon}, address={address}, "
            f"radius={radius}, category={category}, limit={limit}"
        )

        # LocationQuery 생성
        query = LocationQuery(
            latitude=lat,
            longitude=lon,
            address=address,
            radius=radius,
            category=category
        )

        # 워크플로우 실행
        graph = get_service_graph(use_llm=use_llm)
        state = await graph.run(query)

        # 에러 체크
        if state.errors:
            logger.error(f"[nearby] Workflow errors: {', '.join(state.errors)}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Workflow execution failed",
                    details="; ".join(state.errors)
                ).model_dump()
            )

        # 응답 없음
        if state.response is None:
            logger.warning("[nearby] No response generated")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="No response generated"
                ).model_dump()
            )

        # 결과 제한 적용
        final_locations = state.response.locations[:limit]

        # SearchSummary 생성
        summary = SearchSummary(
            total_count=len(final_locations),
            category_counts=state.response.summary.get('category_counts', {}),
            search_center=state.response.summary.get('search_center'),
            search_radius=state.response.summary.get('search_radius'),
            search_radius_km=state.response.summary.get('search_radius_km'),
            search_address=state.response.summary.get('search_address'),
            average_distance=state.response.summary.get('average_distance'),
            average_distance_km=state.response.summary.get('average_distance_km'),
            min_distance=state.response.summary.get('min_distance'),
            max_distance=state.response.summary.get('max_distance'),
            execution_time=state.response.summary.get('execution_time'),
            grouped_by_category=state.response.summary.get('grouped_by_category'),
            kakao_markers=state.response.summary.get('kakao_markers', [])
        )

        # 응답 생성
        response = ServiceSearchResponse(
            success=state.response.success,
            message=state.response.message,
            locations=final_locations,
            summary=summary,
            workflow_id=state.workflow_id,
            errors=state.errors
        )

        logger.info(
            f"[nearby] Success: workflow_id={state.workflow_id}, "
            f"found {len(final_locations)} locations"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[nearby] Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/{category}",
    response_model=ServiceSearchResponse,
    summary="카테고리별 서비스 검색",
    description="특정 카테고리의 서비스만 검색합니다."
)
async def search_by_category(
    category: str,
    lat: float = Query(..., description="위도 (WGS84)"),
    lon: float = Query(..., description="경도 (WGS84)"),
    radius: int = Query(2000, ge=100, le=10000, description="검색 반경 (미터)"),
    limit: int = Query(50, ge=1, le=200, description="최대 결과 개수"),
    sort_by: str = Query("distance", description="정렬 기준 (distance, name)"),
    use_llm: bool = Query(False, description="LLM 기반 응답 생성 사용")
):
    """
    카테고리별 서비스 검색

    **카테고리**:
    - cultural_events: 문화행사
    - libraries: 도서관
    - cultural_spaces: 문화공간
    - future_heritages: 미래유산
    - public_reservations: 공공시설 예약

    **정렬**:
    - distance: 거리순 (기본)
    - name: 이름순
    """
    try:
        # 카테고리 검증
        if category not in CATEGORY_METADATA:
            raise HTTPException(
                status_code=404,
                detail=f"Invalid category: {category}. Must be one of {list(CATEGORY_METADATA.keys())}"
            )

        # 정렬 기준 검증
        if sort_by not in ['distance', 'name']:
            raise HTTPException(
                status_code=400,
                detail="Invalid sort_by. Must be 'distance' or 'name'"
            )

        logger.info(
            f"[category] Request: category={category}, lat={lat}, lon={lon}, "
            f"radius={radius}, limit={limit}, sort_by={sort_by}"
        )

        # LocationQuery 생성
        query = LocationQuery(
            latitude=lat,
            longitude=lon,
            radius=radius,
            category=category
        )

        # 워크플로우 실행
        graph = get_service_graph(use_llm=use_llm)
        state = await graph.run(query)

        # 에러 체크
        if state.errors or state.response is None:
            error_msg = "; ".join(state.errors) if state.errors else "No response generated"
            logger.error(f"[category] Workflow failed: {error_msg}")
            return JSONResponse(
                status_code=500,
                content=ErrorResponse(
                    error="Workflow execution failed",
                    details=error_msg
                ).model_dump()
            )

        # 정렬 적용
        sorted_locations = state.response.locations

        if sort_by == "name":
            # 이름순 정렬 (테이블별 필드명 처리)
            def get_name(loc):
                if loc.get('_table') == 'libraries':
                    return loc.get('library_name', '')
                elif loc.get('_table') == 'cultural_events':
                    return loc.get('title', '')
                elif loc.get('_table') == 'cultural_spaces':
                    return loc.get('facility_name', '')
                elif loc.get('_table') == 'future_heritages':
                    return loc.get('name', '')
                elif loc.get('_table') == 'public_reservations':
                    return loc.get('service_name', '')
                return ''

            sorted_locations = sorted(sorted_locations, key=get_name)

        # 결과 제한 적용
        final_locations = sorted_locations[:limit]

        # SearchSummary 생성
        summary = SearchSummary(
            total_count=len(final_locations),
            category_counts={CATEGORY_METADATA[category]['name']: len(final_locations)},
            search_center={'latitude': lat, 'longitude': lon},
            search_radius=radius,
            search_radius_km=round(radius / 1000, 1),
            execution_time=state.response.summary.get('execution_time'),
            kakao_markers=state.response.summary.get('kakao_markers', [])[:limit]
        )

        # 응답 생성
        response = ServiceSearchResponse(
            success=True,
            message=f"{CATEGORY_METADATA[category]['name']} {len(final_locations)}개를 찾았습니다.",
            locations=final_locations,
            summary=summary,
            workflow_id=state.workflow_id
        )

        logger.info(
            f"[category] Success: workflow_id={state.workflow_id}, "
            f"category={category}, found {len(final_locations)} locations"
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[category] Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                details=str(e)
            ).model_dump()
        )


@router.get(
    "/categories/list",
    response_model=CategoryListResponse,
    summary="카테고리 목록 조회",
    description="사용 가능한 모든 카테고리 목록을 반환합니다."
)
async def list_categories():
    """
    카테고리 목록 조회

    **응답**:
    - 모든 카테고리의 ID, 이름, 설명, 아이콘
    """
    categories = [
        {
            'id': cat_id,
            **metadata
        }
        for cat_id, metadata in CATEGORY_METADATA.items()
    ]

    return CategoryListResponse(categories=categories)


@router.get(
    "/{category}/{item_id}",
    summary="서비스 상세 정보 조회",
    description="특정 서비스의 상세 정보와 주변 추천 서비스를 반환합니다."
)
async def get_service_detail(
    category: str,
    item_id: str,
    nearby_radius: int = Query(500, ge=100, le=2000, description="주변 서비스 검색 반경 (미터)")
):
    """
    서비스 상세 정보 조회

    **카테고리**:
    - cultural_events, libraries, cultural_spaces, future_heritages, public_reservations

    **응답**:
    - 서비스 상세 정보
    - 주변 추천 서비스 (반경 500m 기본)
    """
    try:
        # 카테고리 검증
        if category not in CATEGORY_METADATA:
            raise HTTPException(
                status_code=404,
                detail=f"Invalid category: {category}"
            )

        logger.info(f"[detail] Request: category={category}, id={item_id}, nearby_radius={nearby_radius}")

        # Supabase에서 상세 정보 조회
        from app.db.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        # 테이블명 매핑
        table_map = {
            'cultural_events': 'cultural_events',
            'libraries': 'libraries',
            'cultural_spaces': 'cultural_spaces',
            'future_heritages': 'future_heritages',
            'public_reservations': 'public_reservations'
        }

        table_name = table_map[category]

        # 아이템 조회
        response = supabase.table(table_name).select('*').eq('id', item_id).execute()

        if not response.data or len(response.data) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Service not found: {category}/{item_id}"
            )

        item = response.data[0]

        # 좌표 추출
        if category == 'public_reservations':
            lat = item.get('y_coord')
            lon = item.get('x_coord')
        elif category == 'cultural_events':
            lat = item.get('lat')
            lon = item.get('lot')
        else:
            lat = item.get('latitude')
            lon = item.get('longitude')

        # 주변 서비스 조회 (좌표가 있을 경우)
        nearby_services = []
        if lat is not None and lon is not None:
            # 같은 카테고리 내에서 주변 검색
            query = LocationQuery(
                latitude=lat,
                longitude=lon,
                radius=nearby_radius,
                category=category
            )

            graph = get_service_graph(use_llm=False)
            state = await graph.run(query)

            if state.response and state.response.locations:
                # 현재 아이템 제외
                nearby_services = [
                    loc for loc in state.response.locations
                    if loc.get('id') != item_id
                ][:5]  # 최대 5개

        # 응답 생성
        result = {
            "success": True,
            "category": category,
            "category_name": CATEGORY_METADATA[category]['name'],
            "item": item,
            "nearby_services": nearby_services,
            "nearby_count": len(nearby_services)
        }

        logger.info(
            f"[detail] Success: category={category}, id={item_id}, "
            f"nearby_count={len(nearby_services)}"
        )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[detail] Unexpected error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                details=str(e)
            ).model_dump()
        )
