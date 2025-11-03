"""
ResponseGenerator Agent
응답 생성 에이전트 - 검색 결과를 사용자 친화적 형태로 변환
"""

import logging
from typing import Optional, List, Dict, Any
import json

from app.core.workflow.state import SearchResults, FormattedResponse, AnalyzedLocation
from app.core.config import settings

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    응답 생성 에이전트

    기능:
    1. SearchResults → FormattedResponse 변환
    2. 카테고리별 그룹화
    3. Kakao Map 마커 데이터 생성
    4. 요약 정보 생성 (개수, 평균 거리 등)
    5. (선택적) Ollama LLM 추천 텍스트 생성
    """

    # 카테고리 한글명 매핑
    CATEGORY_NAMES = {
        'cultural_events': '문화행사',
        'libraries': '도서관',
        'cultural_spaces': '문화공간',
        'future_heritages': '미래유산',
        'public_reservations': '공공시설 예약'
    }

    def __init__(self, use_llm: bool = False):
        """
        ResponseGenerator 초기화

        Args:
            use_llm: Ollama LLM 사용 여부 (기본: False)
        """
        self.use_llm = use_llm

        if self.use_llm:
            try:
                from langchain_ollama import ChatOllama
                self.llm = ChatOllama(
                    base_url=settings.OLLAMA_BASE_URL,
                    model=settings.OLLAMA_LLM_MODEL,
                    temperature=0.7
                )
                logger.info("LLM enabled for response generation")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}. Falling back to template-based generation.")
                self.use_llm = False
        else:
            logger.info("Template-based response generation enabled")

    async def generate(
        self,
        search_results: SearchResults,
        analyzed_location: Optional[AnalyzedLocation] = None
    ) -> FormattedResponse:
        """
        응답 생성

        Args:
            search_results: 검색 결과
            analyzed_location: 분석된 위치 (선택)

        Returns:
            FormattedResponse
        """
        try:
            # 1. 카테고리별 그룹화
            grouped = self._group_by_category(search_results.locations)

            # 2. 요약 정보 생성
            summary = self._generate_summary(search_results, grouped, analyzed_location)

            # 3. Kakao Map 마커 데이터 생성
            markers = self._generate_markers(search_results.locations)

            # 4. 메시지 생성 (템플릿 또는 LLM)
            if self.use_llm and analyzed_location:
                message = await self._generate_llm_message(search_results, analyzed_location, summary)
            else:
                message = self._generate_template_message(search_results, analyzed_location, summary)

            # 5. FormattedResponse 생성
            return FormattedResponse(
                message=message,
                locations=search_results.locations,
                summary={
                    **summary,
                    'grouped_by_category': grouped,
                    'kakao_markers': markers
                },
                success=True
            )

        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return FormattedResponse(
                message="응답 생성 중 오류가 발생했습니다.",
                locations=[],
                success=False,
                error=str(e)
            )

    def _group_by_category(
        self,
        locations: List[Dict[str, Any]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        카테고리별 그룹화

        Args:
            locations: 위치 리스트

        Returns:
            {category: [locations]} 딕셔너리
        """
        grouped = {}

        for location in locations:
            table = location.get('_table')
            if not table:
                continue

            if table not in grouped:
                grouped[table] = []

            grouped[table].append(location)

        return grouped

    def _generate_summary(
        self,
        search_results: SearchResults,
        grouped: Dict[str, List[Dict[str, Any]]],
        analyzed_location: Optional[AnalyzedLocation]
    ) -> Dict[str, Any]:
        """
        요약 정보 생성

        Args:
            search_results: 검색 결과
            grouped: 카테고리별 그룹화된 위치
            analyzed_location: 분석된 위치

        Returns:
            요약 정보 딕셔너리
        """
        summary = {
            'total_count': search_results.total,
            'category_counts': {
                self.CATEGORY_NAMES.get(cat, cat): len(locs)
                for cat, locs in grouped.items()
            },
            'search_center': search_results.search_center,
            'search_radius': search_results.search_radius,
            'search_radius_km': round(search_results.search_radius / 1000, 1) if search_results.search_radius else None,
            'execution_time': search_results.execution_time
        }

        # 평균 거리 계산
        distances = [
            loc.get('distance')
            for loc in search_results.locations
            if loc.get('distance') is not None
        ]

        if distances:
            summary['average_distance'] = round(sum(distances) / len(distances), 2)
            summary['average_distance_km'] = round(summary['average_distance'] / 1000, 2)
            summary['min_distance'] = round(min(distances), 2)
            summary['max_distance'] = round(max(distances), 2)

        # 주소 정보 추가
        if analyzed_location and analyzed_location.address:
            summary['search_address'] = analyzed_location.address

        return summary

    def _generate_markers(
        self,
        locations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Kakao Map 마커 데이터 생성

        Args:
            locations: 위치 리스트

        Returns:
            마커 데이터 리스트
        """
        markers = []

        for idx, location in enumerate(locations):
            # 테이블별 좌표 필드명
            table = location.get('_table')

            if table == 'public_reservations':
                lat = location.get('y_coord')
                lon = location.get('x_coord')
            elif table == 'cultural_events':
                lat = location.get('lat')
                lon = location.get('lot')
            else:
                lat = location.get('latitude')
                lon = location.get('longitude')

            # 좌표 없으면 스킵
            if lat is None or lon is None:
                continue

            # 마커 데이터 생성
            marker = {
                'id': location.get('id') or f"marker_{idx}",
                'lat': lat,
                'lon': lon,
                'title': self._extract_title(location, table),
                'category': self.CATEGORY_NAMES.get(table, table),
                'distance': location.get('distance'),
                'distance_formatted': location.get('distance_formatted'),
                'info': self._extract_info(location, table)
            }

            markers.append(marker)

        return markers

    def _extract_title(self, location: Dict[str, Any], table: str) -> str:
        """
        위치의 제목 추출

        Args:
            location: 위치 정보
            table: 테이블명

        Returns:
            제목 문자열
        """
        if table == 'cultural_events':
            return location.get('title') or location.get('codename', 'Unknown')
        elif table == 'libraries':
            return location.get('library_name') or 'Unknown Library'
        elif table == 'cultural_spaces':
            return location.get('facility_name') or location.get('fclty_nm', 'Unknown Space')
        elif table == 'future_heritages':
            return location.get('name') or location.get('spot_nm', 'Unknown Heritage')
        elif table == 'public_reservations':
            return location.get('service_name') or location.get('svcnm', 'Unknown Service')
        else:
            return location.get('name') or 'Unknown'

    def _extract_info(self, location: Dict[str, Any], table: str) -> Dict[str, Any]:
        """
        위치의 상세 정보 추출

        Args:
            location: 위치 정보
            table: 테이블명

        Returns:
            상세 정보 딕셔너리
        """
        info = {}

        if table == 'cultural_events':
            info = {
                'place': location.get('place'),
                'start_date': location.get('strtdate'),
                'end_date': location.get('end_date'),
                'use_fee': location.get('use_fee'),
                'org_name': location.get('org_name')
            }
        elif table == 'libraries':
            info = {
                'address': location.get('address') or location.get('addr', ''),
                'library_type': location.get('library_type') or location.get('lbrry_se_nm', ''),
                'tel': location.get('tel_no'),
                'homepage': location.get('homepage_url')
            }
        elif table == 'cultural_spaces':
            info = {
                'address': location.get('address') or location.get('rdnmadr', ''),
                'subjcode': location.get('subjcode'),
                'tel': location.get('phone_number')
            }
        elif table == 'future_heritages':
            info = {
                'address': location.get('address') or location.get('addr', ''),
                'category': location.get('main_category'),
                'subcategory': location.get('subcategory')
            }
        elif table == 'public_reservations':
            info = {
                'place': location.get('place_name') or location.get('placenm', ''),
                'area': location.get('area_name') or location.get('areanm', ''),
                'service_status': location.get('service_status') or location.get('svcstatnm', ''),
                'payment_method': location.get('payment_method') or location.get('payatnm', ''),
                'tel': location.get('tel_no')
            }

        # None 값 제거
        info = {k: v for k, v in info.items() if v is not None}

        return info

    def _generate_template_message(
        self,
        search_results: SearchResults,
        analyzed_location: Optional[AnalyzedLocation],
        summary: Dict[str, Any]
    ) -> str:
        """
        템플릿 기반 메시지 생성

        Args:
            search_results: 검색 결과
            analyzed_location: 분석된 위치
            summary: 요약 정보

        Returns:
            메시지 문자열
        """
        if search_results.total == 0:
            if analyzed_location:
                return (
                    f"'{analyzed_location.address or '해당 위치'}' 주변 "
                    f"{summary['search_radius_km']}km 내에서 검색 결과를 찾을 수 없습니다."
                )
            else:
                return "검색 결과를 찾을 수 없습니다."

        # 기본 메시지
        lines = []

        if analyzed_location and analyzed_location.address:
            lines.append(f"📍 {analyzed_location.address} 주변 {summary['search_radius_km']}km 내")
        else:
            lines.append(f"📍 지정하신 위치 주변 {summary['search_radius_km']}km 내")

        lines.append(f"총 **{search_results.total}개**의 장소를 찾았습니다.")
        lines.append("")

        # 카테고리별 개수
        if summary['category_counts']:
            lines.append("**카테고리별 결과:**")
            for category, count in summary['category_counts'].items():
                lines.append(f"- {category}: {count}개")
            lines.append("")

        # 거리 정보
        if 'average_distance_km' in summary:
            lines.append(f"평균 거리: {summary['average_distance_km']}km")

        # 실행 시간
        if search_results.execution_time:
            lines.append(f"검색 시간: {search_results.execution_time:.3f}초")

        return "\n".join(lines)

    async def _generate_llm_message(
        self,
        search_results: SearchResults,
        analyzed_location: AnalyzedLocation,
        summary: Dict[str, Any]
    ) -> str:
        """
        LLM 기반 메시지 생성

        Args:
            search_results: 검색 결과
            analyzed_location: 분석된 위치
            summary: 요약 정보

        Returns:
            LLM이 생성한 메시지 문자열
        """
        if not self.use_llm:
            return self._generate_template_message(search_results, analyzed_location, summary)

        try:
            # 상위 5개 장소 정보
            top_locations = []
            for loc in search_results.locations[:5]:
                table = loc.get('_table')
                title = self._extract_title(loc, table)
                distance = loc.get('distance_formatted', '')
                top_locations.append(f"- {title} ({distance})")

            # 프롬프트 생성
            prompt = f"""당신은 서울시 문화/공공시설 추천 도우미입니다.

사용자가 '{analyzed_location.address or '특정 위치'}' 주변 {summary['search_radius_km']}km 내에서 검색했습니다.

검색 결과:
- 총 {search_results.total}개 장소 발견
- 카테고리별 개수: {', '.join([f'{k} {v}개' for k, v in summary['category_counts'].items()])}
- 평균 거리: {summary.get('average_distance_km', 'N/A')}km

가장 가까운 장소 5곳:
{chr(10).join(top_locations)}

위 정보를 바탕으로 사용자에게 친근하고 유용한 추천 메시지를 작성해주세요.
다음 내용을 포함하세요:
1. 검색 결과 요약
2. 추천 장소 소개 (거리순 상위 3-5개)
3. 방문 팁이나 제안 (선택)

한국어로 3-5문장 정도로 간결하게 작성하세요."""

            # LLM 호출
            response = await self.llm.ainvoke(prompt)
            return response.content.strip()

        except Exception as e:
            logger.error(f"LLM message generation failed: {e}")
            return self._generate_template_message(search_results, analyzed_location, summary)

    async def generate_batch(
        self,
        results_list: List[SearchResults],
        analyzed_location: Optional[AnalyzedLocation] = None
    ) -> List[FormattedResponse]:
        """
        배치 응답 생성

        Args:
            results_list: SearchResults 리스트
            analyzed_location: 분석된 위치

        Returns:
            FormattedResponse 리스트
        """
        responses = []
        for results in results_list:
            response = await self.generate(results, analyzed_location)
            responses.append(response)
        return responses


# Convenience functions

async def generate_response(
    search_results: SearchResults,
    analyzed_location: Optional[AnalyzedLocation] = None,
    use_llm: bool = False
) -> FormattedResponse:
    """
    응답 생성 (편의 함수)

    Args:
        search_results: 검색 결과
        analyzed_location: 분석된 위치
        use_llm: LLM 사용 여부

    Returns:
        FormattedResponse

    Example:
        >>> response = await generate_response(search_results, analyzed_location)
        >>> print(response.message)
    """
    generator = ResponseGenerator(use_llm=use_llm)
    return await generator.generate(search_results, analyzed_location)
