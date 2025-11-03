"""
Future Heritages Collector
미래유산 정보 수집기
"""

import logging
from typing import Dict, Optional, Any
import hashlib

from collectors.base_collector import BaseCollector

logger = logging.getLogger(__name__)


class FutureHeritagesCollector(BaseCollector):
    """
    미래유산 정보 수집기

    API: /futureHeritageInfo
    테이블: future_heritages

    Note: API에서 YCRD(위도), XCRD(경도) 제공
    """

    @property
    def table_name(self) -> str:
        return 'future_heritages'

    @property
    def endpoint_key(self) -> str:
        return 'future_heritage'

    def transform_record(self, record: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        API 응답 레코드를 future_heritages 스키마에 맞게 변환

        API 필드:
        - FTR_HRTG_NM: 유산명
        - FTR_HRTG_ID: 미래유산 ID
        - RGN: 지역(구명)
        - LCTN_NM: 위치/주소
        - YCRD: 위도 (latitude)
        - XCRD: 경도 (longitude)
        - CATEGORY: 카테고리
        - MAIN_CATEGORY: 주요 카테고리

        Args:
            record: Seoul API 응답 레코드

        Returns:
            변환된 레코드 또는 None
        """
        try:
            # 유산명 (FTR_HRTG_NM)
            name = self.normalize_string(record.get('FTR_HRTG_NM'))

            if not name:
                logger.warning(f"Missing FTR_HRTG_NM, skipping record: {record}")
                return None

            # FTR_HRTG_ID를 API ID로 사용, 없으면 이름 해시
            ftr_hrtg_id = record.get('FTR_HRTG_ID')
            if ftr_hrtg_id:
                api_id = str(int(ftr_hrtg_id)) if isinstance(ftr_hrtg_id, float) else str(ftr_hrtg_id)
            else:
                api_id = hashlib.md5(name.encode()).hexdigest()

            # 좌표 추출: YCRD=위도, XCRD=경도
            ycrd_str = record.get('YCRD')  # Latitude
            xcrd_str = record.get('XCRD')  # Longitude
            lat, lon = self.transform_coordinates(ycrd_str, xcrd_str, swap=False)

            # 변환된 레코드 (Supabase 스키마 컬럼명에 정확히 매칭)
            transformed = {
                'api_id': api_id,
                'no': None,  # API에 NO 필드 없음
                'main_category': self.normalize_string(record.get('MAIN_CATEGORY') or record.get('CATEGORY')),
                'sub_category': None,  # API에 sub_category 해당 필드 없음
                'name': name,
                'year_designated': None,  # API에 year_designated 해당 필드 없음
                'gu_name': self.normalize_string(record.get('RGN')),  # RGN → gu_name
                'dong_name': None,  # API에 dong_name 해당 필드 없음
                'address': self.normalize_string(record.get('LCTN_NM')),  # LCTN_NM → address
                'latitude': lat,  # YCRD (위도)
                'longitude': lon,  # XCRD (경도)
                'description': None,  # API에 description 해당 필드 없음
                'reason': None,  # API에 reason 해당 필드 없음
                'main_img': None  # API에 main_img 해당 필드 없음
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

    collector = FutureHeritagesCollector()

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
