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

    Note: API에서 X_COORD(위도), Y_COORD(경도) 제공
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
        - X_COORD: 위도 (latitude)
        - Y_COORD: 경도 (longitude)
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

            # 좌표 추출: X_COORD=위도, Y_COORD=경도
            x_coord_str = record.get('X_COORD')  # Latitude
            y_coord_str = record.get('Y_COORD')  # Longitude
            lat, lon = self.transform_coordinates(x_coord_str, y_coord_str, swap=False)

            # 변환된 레코드 (Supabase 스키마 컬럼명에 정확히 매칭)
            transformed = {
                'api_id': api_id,
                'fac_name': name,
                'guname': self.normalize_string(record.get('GUNAME')),
                'subjcode': self.normalize_string(record.get('SUBJCODE')),
                'fac_code': self.normalize_string(record.get('FAC_CODE')),
                'codename': self.normalize_string(record.get('CODENAME')),
                'addr': self.normalize_string(record.get('ADDR')),
                'zipcode': self.normalize_string(record.get('ZIPCODE')),
                'telno': self.normalize_string(record.get('TELNO') or record.get('PHNE')),
                'homepage': self.normalize_string(record.get('HOMEPAGE')),
                'restroomyn': self.normalize_string(record.get('RESTROOMYN')),
                'parking_info': self.normalize_string(record.get('PARKING')),
                'main_purps': self.normalize_string(record.get('MAIN_PURPS')),
                'latitude': lat,  # X_COORD (위도)
                'longitude': lon  # Y_COORD (경도)
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
