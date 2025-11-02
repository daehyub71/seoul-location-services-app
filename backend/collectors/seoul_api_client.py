"""
Seoul Open API Client
서울 열린데이터광장 API 통신 모듈
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import httpx
import xmltodict
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = logging.getLogger(__name__)


class SeoulAPIError(Exception):
    """Seoul API 관련 에러"""
    pass


class SeoulAPIClient:
    """
    Seoul Open API 비동기 클라이언트

    Features:
    - httpx 기반 비동기 HTTP 통신
    - 자동 Retry (3회, exponential backoff)
    - XML → JSON 자동 파싱
    - 페이지네이션 자동 처리
    - 에러 핸들링
    """

    BASE_URL = "http://openapi.seoul.go.kr:8088"
    DEFAULT_TIMEOUT = 30.0  # seconds
    MAX_RETRIES = 3
    PAGE_SIZE = 1000  # 서울시 API 최대 페이지 크기

    # 서울시 API 엔드포인트 목록
    ENDPOINTS = {
        'cultural_events': 'culturalEventInfo',
        'public_libraries': 'SeoulPublicLibraryInfo',
        'cultural_spaces': 'culturalSpaceInfo',
        'disabled_libraries': 'SeoulDisableLibraryInfo',
        'reservation_medical': 'ListPublicReservationMedical',
        'reservation_education': 'ListPublicReservationEducation',
        'reservation_culture': 'ListPublicReservationCulture',
        'reservation_all': 'tvYeyakCOllect',
        'future_heritage': 'futureHeritageInfo'
    }

    def __init__(self, api_key: str, timeout: float = DEFAULT_TIMEOUT):
        """
        Args:
            api_key: Seoul Open API 인증키
            timeout: HTTP 요청 타임아웃 (초)
        """
        self.api_key = api_key
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            follow_redirects=True,
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.client:
            await self.client.aclose()

    def _build_url(
        self,
        endpoint: str,
        start_index: int = 1,
        end_index: int = 1000,
        format: str = "json"
    ) -> str:
        """
        API URL 생성

        Format:
        http://openapi.seoul.go.kr:8088/{API_KEY}/{FORMAT}/{SERVICE_NAME}/{START_INDEX}/{END_INDEX}/

        Args:
            endpoint: API 엔드포인트명
            start_index: 시작 인덱스 (1부터 시작)
            end_index: 종료 인덱스
            format: 응답 포맷 (json 또는 xml)

        Returns:
            완전한 API URL
        """
        return f"{self.BASE_URL}/{self.api_key}/{format}/{endpoint}/{start_index}/{end_index}/"

    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True
    )
    async def _fetch(self, url: str) -> Dict[str, Any]:
        """
        HTTP GET 요청 (자동 Retry)

        Args:
            url: 요청 URL

        Returns:
            JSON 응답 데이터

        Raises:
            SeoulAPIError: API 에러 발생 시
            httpx.TimeoutException: 타임아웃 시
            httpx.NetworkError: 네트워크 에러 시
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with' statement.")

        try:
            logger.debug(f"Fetching: {url}")
            response = await self.client.get(url)

            # HTTP 상태 코드 확인
            if response.status_code == 429:
                logger.warning("Rate limit exceeded (429)")
                raise SeoulAPIError("API rate limit exceeded")
            elif response.status_code == 500:
                logger.error("Server error (500)")
                raise SeoulAPIError("API server error")
            elif response.status_code == 503:
                logger.error("Service unavailable (503)")
                raise SeoulAPIError("API service unavailable")

            response.raise_for_status()

            # JSON 응답 파싱
            data = response.json()

            # Seoul API 에러 코드 확인
            # 일부 API는 에러를 RESULT 필드에 포함
            if isinstance(data, dict):
                for key in data.keys():
                    if isinstance(data[key], dict) and 'RESULT' in data[key]:
                        result = data[key]['RESULT']
                        code = result.get('CODE')
                        message = result.get('MESSAGE', '')

                        # INFO-000: 정상
                        if code and code != 'INFO-000':
                            logger.error(f"API Error: {code} - {message}")
                            raise SeoulAPIError(f"{code}: {message}")

            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code}")
            raise SeoulAPIError(f"HTTP {e.response.status_code}: {e}")
        except httpx.TimeoutException:
            logger.warning("Request timeout")
            raise
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise SeoulAPIError(f"Unexpected error: {e}")

    async def fetch_page(
        self,
        endpoint: str,
        start_index: int = 1,
        end_index: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        단일 페이지 조회

        Args:
            endpoint: API 엔드포인트명
            start_index: 시작 인덱스
            end_index: 종료 인덱스 (None이면 start_index + PAGE_SIZE - 1)

        Returns:
            API 응답 데이터
        """
        if end_index is None:
            end_index = start_index + self.PAGE_SIZE - 1

        url = self._build_url(endpoint, start_index, end_index)
        data = await self._fetch(url)

        logger.info(f"Fetched {endpoint}: {start_index}-{end_index}")

        return data

    async def fetch_all(
        self,
        endpoint: str,
        max_records: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        모든 데이터 조회 (페이지네이션 자동 처리)

        Args:
            endpoint: API 엔드포인트명
            max_records: 최대 조회 레코드 수 (None이면 전체)

        Returns:
            전체 레코드 리스트
        """
        all_records = []
        start_index = 1

        while True:
            # 최대 레코드 수 체크
            if max_records and len(all_records) >= max_records:
                logger.info(f"Reached max_records limit: {max_records}")
                break

            try:
                data = await self.fetch_page(endpoint, start_index)

                # 응답에서 레코드 추출
                records = self._extract_records(data, endpoint)

                if not records:
                    logger.info(f"No more records for {endpoint}")
                    break

                all_records.extend(records)
                logger.info(f"Total records collected: {len(all_records)}")

                # 다음 페이지 계산
                start_index += len(records)

                # 마지막 페이지 확인 (레코드가 PAGE_SIZE보다 적으면 종료)
                if len(records) < self.PAGE_SIZE:
                    logger.info(f"Last page reached for {endpoint}")
                    break

                # Rate limiting 방지를 위한 짧은 대기
                await asyncio.sleep(0.5)

            except SeoulAPIError as e:
                logger.error(f"Error fetching {endpoint}: {e}")
                # 에러 발생 시 현재까지 수집한 데이터 반환
                break

        logger.info(f"Completed fetching {endpoint}: {len(all_records)} records")
        return all_records

    def _extract_records(self, data: Dict[str, Any], endpoint: str) -> List[Dict[str, Any]]:
        """
        API 응답에서 실제 레코드 추출

        Seoul API 응답 구조:
        {
            "SERVICE_NAME": {
                "list_total_count": 100,
                "RESULT": {"CODE": "INFO-000", "MESSAGE": "정상"},
                "row": [...]
            }
        }

        Args:
            data: API 응답 데이터
            endpoint: 엔드포인트명

        Returns:
            레코드 리스트
        """
        if not isinstance(data, dict):
            return []

        # 응답 키 찾기 (대소문자 구분 없이)
        service_key = None
        for key in data.keys():
            if key.lower() == endpoint.lower() or endpoint.lower() in key.lower():
                service_key = key
                break

        if not service_key:
            logger.warning(f"Service key not found for {endpoint}")
            logger.debug(f"Available keys: {list(data.keys())}")
            # 첫 번째 키 사용 (fallback)
            service_key = list(data.keys())[0] if data else None

        if not service_key:
            return []

        service_data = data[service_key]

        if not isinstance(service_data, dict):
            return []

        # row 필드에서 레코드 추출
        records = service_data.get('row', [])

        # row가 단일 dict인 경우 리스트로 변환
        if isinstance(records, dict):
            records = [records]

        return records if isinstance(records, list) else []

    async def get_total_count(self, endpoint: str) -> int:
        """
        총 레코드 수 조회

        Args:
            endpoint: API 엔드포인트명

        Returns:
            총 레코드 수
        """
        try:
            # 첫 페이지만 조회하여 total count 확인
            data = await self.fetch_page(endpoint, 1, 5)

            # 서비스 키 찾기
            for key in data.keys():
                if isinstance(data[key], dict) and 'list_total_count' in data[key]:
                    total = data[key]['list_total_count']
                    logger.info(f"Total count for {endpoint}: {total}")
                    return int(total)

            logger.warning(f"Could not find total count for {endpoint}")
            return 0

        except Exception as e:
            logger.error(f"Error getting total count: {e}")
            return 0

    @classmethod
    def get_endpoint_name(cls, key: str) -> Optional[str]:
        """
        엔드포인트 키로 실제 API 엔드포인트명 조회

        Args:
            key: 엔드포인트 키 (예: 'cultural_events')

        Returns:
            API 엔드포인트명 (예: 'culturalEventInfo')
        """
        return cls.ENDPOINTS.get(key)

    @classmethod
    def list_endpoints(cls) -> Dict[str, str]:
        """
        사용 가능한 모든 엔드포인트 목록

        Returns:
            {key: endpoint_name} 딕셔너리
        """
        return cls.ENDPOINTS.copy()


async def main():
    """테스트용 메인 함수"""
    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv('SEOUL_API_KEY')

    if not api_key:
        print("❌ SEOUL_API_KEY not found in .env")
        return

    async with SeoulAPIClient(api_key) as client:
        # 엔드포인트 목록 출력
        print("\n사용 가능한 엔드포인트:")
        for key, endpoint in client.list_endpoints().items():
            print(f"  - {key}: {endpoint}")

        # 문화행사 정보 조회 테스트
        print("\n문화행사 정보 조회 중...")
        endpoint = client.get_endpoint_name('cultural_events')

        if endpoint:
            # 총 개수 확인
            total = await client.get_total_count(endpoint)
            print(f"총 레코드 수: {total}")

            # 첫 10개만 조회
            records = await client.fetch_all(endpoint, max_records=10)
            print(f"\n조회된 레코드 수: {len(records)}")

            if records:
                print("\n첫 번째 레코드:")
                import json
                print(json.dumps(records[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    asyncio.run(main())
