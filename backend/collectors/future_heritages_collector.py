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

            # 등록일 파싱
            regist_date = self.parse_date(record.get('REGIST_DATE'))

            # 변환된 레코드
            transformed = {
                'api_id': api_id,
                'name': name,
                'category': self.normalize_string(record.get('CATEGORY')),
                'era': self.normalize_string(record.get('ERA')),
                'address': self.normalize_string(record.get('ADDR')),
                'content': self.normalize_string(record.get('CONTENT')),
                'main_purpose': self.normalize_string(record.get('MAIN_PURPS')),
                'registered_at': regist_date,
                'main_image': self.normalize_string(record.get('T_IMAGE')),
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
