"""
Public Reservations Collector
공공예약 정보 수집기 (의료/교육/문화 통합)
"""

import logging
from typing import Dict, Optional, Any
import hashlib

from collectors.base_collector import BaseCollector
from collectors.seoul_api_client import SeoulAPIClient

logger = logging.getLogger(__name__)


class PublicReservationsCollector(BaseCollector):
    """
    공공예약 정보 수집기

    API:
    - /ListPublicReservationMedical (의료)
    - /ListPublicReservationEducation (교육)
    - /ListPublicReservationCulture (문화)
    - /tvYeyakCOllect (전체 - 중복 방지를 위해 사용 안함)

    테이블: public_reservations

    Note: 이 API들은 LAT/LOT 필드가 반대로 저장되어 있음 (swap=True 필요)
    """

    @property
    def table_name(self) -> str:
        return 'public_reservations'

    @property
    def endpoint_key(self) -> str:
        # 메인으로는 의료 사용
        return 'reservation_medical'

    def transform_record(self, record: Dict[str, Any], category: str) -> Optional[Dict[str, Any]]:
        """
        API 응답 레코드를 public_reservations 스키마에 맞게 변환

        공통 API 필드:
        - SVCNM: 서비스명
        - SVCID: 서비스ID
        - PLACENM: 장소명
        - PAYATNM: 결제방법
        - RCPTBGNDT: 접수시작일시
        - RCPTENDDT: 접수종료일시
        - SVCOPNBGNDT: 서비스개시시작일시
        - SVCOPNENDDT: 서비스개시종료일시
        - AREANM: 지역명
        - IMGURL: 이미지URL
        - DTLCONT: 상세내용
        - TELNO: 전화번호
        - V_MAX: 최대인원
        - V_MIN: 최소인원
        - REVSTDDAY: 예약마감일
        - X: X좌표 (실제로는 경도)
        - Y: Y좌표 (실제로는 위도)

        Args:
            record: Seoul API 응답 레코드
            category: 카테고리 ('medical', 'education', 'culture')

        Returns:
            변환된 레코드 또는 None
        """
        try:
            # 서비스명
            name = self.normalize_string(record.get('SVCNM'))
            service_id = self.normalize_string(record.get('SVCID'))

            if not name or not service_id:
                logger.warning("Missing SVCNM or SVCID, skipping record")
                return None

            # API ID: 서비스 ID 사용
            api_id = service_id

            # 좌표 변환 (LAT/LOT가 반대로 저장됨 - swap=True)
            # X는 실제로 경도(LOT), Y는 실제로 위도(LAT)
            lat_str = record.get('Y')  # Y가 위도
            lon_str = record.get('X')  # X가 경도

            lat, lon = self.transform_coordinates(lat_str, lon_str, swap=False)

            # 날짜 파싱 (YYYY-MM-DD HH:MM:SS.0 형식)
            rcpt_begin = self.parse_date(
                record.get('RCPTBGNDT', '').split()[0] if record.get('RCPTBGNDT') else None,
                format='%Y-%m-%d'
            )
            rcpt_end = self.parse_date(
                record.get('RCPTENDDT', '').split()[0] if record.get('RCPTENDDT') else None,
                format='%Y-%m-%d'
            )
            svc_begin = self.parse_date(
                record.get('SVCOPNBGNDT', '').split()[0] if record.get('SVCOPNBGNDT') else None,
                format='%Y-%m-%d'
            )
            svc_end = self.parse_date(
                record.get('SVCOPNENDDT', '').split()[0] if record.get('SVCOPNENDDT') else None,
                format='%Y-%m-%d'
            )

            # 인원 수 변환
            max_capacity = None
            min_capacity = None

            try:
                v_max = record.get('V_MAX')
                if v_max:
                    max_capacity = int(v_max)
            except (ValueError, TypeError):
                pass

            try:
                v_min = record.get('V_MIN')
                if v_min:
                    min_capacity = int(v_min)
            except (ValueError, TypeError):
                pass

            # 변환된 레코드
            transformed = {
                'api_id': api_id,
                'service_name': name,
                'category': category,
                'place_name': self.normalize_string(record.get('PLACENM')),
                'payment_method': self.normalize_string(record.get('PAYATNM')),
                'reception_start': rcpt_begin,
                'reception_end': rcpt_end,
                'service_start': svc_begin,
                'service_end': svc_end,
                'district': self.normalize_string(record.get('AREANM')),
                'description': self.normalize_string(record.get('DTLCONT')),
                'phone': self.normalize_string(record.get('TELNO')),
                'max_capacity': max_capacity,
                'min_capacity': min_capacity,
                'reservation_deadline': self.normalize_string(record.get('REVSTDDAY')),
                'image_url': self.normalize_string(record.get('IMGURL')),
                'lat': lat,
                'lot': lon
            }

            return transformed

        except Exception as e:
            logger.error(f"Transform error: {e}")
            logger.debug(f"Problematic record: {record}")
            return None

    async def collect(self, max_records: Optional[int] = None) -> Dict[str, Any]:
        """
        세 개의 API에서 데이터 수집 (의료/교육/문화)

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
                # 1. 의료 예약
                await self._collect_from_endpoint(
                    client,
                    'reservation_medical',
                    'medical',
                    max_records
                )

                # 2. 교육 예약
                await self._collect_from_endpoint(
                    client,
                    'reservation_education',
                    'education',
                    max_records
                )

                # 3. 문화 예약
                await self._collect_from_endpoint(
                    client,
                    'reservation_culture',
                    'culture',
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
        category: str,
        max_records: Optional[int]
    ):
        """
        특정 엔드포인트에서 데이터 수집

        Args:
            client: Seoul API Client
            endpoint_key: 엔드포인트 키
            category: 카테고리 ('medical', 'education', 'culture')
            max_records: 최대 레코드 수
        """
        endpoint_name = client.get_endpoint_name(endpoint_key)

        if not endpoint_name:
            logger.warning(f"Unknown endpoint key: {endpoint_key}")
            return

        logger.info(f"Collecting from {endpoint_key} ({category})")

        # 데이터 수집
        raw_records = await client.fetch_all(endpoint_name, max_records=max_records)
        self.stats['total'] += len(raw_records)

        logger.info(f"Fetched {len(raw_records):,} records from {endpoint_key}")

        # 레코드 변환 및 저장
        for i, raw_record in enumerate(raw_records, 1):
            try:
                # 변환
                transformed = self.transform_record(raw_record, category)

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

    sys.path.insert(0, str(Path(__file__).parent.parent))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    collector = PublicReservationsCollector()

    # 각 카테고리에서 5개씩 수집 (테스트)
    stats = await collector.collect(max_records=5)

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
