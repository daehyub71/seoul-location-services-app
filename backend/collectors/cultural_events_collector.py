"""
Cultural Events Collector
문화행사 정보 수집기
"""

import logging
from typing import Dict, Optional, Any

from collectors.base_collector import BaseCollector

logger = logging.getLogger(__name__)


class CulturalEventsCollector(BaseCollector):
    """
    문화행사 정보 수집기

    API: /culturalEventInfo
    테이블: cultural_events
    """

    @property
    def table_name(self) -> str:
        return 'cultural_events'

    @property
    def endpoint_key(self) -> str:
        return 'cultural_events'

    def transform_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        API 응답 레코드를 cultural_events 스키마에 맞게 변환

        API 필드:
        - CODENAME: 분류명
        - GUNAME: 자치구
        - TITLE: 제목
        - DATE: 날짜 (YYYY-MM-DD~YYYY-MM-DD)
        - PLACE: 장소
        - ORG_NAME: 기관명
        - USE_TRGT: 이용대상
        - USE_FEE: 이용요금
        - PLAYER: 출연자
        - PROGRAM: 프로그램
        - ETC_DESC: 기타설명
        - ORG_LINK: 기관링크
        - MAIN_IMG: 대표이미지
        - RGSTDATE: 등록일
        - TICKET: 티켓 구분
        - STRTDATE: 시작일
        - END_DATE: 종료일
        - THEMECODE: 테마분류
        - LAT: 위도
        - LOT: 경도
        - IS_FREE: 유무료
        - HMPG_ADDR: 홈페이지
        - PRO_TIME: 공연시간

        Args:
            record: Seoul API 응답 레코드

        Returns:
            변환된 레코드 또는 None
        """
        try:
            # API ID 생성 (TITLE + PLACE + STRTDATE 조합)
            title = self.normalize_string(record.get('TITLE'))
            place = self.normalize_string(record.get('PLACE'))
            start_date = self.normalize_string(record.get('STRTDATE'))

            if not title:
                logger.warning("Missing TITLE, skipping record")
                return None

            # API ID: title의 해시값 사용
            import hashlib
            api_id_source = f"{title}_{place}_{start_date}"
            api_id = hashlib.md5(api_id_source.encode()).hexdigest()

            # 좌표 변환
            lat_str = record.get('LAT')
            lon_str = record.get('LOT')
            lat, lon = self.transform_coordinates(lat_str, lon_str)

            # 날짜 파싱
            start_date_parsed = self.parse_date(
                record.get('STRTDATE', '').split()[0] if record.get('STRTDATE') else None,
                format='%Y-%m-%d'
            )
            end_date_parsed = self.parse_date(
                record.get('END_DATE', '').split()[0] if record.get('END_DATE') else None,
                format='%Y-%m-%d'
            )
            registered_date = self.parse_date(record.get('RGSTDATE'))

            # 유무료 boolean 변환
            is_free_str = self.normalize_string(record.get('IS_FREE'))
            is_free = is_free_str == '무료' if is_free_str else None

            # 변환된 레코드
            transformed = {
                'api_id': api_id,
                'title': title,
                'category': self.normalize_string(record.get('CODENAME')),
                'district': self.normalize_string(record.get('GUNAME')),
                'place': place,
                'organization': self.normalize_string(record.get('ORG_NAME')),
                'target': self.normalize_string(record.get('USE_TRGT')),
                'fee': self.normalize_string(record.get('USE_FEE')),
                'is_free': is_free,
                'performer': self.normalize_string(record.get('PLAYER')),
                'program': self.normalize_string(record.get('PROGRAM')),
                'description': self.normalize_string(record.get('ETC_DESC')),
                'start_date': start_date_parsed,
                'end_date': end_date_parsed,
                'time_info': self.normalize_string(record.get('PRO_TIME')),
                'registered_at': registered_date,
                'theme': self.normalize_string(record.get('THEMECODE')),
                'ticket_type': self.normalize_string(record.get('TICKET')),
                'lat': lat,
                'lot': lon,
                'homepage_url': self.normalize_string(record.get('HMPG_ADDR')),
                'org_link': self.normalize_string(record.get('ORG_LINK')),
                'main_image': self.normalize_string(record.get('MAIN_IMG'))
            }

            return transformed

        except Exception as e:
            logger.error(f"Transform error: {e}")
            logger.debug(f"Problematic record: {record}")
            return None


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

    collector = CulturalEventsCollector()

    # 10개만 수집 (테스트)
    stats = await collector.collect(max_records=10)

    print("\n" + "="*60)
    print("Collection Results:")
    print("="*60)
    print(f"Total:   {stats['total']}")
    print(f"Success: {stats['success']}")
    print(f"Failed:  {stats['failed']}")
    print(f"Skipped: {stats['skipped']}")

    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for error in stats['errors'][:5]:  # 처음 5개만 출력
            print(f"  - {error}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
