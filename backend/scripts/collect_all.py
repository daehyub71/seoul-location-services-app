"""
전체 데이터 수집 스크립트 (Day 6)
모든 Collector를 순차 실행하여 Supabase에 데이터 저장
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import argparse

# tqdm for progress bars
try:
    from tqdm import tqdm
except ImportError:
    print("Warning: tqdm not installed. Install with: pip install tqdm")
    tqdm = None

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors import (
    CulturalEventsCollector,
    LibrariesCollector,
    CulturalSpacesCollector,
    FutureHeritagesCollector,
    PublicReservationsCollector
)

logger = logging.getLogger(__name__)


class DataCollectionOrchestrator:
    """
    데이터 수집 오케스트레이터
    - 9개 Collector 순차 실행 (현재 5개 구현됨)
    - 진행상황 표시 (tqdm)
    - Supabase Upsert (중복 시 업데이트)
    - 수집 로그 저장
    """

    def __init__(self):
        self.collectors = [
            ("문화행사", CulturalEventsCollector()),
            ("도서관", LibrariesCollector()),
            ("문화공간", CulturalSpacesCollector()),
            ("미래유산", FutureHeritagesCollector()),
            ("공공예약", PublicReservationsCollector()),
        ]

        self.total_stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        self.results: List[Dict[str, Any]] = []

    async def collect_all(self, max_records: int = None, verbose: bool = True):
        """
        모든 데이터 수집

        Args:
            max_records: 엔드포인트당 최대 레코드 수 (None이면 전체)
            verbose: 상세 출력 여부

        Returns:
            수집 통계 딕셔너리
        """
        start_time = datetime.now()

        if verbose:
            self._print_header(max_records)

        # 각 Collector 실행
        if tqdm:
            collector_iterator = tqdm(
                enumerate(self.collectors, 1),
                total=len(self.collectors),
                desc="전체 수집 진행",
                unit="collector"
            )
        else:
            collector_iterator = enumerate(self.collectors, 1)

        for i, (name, collector) in collector_iterator:
            if verbose and not tqdm:
                print(f"\n[{i}/{len(self.collectors)}] {name} 수집 중...")
                print("-" * 70)

            try:
                # 데이터 수집
                stats = await collector.collect(max_records=max_records)

                # 통계 누적
                self.total_stats['total'] += stats['total']
                self.total_stats['success'] += stats['success']
                self.total_stats['failed'] += stats['failed']
                self.total_stats['skipped'] += stats['skipped']

                self.results.append({
                    'name': name,
                    'success': True,
                    'stats': stats,
                    'table': collector.table_name
                })

                if verbose and not tqdm:
                    print(f"✅ {name} 수집 완료:")
                    print(f"   Total: {stats['total']}, Success: {stats['success']}, "
                          f"Failed: {stats['failed']}, Skipped: {stats['skipped']}")

                logger.info(f"{name} 수집 완료: {stats['success']}/{stats['total']} 성공")

            except Exception as e:
                logger.error(f"{name} 수집 실패: {e}", exc_info=True)

                self.results.append({
                    'name': name,
                    'success': False,
                    'error': str(e),
                    'table': collector.table_name
                })

        # 최종 결과 출력
        duration = (datetime.now() - start_time).total_seconds()

        if verbose:
            self._print_summary(duration)

        return {
            'total_stats': self.total_stats,
            'results': self.results,
            'duration': duration
        }

    def _print_header(self, max_records: int = None):
        """헤더 출력"""
        print("\n" + "="*70)
        print("🗂️  Seoul Open API 전체 데이터 수집")
        print("="*70)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        if max_records:
            print(f"엔드포인트당 최대 레코드: {max_records}")
        else:
            print("전체 데이터 수집 모드")

        print(f"수집기 개수: {len(self.collectors)}")
        print("="*70 + "\n")

    def _print_summary(self, duration: float):
        """최종 결과 요약 출력"""
        print("\n" + "="*70)
        print("📊 전체 수집 결과")
        print("="*70)

        for result in self.results:
            name = result['name']
            table = result.get('table', 'N/A')

            if result['success']:
                stats = result['stats']
                status = "✅ 성공"
                detail = f"(Success: {stats['success']}, Failed: {stats['failed']}, Skipped: {stats['skipped']})"
            else:
                status = "❌ 실패"
                detail = f"(Error: {result['error'][:50]}...)"

            print(f"{name:<15} {status:<10} {detail}")
            print(f"                → 테이블: {table}")

        print("\n" + "-"*70)
        print(f"총 레코드:     {self.total_stats['total']:,}")
        print(f"성공:         {self.total_stats['success']:,}")
        print(f"실패:         {self.total_stats['failed']:,}")
        print(f"스킵:         {self.total_stats['skipped']:,}")

        if self.total_stats['total'] > 0:
            success_rate = self.total_stats['success'] / self.total_stats['total'] * 100
            print(f"성공률:       {success_rate:.1f}%")

        print(f"소요 시간:    {duration:.1f}초 ({duration/60:.1f}분)")
        print("-"*70)

        print(f"\n완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")


async def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(
        description='Seoul Open API 데이터 수집',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 전체 수집
  python collect_all.py

  # 테스트 모드 (각 엔드포인트 10개만)
  python collect_all.py --test

  # 각 엔드포인트에서 100개씩
  python collect_all.py --max-records 100

  # 조용한 모드 (로그만)
  python collect_all.py --quiet
        """
    )

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
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='조용한 모드 (상세 출력 최소화)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='로그 레벨 (기본값: INFO)'
    )

    args = parser.parse_args()

    # 로그 레벨 설정
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('logs/collect_all.log', encoding='utf-8')
        ]
    )

    # 테스트 모드
    if args.test:
        max_records = 10
        print("🧪 테스트 모드: 각 엔드포인트에서 10개만 수집\n")
    else:
        max_records = args.max_records

    # 수집 실행
    orchestrator = DataCollectionOrchestrator()
    await orchestrator.collect_all(
        max_records=max_records,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    # logs 디렉토리 생성
    Path('logs').mkdir(exist_ok=True)

    asyncio.run(main())
