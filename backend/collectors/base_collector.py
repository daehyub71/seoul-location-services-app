"""
Base Collector 추상 클래스
모든 데이터 수집기의 공통 로직 정의
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from supabase import create_client, Client
import os
from dotenv import load_dotenv

from collectors.seoul_api_client import SeoulAPIClient
from app.utils.coordinate_transform import CoordinateTransformer

load_dotenv()

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """
    데이터 수집기 베이스 클래스

    Features:
    - Supabase 연결 관리
    - Seoul API Client 통합
    - 좌표 변환 지원
    - 공통 로깅 로직
    - 데이터 검증
    - 수집 로그 기록
    """

    def __init__(self):
        """초기화"""
        # Supabase 연결
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)

        # Seoul API 설정
        self.seoul_api_key = os.getenv('SEOUL_API_KEY')
        if not self.seoul_api_key:
            raise ValueError("SEOUL_API_KEY must be set in .env")

        # 좌표 변환기
        self.transformer = CoordinateTransformer()

        # 수집 통계
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

        logger.info(f"{self.__class__.__name__} initialized")

    @property
    @abstractmethod
    def table_name(self) -> str:
        """
        Supabase 테이블명 (하위 클래스에서 구현)

        Returns:
            테이블명 (예: 'cultural_events')
        """
        pass

    @property
    @abstractmethod
    def endpoint_key(self) -> str:
        """
        Seoul API 엔드포인트 키 (하위 클래스에서 구현)

        Returns:
            엔드포인트 키 (예: 'cultural_events')
        """
        pass

    @abstractmethod
    def transform_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        API 응답 레코드를 Supabase 스키마에 맞게 변환 (하위 클래스에서 구현)

        Args:
            record: Seoul API 응답 레코드

        Returns:
            변환된 레코드 또는 None (스킵할 경우)
        """
        pass

    def validate_record(self, record: Dict[str, Any]) -> bool:
        """
        레코드 유효성 검증

        Args:
            record: 변환된 레코드

        Returns:
            유효 여부
        """
        # 필수 필드 확인
        required_fields = ['api_id']

        for field in required_fields:
            if field not in record or record[field] is None:
                logger.warning(f"Missing required field: {field}")
                return False

        return True

    def transform_coordinates(
        self,
        lat: Optional[float],
        lon: Optional[float],
        swap: bool = False
    ) -> tuple[Optional[float], Optional[float]]:
        """
        좌표 변환 및 검증

        Args:
            lat: 위도
            lon: 경도
            swap: True이면 lat/lon 위치 바꿈 (reservation API 이슈)

        Returns:
            (위도, 경도) 튜플 또는 (None, None)
        """
        if lat is None or lon is None:
            return None, None

        try:
            # 문자열을 float로 변환
            lat = float(lat)
            lon = float(lon)

            # reservation API 좌표 반전 수정
            if swap:
                lat, lon = lon, lat

            # 좌표 유효성 검증
            if not self.transformer.validate_wgs84(lat, lon):
                logger.warning(f"Invalid coordinates: lat={lat}, lon={lon}")
                return None, None

            return lat, lon

        except (ValueError, TypeError) as e:
            logger.warning(f"Coordinate conversion error: {e}")
            return None, None

    def parse_date(self, date_str: Optional[str], target_type: str = 'date') -> Optional[str]:
        """
        여러 형식의 날짜 문자열 파싱 (유연한 포맷 지원)

        Args:
            date_str: 날짜 문자열 (예: '2025-10-20', '20251020', '2025-10-20 10:00:00.0')
            target_type: 'date' (DATE), 'timestamp' (TIMESTAMPTZ), 'year' (INTEGER)

        Returns:
            파싱된 날짜 문자열 또는 None
        """
        if not date_str:
            return None

        try:
            # 공백 제거
            date_str = str(date_str).strip()

            # 빈 문자열 체크
            if not date_str:
                return None

            # Datetime 형식인 경우 날짜 부분만 추출 (YYYY-MM-DD HH:MM:SS.0 → YYYY-MM-DD)
            if ' ' in date_str:
                date_str = date_str.split()[0]

            # 여러 포맷 시도
            formats = [
                '%Y-%m-%d',      # 2025-10-20 (가장 흔한 형식)
                '%Y%m%d',        # 20251020
                '%Y',            # 2025 (year only)
            ]

            for fmt in formats:
                try:
                    dt = datetime.strptime(date_str, fmt)

                    # 타입에 따라 반환
                    if target_type == 'year':
                        return dt.year  # INTEGER
                    elif target_type == 'timestamp':
                        return dt.isoformat()  # TIMESTAMPTZ
                    else:  # 'date'
                        return dt.date().isoformat()  # DATE (YYYY-MM-DD)

                except ValueError:
                    continue

            # 모든 포맷 실패
            logger.warning(f"Date parsing failed for all formats: {date_str}")
            return None

        except (AttributeError, TypeError) as e:
            logger.warning(f"Date parsing error: {date_str} - {e}")
            return None

    def normalize_string(self, value: Optional[str]) -> Optional[str]:
        """
        문자열 정규화 (공백 제거, None 처리)

        Args:
            value: 입력 문자열

        Returns:
            정규화된 문자열 또는 None
        """
        if value is None:
            return None

        value = str(value).strip()

        if not value or value == '':
            return None

        return value

    async def collect(self, max_records: Optional[int] = None) -> Dict[str, Any]:
        """
        데이터 수집 및 저장 (메인 메서드)

        Args:
            max_records: 최대 수집 레코드 수 (None이면 전체)

        Returns:
            수집 통계 딕셔너리
        """
        logger.info(f"Starting collection for {self.table_name}")
        start_time = datetime.now()

        # 통계 초기화
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'errors': []
        }

        try:
            async with SeoulAPIClient(self.seoul_api_key) as client:
                # 엔드포인트명 조회
                endpoint_name = client.get_endpoint_name(self.endpoint_key)

                if not endpoint_name:
                    raise ValueError(f"Unknown endpoint key: {self.endpoint_key}")

                # 총 레코드 수 확인
                total_count = await client.get_total_count(endpoint_name)
                logger.info(f"Total records available: {total_count:,}")

                # 데이터 수집
                raw_records = await client.fetch_all(endpoint_name, max_records=max_records)
                self.stats['total'] = len(raw_records)

                logger.info(f"Fetched {len(raw_records):,} records from API")

                # 레코드 변환 및 저장
                for i, raw_record in enumerate(raw_records, 1):
                    try:
                        # 변환
                        transformed = self.transform_record(raw_record)

                        if transformed is None:
                            self.stats['skipped'] += 1
                            continue

                        # 검증
                        if not self.validate_record(transformed):
                            self.stats['skipped'] += 1
                            continue

                        # Supabase 저장 (UPSERT)
                        self.supabase.table(self.table_name).upsert(
                            transformed,
                            on_conflict='api_id'
                        ).execute()

                        self.stats['success'] += 1

                        # 진행상황 로깅 (100개마다)
                        if i % 100 == 0:
                            logger.info(f"Progress: {i}/{len(raw_records)} ({i/len(raw_records)*100:.1f}%)")

                    except Exception as e:
                        self.stats['failed'] += 1
                        error_msg = f"Record {i} failed: {str(e)}"
                        logger.error(error_msg)
                        self.stats['errors'].append(error_msg)

                # 수집 로그 기록
                await self._log_collection(start_time, success=True)

        except Exception as e:
            logger.error(f"Collection failed: {e}")
            self.stats['errors'].append(str(e))
            await self._log_collection(start_time, success=False, error=str(e))
            raise

        # 최종 통계 출력
        duration = (datetime.now() - start_time).total_seconds()
        logger.info(f"""
Collection completed for {self.table_name}:
  Total:   {self.stats['total']:,}
  Success: {self.stats['success']:,}
  Failed:  {self.stats['failed']:,}
  Skipped: {self.stats['skipped']:,}
  Duration: {duration:.2f}s
        """)

        return self.stats

    async def _log_collection(
        self,
        start_time: datetime,
        success: bool,
        error: Optional[str] = None
    ):
        """
        수집 로그를 collection_logs 테이블에 기록

        Args:
            start_time: 수집 시작 시간
            success: 성공 여부
            error: 에러 메시지 (실패 시)
        """
        try:
            log_entry = {
                'table_name': self.table_name,
                'records_collected': self.stats['success'],
                'records_failed': self.stats['failed'],
                'records_skipped': self.stats['skipped'],
                'success': success,
                'error_message': error,
                'started_at': start_time.isoformat(),
                'completed_at': datetime.now().isoformat()
            }

            self.supabase.table('collection_logs').insert(log_entry).execute()
            logger.info("Collection log saved")

        except Exception as e:
            logger.error(f"Failed to save collection log: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """
        수집 통계 반환

        Returns:
            통계 딕셔너리
        """
        return self.stats.copy()
