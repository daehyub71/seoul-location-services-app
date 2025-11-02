"""
Seoul API 샘플 데이터 수집 스크립트
전체 9개 엔드포인트에서 소량의 샘플 데이터 수집
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from collectors.seoul_api_client import SeoulAPIClient
from app.utils.coordinate_transform import CoordinateTransformer

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


async def collect_endpoint_sample(
    client: SeoulAPIClient,
    endpoint_key: str,
    max_records: int = 10
) -> Dict:
    """
    특정 엔드포인트에서 샘플 데이터 수집

    Args:
        client: SeoulAPIClient 인스턴스
        endpoint_key: 엔드포인트 키 (예: 'cultural_events')
        max_records: 최대 수집 레코드 수

    Returns:
        {
            'endpoint_key': str,
            'endpoint_name': str,
            'total_count': int,
            'sample_count': int,
            'records': List[Dict],
            'collected_at': str
        }
    """
    endpoint_name = client.get_endpoint_name(endpoint_key)

    if not endpoint_name:
        logger.error(f"Unknown endpoint key: {endpoint_key}")
        return None

    try:
        logger.info(f"🔍 Collecting from {endpoint_key} ({endpoint_name})...")

        # 총 레코드 수 조회
        total_count = await client.get_total_count(endpoint_name)
        logger.info(f"   Total records: {total_count:,}")

        # 샘플 데이터 수집
        records = await client.fetch_all(endpoint_name, max_records=max_records)
        logger.info(f"   Collected: {len(records)} records")

        return {
            'endpoint_key': endpoint_key,
            'endpoint_name': endpoint_name,
            'total_count': total_count,
            'sample_count': len(records),
            'records': records,
            'collected_at': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Error collecting {endpoint_key}: {e}")
        return {
            'endpoint_key': endpoint_key,
            'endpoint_name': endpoint_name,
            'total_count': 0,
            'sample_count': 0,
            'records': [],
            'error': str(e),
            'collected_at': datetime.now().isoformat()
        }


def analyze_coordinates(records: List[Dict]) -> Dict:
    """
    레코드의 좌표 데이터 분석

    Args:
        records: 레코드 리스트

    Returns:
        좌표 통계 정보
    """
    transformer = CoordinateTransformer()

    total = len(records)
    with_coords = 0
    valid_coords = 0
    in_seoul = 0

    coord_fields = [
        ('LAT', 'LOT'),  # 대부분의 API
        ('lat', 'lot'),  # 소문자
        ('XCNTS', 'YDNTS'),  # 일부 예약 API
        ('X', 'Y'),  # 기타
    ]

    for record in records:
        # 좌표 필드 찾기
        lat, lon = None, None

        for lat_field, lon_field in coord_fields:
            if lat_field in record and lon_field in record:
                try:
                    lat = float(record[lat_field])
                    lon = float(record[lon_field])
                    with_coords += 1
                    break
                except (ValueError, TypeError):
                    continue

        if lat and lon:
            # 유효성 검증
            if transformer.validate_wgs84(lat, lon):
                valid_coords += 1

                # 서울시 범위 확인
                if transformer.is_in_seoul(lat, lon):
                    in_seoul += 1

    return {
        'total_records': total,
        'with_coordinates': with_coords,
        'valid_coordinates': valid_coords,
        'in_seoul': in_seoul,
        'coverage_rate': f"{with_coords/total*100:.1f}%" if total > 0 else "0%",
        'seoul_rate': f"{in_seoul/with_coords*100:.1f}%" if with_coords > 0 else "0%"
    }


async def collect_all_samples(max_records_per_endpoint: int = 10):
    """
    모든 엔드포인트에서 샘플 데이터 수집

    Args:
        max_records_per_endpoint: 엔드포인트당 최대 레코드 수
    """
    api_key = os.getenv('SEOUL_API_KEY')

    if not api_key:
        logger.error("❌ SEOUL_API_KEY not found in .env")
        return

    # 출력 디렉토리 생성
    output_dir = Path(__file__).parent.parent / 'data' / 'samples'
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n" + "="*70)
    print("Seoul API 샘플 데이터 수집")
    print("="*70)
    print(f"출력 디렉토리: {output_dir}")
    print(f"엔드포인트당 최대 레코드: {max_records_per_endpoint}")
    print("="*70 + "\n")

    async with SeoulAPIClient(api_key) as client:
        endpoints = client.list_endpoints()

        print(f"📊 총 {len(endpoints)}개 엔드포인트:\n")
        for key, name in endpoints.items():
            print(f"   - {key}: {name}")
        print()

        # 모든 엔드포인트에서 데이터 수집
        results = []

        for i, endpoint_key in enumerate(endpoints.keys(), 1):
            print(f"\n[{i}/{len(endpoints)}] {endpoint_key}")
            print("-" * 70)

            result = await collect_endpoint_sample(
                client,
                endpoint_key,
                max_records=max_records_per_endpoint
            )

            if result:
                results.append(result)

                # 개별 파일 저장
                output_file = output_dir / f"{endpoint_key}_sample.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)

                logger.info(f"   ✅ Saved to {output_file.name}")

                # 좌표 분석
                if result['sample_count'] > 0:
                    coord_stats = analyze_coordinates(result['records'])
                    print(f"   📍 좌표 통계:")
                    print(f"      - 좌표 포함: {coord_stats['with_coordinates']}/{coord_stats['total_records']} ({coord_stats['coverage_rate']})")
                    print(f"      - 유효 좌표: {coord_stats['valid_coordinates']}/{coord_stats['with_coordinates']}")
                    print(f"      - 서울시 내: {coord_stats['in_seoul']}/{coord_stats['with_coordinates']} ({coord_stats['seoul_rate']})")

            # Rate limiting 방지
            await asyncio.sleep(1)

        # 전체 결과 요약 저장
        summary = {
            'collected_at': datetime.now().isoformat(),
            'total_endpoints': len(endpoints),
            'successful': sum(1 for r in results if r.get('sample_count', 0) > 0),
            'failed': sum(1 for r in results if r.get('error')),
            'total_records': sum(r.get('sample_count', 0) for r in results),
            'endpoints': [
                {
                    'key': r['endpoint_key'],
                    'name': r['endpoint_name'],
                    'total_count': r['total_count'],
                    'sample_count': r['sample_count'],
                    'has_error': 'error' in r
                }
                for r in results
            ]
        }

        summary_file = output_dir / 'collection_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        # 최종 요약 출력
        print("\n" + "="*70)
        print("📊 수집 결과 요약")
        print("="*70)
        print(f"총 엔드포인트: {summary['total_endpoints']}")
        print(f"성공: {summary['successful']}")
        print(f"실패: {summary['failed']}")
        print(f"총 수집 레코드: {summary['total_records']:,}")
        print(f"\n요약 파일: {summary_file}")
        print("="*70 + "\n")

        # 상세 테이블 출력
        print("\n엔드포인트별 상세:")
        print("-" * 70)
        print(f"{'엔드포인트':<30} {'전체 레코드':>15} {'샘플':>10} {'상태':>10}")
        print("-" * 70)

        for endpoint in summary['endpoints']:
            status = "❌ 실패" if endpoint['has_error'] else "✅ 성공"
            print(f"{endpoint['key']:<30} {endpoint['total_count']:>15,} {endpoint['sample_count']:>10} {status:>10}")

        print("-" * 70)

        return summary


async def main():
    """메인 실행 함수"""
    import argparse

    parser = argparse.ArgumentParser(description='Seoul API 샘플 데이터 수집')
    parser.add_argument(
        '--max-records',
        type=int,
        default=10,
        help='엔드포인트당 최대 레코드 수 (기본값: 10)'
    )
    parser.add_argument(
        '--endpoint',
        type=str,
        help='특정 엔드포인트만 수집 (예: cultural_events)'
    )

    args = parser.parse_args()

    if args.endpoint:
        # 특정 엔드포인트만 수집
        api_key = os.getenv('SEOUL_API_KEY')
        async with SeoulAPIClient(api_key) as client:
            result = await collect_endpoint_sample(
                client,
                args.endpoint,
                max_records=args.max_records
            )
            if result:
                print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 전체 수집
        await collect_all_samples(max_records_per_endpoint=args.max_records)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    asyncio.run(main())
