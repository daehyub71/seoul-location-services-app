"""
Cultural Spaces Collector
문화공간 정보 수집기
"""

import logging
from typing import Dict, Optional, Any
import hashlib

from collectors.base_collector import BaseCollector

logger = logging.getLogger(__name__)


class CulturalSpacesCollector(BaseCollector):
    """
    문화공간 정보 수집기

    API: /culturalSpaceInfo
    테이블: cultural_spaces

    Note: 이 API는 좌표 데이터가 없고 주소만 제공됨
    """

    @property
    def table_name(self) -> str:
        return 'cultural_spaces'

    @property
    def endpoint_key(self) -> str:
        return 'cultural_spaces'

    def transform_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        API 응답 레코드를 cultural_spaces 스키마에 맞게 변환

        API 필드:
        - FAC_NAME: 시설명
        - SUBJCODE: 주제분류코드
        - CODENAME: 분류명
        - FAC_DESC: 시설설명
        - ADDR: 주소
        - PHNE: 전화번호
        - HOMEPAGE: 홈페이지
        - OPENHOUR: 운영시간
        - CLOSEDAY: 휴무일
        - SUBWAY_INFO: 지하철정보
        - BUS_INFO: 버스정보
        - ENTRANCE_FEE: 입장료

        Args:
            record: Seoul API 응답 레코드

        Returns:
            변환된 레코드 또는 None
        """
        try:
            # 시설명
            name = self.normalize_string(record.get('FAC_NAME'))

            if not name:
                logger.warning("Missing FAC_NAME, skipping record")
                return None

            # API ID: 시설명 해시
            api_id = hashlib.md5(name.encode()).hexdigest()

            # 입장료 boolean 변환
            entrance_fee_str = self.normalize_string(record.get('ENTRANCE_FEE'))
            is_free = entrance_fee_str in ['무료', '없음'] if entrance_fee_str else None

            # 변환된 레코드
            transformed = {
                'api_id': api_id,
                'name': name,
                'category_code': self.normalize_string(record.get('SUBJCODE')),
                'category_name': self.normalize_string(record.get('CODENAME')),
                'description': self.normalize_string(record.get('FAC_DESC')),
                'address': self.normalize_string(record.get('ADDR')),
                'phone': self.normalize_string(record.get('PHNE')),
                'homepage_url': self.normalize_string(record.get('HOMEPAGE')),
                'operating_hours': self.normalize_string(record.get('OPENHOUR')),
                'closed_days': self.normalize_string(record.get('CLOSEDAY')),
                'subway_info': self.normalize_string(record.get('SUBWAY_INFO')),
                'bus_info': self.normalize_string(record.get('BUS_INFO')),
                'entrance_fee': entrance_fee_str,
                'is_free': is_free,
                'lat': None,  # 좌표 없음
                'lot': None   # 좌표 없음
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

    sys.path.insert(0, str(Path(__file__).parent.parent))

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    collector = CulturalSpacesCollector()

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
        for error in stats['errors'][:5]:
            print(f"  - {error}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
