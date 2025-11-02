"""
데이터 수집 스케줄러 (Day 6)
APScheduler를 사용한 자동 수집 시스템
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
import signal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    print("Error: APScheduler not installed. Install with: pip install apscheduler")
    sys.exit(1)

from collectors import (
    CulturalEventsCollector,
    LibrariesCollector,
    CulturalSpacesCollector,
    FutureHeritagesCollector,
    PublicReservationsCollector
)

logger = logging.getLogger(__name__)


class DataCollectionScheduler:
    """
    데이터 수집 스케줄러

    스케줄:
    - 매일 03:00: 문화행사, 공공예약 (변동이 잦은 데이터)
    - 매주 월요일 04:00: 도서관, 문화공간 (변동이 적은 데이터)
    - 매월 1일 05:00: 미래유산 (거의 변하지 않는 데이터)
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone='Asia/Seoul')
        self.is_running = False

        # Graceful shutdown을 위한 signal handler
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Graceful shutdown"""
        logger.info(f"Received signal {signum}. Shutting down gracefully...")
        self.stop()
        sys.exit(0)

    async def collect_daily_data(self):
        """매일 수집: 문화행사, 공공예약"""
        logger.info("=" * 70)
        logger.info("📅 일일 데이터 수집 시작 (문화행사, 공공예약)")
        logger.info("=" * 70)

        collectors = [
            ("문화행사", CulturalEventsCollector()),
            ("공공예약", PublicReservationsCollector()),
        ]

        await self._run_collectors(collectors, "daily")

    async def collect_weekly_data(self):
        """주간 수집: 도서관, 문화공간"""
        logger.info("=" * 70)
        logger.info("📅 주간 데이터 수집 시작 (도서관, 문화공간)")
        logger.info("=" * 70)

        collectors = [
            ("도서관", LibrariesCollector()),
            ("문화공간", CulturalSpacesCollector()),
        ]

        await self._run_collectors(collectors, "weekly")

    async def collect_monthly_data(self):
        """월간 수집: 미래유산"""
        logger.info("=" * 70)
        logger.info("📅 월간 데이터 수집 시작 (미래유산)")
        logger.info("=" * 70)

        collectors = [
            ("미래유산", FutureHeritagesCollector()),
        ]

        await self._run_collectors(collectors, "monthly")

    async def _run_collectors(self, collectors, schedule_type: str):
        """
        Collector 실행

        Args:
            collectors: (이름, Collector 인스턴스) 튜플 리스트
            schedule_type: 스케줄 타입 ('daily', 'weekly', 'monthly')
        """
        start_time = datetime.now()
        total_success = 0
        total_failed = 0
        total_records = 0

        for name, collector in collectors:
            try:
                logger.info(f"⏳ {name} 수집 시작...")

                stats = await collector.collect()

                total_records += stats['total']
                total_success += stats['success']
                total_failed += stats['failed']

                logger.info(
                    f"✅ {name} 수집 완료: "
                    f"{stats['success']}/{stats['total']} 성공 "
                    f"({stats['failed']} 실패, {stats['skipped']} 스킵)"
                )

            except Exception as e:
                logger.error(f"❌ {name} 수집 실패: {e}", exc_info=True)
                total_failed += 1

        duration = (datetime.now() - start_time).total_seconds()

        logger.info("=" * 70)
        logger.info(f"📊 {schedule_type.upper()} 수집 완료")
        logger.info(f"  총 레코드: {total_records:,}")
        logger.info(f"  성공: {total_success:,}")
        logger.info(f"  실패: {total_failed:,}")
        logger.info(f"  소요 시간: {duration:.1f}초")
        logger.info("=" * 70)

    def setup_jobs(self):
        """스케줄 작업 설정"""

        # 매일 03:00 - 문화행사, 공공예약
        self.scheduler.add_job(
            self.collect_daily_data,
            CronTrigger(hour=3, minute=0),
            id='daily_collection',
            name='일일 데이터 수집 (문화행사, 공공예약)',
            replace_existing=True
        )
        logger.info("✅ 일일 수집 작업 등록 완료: 매일 03:00")

        # 매주 월요일 04:00 - 도서관, 문화공간
        self.scheduler.add_job(
            self.collect_weekly_data,
            CronTrigger(day_of_week='mon', hour=4, minute=0),
            id='weekly_collection',
            name='주간 데이터 수집 (도서관, 문화공간)',
            replace_existing=True
        )
        logger.info("✅ 주간 수집 작업 등록 완료: 매주 월요일 04:00")

        # 매월 1일 05:00 - 미래유산
        self.scheduler.add_job(
            self.collect_monthly_data,
            CronTrigger(day=1, hour=5, minute=0),
            id='monthly_collection',
            name='월간 데이터 수집 (미래유산)',
            replace_existing=True
        )
        logger.info("✅ 월간 수집 작업 등록 완료: 매월 1일 05:00")

    def start(self):
        """스케줄러 시작"""
        if self.is_running:
            logger.warning("스케줄러가 이미 실행 중입니다.")
            return

        self.setup_jobs()

        logger.info("=" * 70)
        logger.info("🚀 데이터 수집 스케줄러 시작")
        logger.info("=" * 70)

        # 등록된 작업 출력
        jobs = self.scheduler.get_jobs()
        logger.info(f"등록된 작업 개수: {len(jobs)}")

        for job in jobs:
            logger.info(f"  - {job.name}: {job.trigger}")

        logger.info("=" * 70)

        self.scheduler.start()
        self.is_running = True

        logger.info("✅ 스케줄러가 시작되었습니다. (Ctrl+C로 종료)")

    def stop(self):
        """스케줄러 중지"""
        if not self.is_running:
            logger.warning("스케줄러가 실행 중이 아닙니다.")
            return

        logger.info("⏹️  스케줄러를 중지합니다...")
        self.scheduler.shutdown(wait=True)
        self.is_running = False
        logger.info("✅ 스케줄러가 중지되었습니다.")

    def print_next_run_times(self):
        """다음 실행 시간 출력"""
        jobs = self.scheduler.get_jobs()

        print("\n" + "=" * 70)
        print("⏰ 다음 실행 예정 시간")
        print("=" * 70)

        for job in jobs:
            next_run = job.next_run_time
            if next_run:
                print(f"{job.name}:")
                print(f"  → {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"{job.name}: 예정 없음")

        print("=" * 70 + "\n")


async def run_once(job_type: str):
    """
    특정 작업을 즉시 실행 (테스트용)

    Args:
        job_type: 'daily', 'weekly', 'monthly'
    """
    scheduler = DataCollectionScheduler()

    if job_type == 'daily':
        await scheduler.collect_daily_data()
    elif job_type == 'weekly':
        await scheduler.collect_weekly_data()
    elif job_type == 'monthly':
        await scheduler.collect_monthly_data()
    else:
        logger.error(f"Unknown job type: {job_type}")
        print("사용 가능한 job_type: daily, weekly, monthly")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Seoul Open API 데이터 수집 스케줄러',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 스케줄러 시작 (백그라운드 실행)
  python scheduler.py

  # 일일 수집 즉시 실행 (테스트)
  python scheduler.py --run-once daily

  # 주간 수집 즉시 실행 (테스트)
  python scheduler.py --run-once weekly

  # 월간 수집 즉시 실행 (테스트)
  python scheduler.py --run-once monthly
        """
    )

    parser.add_argument(
        '--run-once',
        choices=['daily', 'weekly', 'monthly'],
        help='특정 작업을 즉시 한 번 실행 (테스트용)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='로그 레벨 (기본값: INFO)'
    )

    args = parser.parse_args()

    # 로그 설정
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(
                log_dir / 'scheduler.log',
                encoding='utf-8'
            )
        ]
    )

    # 즉시 실행 모드
    if args.run_once:
        asyncio.run(run_once(args.run_once))
        return

    # 스케줄러 모드
    scheduler = DataCollectionScheduler()
    scheduler.start()
    scheduler.print_next_run_times()

    try:
        # 무한 대기 (스케줄러가 백그라운드에서 실행됨)
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.stop()


if __name__ == "__main__":
    main()
