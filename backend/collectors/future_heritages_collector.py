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

    Note: 이 API는 좌표 데이터가 없고 주소만 제공됨
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
        - NM: 유산명
        - CATEGORY: 카테고리
        - ERA: 시대
        - MANAGE_NO: 관리번호
        - ADDR: 주소
        - CONTENT: 내용
        - MAIN_PURPS: 주요용도
        - REGIST_DATE: 등록일
        - T_IMAGE: 대표이미지

        Args:
            record: Seoul API 응답 레코드

        Returns:
            변환된 레코드 또는 None
        """
        try:
            # 유산명
            name = self.normalize_string(record.get('NM'))

            if not name:
                logger.warning("Missing NM, skipping record")
                return None

            # 관리번호가 있으면 그것을 API ID로 사용, 없으면 이름 해시
            manage_no = self.normalize_string(record.get('MANAGE_NO'))
            if manage_no:
                api_id = manage_no
            else:
                api_id = hashlib.md5(name.encode()).hexdigest()

            # 등록 연도 파싱 (year_designated는 INTEGER)
            regist_date_str = record.get('REGIST_DATE')
            year_designated = self.parse_date(regist_date_str, target_type='year') if regist_date_str else None

            # 변환된 레코드 (Supabase 스키마 컬럼명에 정확히 매칭)
            transformed = {
                'api_id': api_id,
                'no': int(record.get('NO')) if record.get('NO') else None,
                'main_category': self.normalize_string(record.get('CATEGORY')),  # CATEGORY → main_category
                'sub_category': self.normalize_string(record.get('ERA')),  # ERA → sub_category로 사용
                'name': name,
                'year_designated': year_designated,  # INTEGER
                'gu_name': self.normalize_string(record.get('GU_NAME')),
                'dong_name': self.normalize_string(record.get('DONG_NAME')),
                'address': self.normalize_string(record.get('ADDR')),
                'latitude': None,  # API에서 제공하지 않음 (지오코딩 필요)
                'longitude': None,  # API에서 제공하지 않음 (지오코딩 필요)
                'description': self.normalize_string(record.get('CONTENT')),
                'reason': self.normalize_string(record.get('MAIN_PURPS')),
                'main_img': self.normalize_string(record.get('T_IMAGE'))
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
