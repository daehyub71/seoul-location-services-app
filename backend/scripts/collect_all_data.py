"""
전체 데이터 수집 스크립트
모든 Collector를 실행하여 Supabase에 데이터 저장
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors import (
    CulturalEventsCollector,
    LibrariesCollector,
    CulturalSpacesCollector,
    FutureHeritagesCollector,
    PublicReservationsCollector
)


async def collect_all(max_records_per_endpoint: int = None):
    """
    모든 데이터 수집

    Args:
        max_records_per_endpoint: 엔드포인트당 최대 레코드 수 (None이면 전체)
    """
    print("\n" + "="*70)
    print("Seoul Open API 전체 데이터 수집")
    print("="*70)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if max_records_per_endpoint:
        print(f"엔드포인트당 최대 레코드: {max_records_per_endpoint}")
    else:
        print("전체 데이터 수집 모드")

    print("="*70 + "\n")

    # 수집기 목록
    collectors = [
        ("문화행사", CulturalEventsCollector()),
        ("도서관", LibrariesCollector()),
        ("문화공간", CulturalSpacesCollector()),
        ("미래유산", FutureHeritagesCollector()),
        ("공공예약", PublicReservationsCollector()),
    ]

    # 전체 통계
    total_stats = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    results = []

    # 각 Collector 실행
    for i, (name, collector) in enumerate(collectors, 1):
        print(f"\n[{i}/{len(collectors)}] {name} 수집 중...")
        print("-" * 70)

        try:
            stats = await collector.collect(max_records=max_records_per_endpoint)

            # 통계 누적
            total_stats['total'] += stats['total']
            total_stats['success'] += stats['success']
            total_stats['failed'] += stats['failed']
            total_stats['skipped'] += stats['skipped']

            results.append({
                'name': name,
                'success': True,
                'stats': stats
            })

            print(f"✅ {name} 수집 완료:")
            print(f"   Total: {stats['total']}, Success: {stats['success']}, "
                  f"Failed: {stats['failed']}, Skipped: {stats['skipped']}")

        except Exception as e:
            logger.error(f"❌ {name} 수집 실패: {e}")
            results.append({
                'name': name,
                'success': False,
                'error': str(e)
            })

    # 최종 결과 출력
    print("\n" + "="*70)
    print("📊 전체 수집 결과")
    print("="*70)

    for result in results:
        name = result['name']
        if result['success']:
            stats = result['stats']
            status = "✅ 성공"
            detail = f"(Success: {stats['success']}, Failed: {stats['failed']}, Skipped: {stats['skipped']})"
        else:
            status = "❌ 실패"
            detail = f"(Error: {result['error']})"

        print(f"{name:<15} {status:<10} {detail}")

    print("\n" + "-"*70)
    print(f"총 레코드:     {total_stats['total']:,}")
    print(f"성공:         {total_stats['success']:,}")
    print(f"실패:         {total_stats['failed']:,}")
    print(f"스킵:         {total_stats['skipped']:,}")
    print(f"성공률:       {total_stats['success']/total_stats['total']*100:.1f}%" if total_stats['total'] > 0 else "N/A")
    print("-"*70)

    print(f"\n완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70 + "\n")


async def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Seoul Open API 데이터 수집')
    parser.add_argument(
        '--max-records',
        type=int,
        default=None,
        help='엔드포인트당 최대 레코드 수 (기본값: 전체)'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='테스트 모드 (각 엔드포인트에서 10개만 수집)'
    )

    args = parser.parse_args()

    # 테스트 모드
    if args.test:
        max_records = 10
        print("🧪 테스트 모드: 각 엔드포인트에서 10개만 수집")
    else:
        max_records = args.max_records

    await collect_all(max_records_per_endpoint=max_records)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger = logging.getLogger(__name__)

    asyncio.run(main())
