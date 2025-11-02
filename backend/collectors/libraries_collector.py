"""
Libraries Collector
도서관 정보 수집기 (공공도서관 + 장애인도서관 통합)
"""

import logging
from typing import Dict, Optional, Any
import hashlib

from collectors.base_collector import BaseCollector
from collectors.seoul_api_client import SeoulAPIClient

logger = logging.getLogger(__name__)


class LibrariesCollector(BaseCollector):
    """
    도서관 정보 수집기

    API:
    - /SeoulPublicLibraryInfo (공공도서관)
    - /SeoulDisableLibraryInfo (장애인도서관)

    테이블: libraries
    """

    @property
    def table_name(self) -> str:
        return 'libraries'

    @property
    def endpoint_key(self) -> str:
        # 공공도서관을 메인으로 사용
        return 'public_libraries'

    def transform_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        API 응답 레코드를 libraries 스키마에 맞게 변환

        공공도서관 API 필드:
        - LBRRY_NAME: 도서관명
        - ADRES: 주소
        - TEL: 전화번호
        - FDRM_CLOSE_DATE: 정기휴관일
        - OP_TIME: 운영시간
        - HMPG_URL: 홈페이지
        - LAT: 위도
        - LNG: 경도
        - FCODE_NM: 지역명

        장애인도서관 API 필드:
        - LBRRY_NAME: 도서관명
        - ADRES: 주소
        - TEL: 전화번호
        - FDRM_CLOSE_DATE: 정기휴관일
        - XCNTS: X좌표
        - YDNTS: Y좌표
        - FCODE_NM: 지역명

        Args:
            record: Seoul API 응답 레코드

        Returns:
            변환된 레코드 또는 None
        """
        try:
            # 도서관명
            name = self.normalize_string(record.get('LBRRY_NAME'))

            if not name:
                logger.warning("Missing LBRRY_NAME, skipping record")
                return None

            # API ID: 도서관명 해시
            api_id = hashlib.md5(name.encode()).hexdigest()

            # 좌표 변환 (공공도서관: LAT/LNG, 장애인도서관: XCNTS/YDNTS)
            lat_str = record.get('LAT') or record.get('YDNTS')
            lon_str = record.get('LNG') or record.get('XCNTS')

            lat, lon = self.transform_coordinates(lat_str, lon_str)

            # 변환된 레코드 (Supabase 스키마 컬럼명에 정확히 매칭)
            transformed = {
                'api_id': api_id,
                'library_name': name,
                'library_type': 'public',  # 기본값, _collect_from_endpoint에서 덮어씀
                'guname': self.normalize_string(record.get('FCODE_NM')),
                'address': self.normalize_string(record.get('ADRES')),
                'tel': self.normalize_string(record.get('TEL')),
                'homepage': self.normalize_string(record.get('HMPG_URL')),
                'latitude': lat,
                'longitude': lon,
                'opertime': self.normalize_string(record.get('OP_TIME')),
                'closing_day': self.normalize_string(record.get('FDRM_CLOSE_DATE')),
                'book_count': None,  # API에서 제공하지 않음
                'seat_count': None,  # API에서 제공하지 않음
                'facilities': None   # API에서 제공하지 않음
            }

            return transformed

        except Exception as e:
            logger.error(f"Transform error: {e}")
            logger.debug(f"Problematic record: {record}")
            return None

    async def collect(self, max_records: Optional[int] = None) -> Dict[str, Any]:
        """
        두 개의 API에서 데이터 수집 (공공도서관 + 장애인도서관)

        Args:
            max_records: 최대 수집 레코드 수 (각 API별)

        Returns:
            수집 통계 딕셔너리
        """
        logger.info(f"Starting collection for {self.table_name}")
        from datetime import datetime
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
                # 1. 공공도서관 수집
                await self._collect_from_endpoint(
                    client,
                    'public_libraries',
                    'public',
                    max_records
                )

                # 2. 장애인도서관 수집
                await self._collect_from_endpoint(
                    client,
                    'disabled_libraries',
                    'disabled',
                    max_records
                )

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

    async def _collect_from_endpoint(
        self,
        client: SeoulAPIClient,
        endpoint_key: str,
        library_type: str,
        max_records: Optional[int]
    ):
        """
        특정 엔드포인트에서 데이터 수집

        Args:
            client: Seoul API Client
            endpoint_key: 엔드포인트 키
            library_type: 도서관 유형 ('public' or 'disabled')
            max_records: 최대 레코드 수
        """
        endpoint_name = client.get_endpoint_name(endpoint_key)

        if not endpoint_name:
            logger.warning(f"Unknown endpoint key: {endpoint_key}")
            return

        logger.info(f"Collecting from {endpoint_key} ({library_type})")

        # 데이터 수집
        raw_records = await client.fetch_all(endpoint_name, max_records=max_records)
        self.stats['total'] += len(raw_records)

        logger.info(f"Fetched {len(raw_records):,} records from {endpoint_key}")

        # 레코드 변환 및 저장
        for i, raw_record in enumerate(raw_records, 1):
            try:
                # 변환
                transformed = self.transform_record(raw_record)

                if transformed is None:
                    self.stats['skipped'] += 1
                    continue

                # 도서관 유형 설정
                transformed['library_type'] = library_type

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

                # 진행상황 로깅 (50개마다)
                if i % 50 == 0:
                    logger.info(f"Progress [{endpoint_key}]: {i}/{len(raw_records)}")

            except Exception as e:
                self.stats['failed'] += 1
                error_msg = f"{endpoint_key} record {i} failed: {str(e)}"
                logger.error(error_msg)
                self.stats['errors'].append(error_msg)


async def main():
    """테스트용 메인 함수"""
    import sys
    from pathlib import Path

    # Add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    collector = LibrariesCollector()

    # 전체 수집 (도서관은 수가 적어서 전체 수집)
    stats = await collector.collect()

    print("\n" + "="*60)
    print("Collection Results:")
    print("="*60)
    print(f"Total:   {stats['total']}")
    print(f"Success: {stats['success']}")
    print(f"Failed:  {stats['failed']}")
    print(f"Skipped: {stats['skipped']}")

    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for error in stats['errors'][:5]:
            print(f"  - {error}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
