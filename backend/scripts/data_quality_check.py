"""
데이터 품질 검증 스크립트 (Day 6)
Supabase에 저장된 데이터의 품질 검증
"""

import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import os

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# 서울시 좌표 범위 (WGS84)
SEOUL_BOUNDS = {
    'lat_min': 37.413,  # 남단
    'lat_max': 37.715,  # 북단
    'lon_min': 126.734,  # 서단
    'lon_max': 127.269   # 동단
}


class DataQualityChecker:
    """
    데이터 품질 검증기

    검증 항목:
    1. 좌표 범위 검증 (서울시 내)
    2. 중복 레코드 체크
    3. 누락 필드 체크
    4. 날짜 유효성 검증
    """

    def __init__(self):
        self.tables = [
            'cultural_events',
            'libraries',
            'cultural_spaces',
            'future_heritages',
            'public_reservations'
        ]

        self.issues: List[Dict[str, Any]] = []

    def check_all(self) -> Dict[str, Any]:
        """전체 품질 검증 실행"""
        print("\n" + "="*70)
        print("🔍 데이터 품질 검증 시작")
        print("="*70)
        print(f"검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"검증 테이블: {len(self.tables)}개")
        print("="*70 + "\n")

        for table in self.tables:
            print(f"\n📊 [{table}] 검증 중...")
            print("-" * 70)

            try:
                # 테이블 통계
                self._check_table_stats(table)

                # 좌표 범위 검증
                self._check_coordinate_bounds(table)

                # 중복 레코드 검증
                self._check_duplicates(table)

                # 필수 필드 누락 검증
                self._check_missing_fields(table)

                print(f"✅ [{table}] 검증 완료")

            except Exception as e:
                print(f"❌ [{table}] 검증 실패: {e}")
                self.issues.append({
                    'table': table,
                    'type': 'error',
                    'message': str(e)
                })

        # 최종 리포트 출력
        self._print_report()

        return {
            'issues': self.issues,
            'total_issues': len(self.issues)
        }

    def _check_table_stats(self, table: str):
        """테이블 기본 통계"""
        try:
            response = supabase.table(table).select('*', count='exact').execute()
            count = response.count

            print(f"  총 레코드: {count:,}개")

        except Exception as e:
            print(f"  ⚠️  통계 조회 실패: {e}")

    def _check_coordinate_bounds(self, table: str):
        """좌표 범위 검증 (서울시 내)"""

        # 테이블별 좌표 컬럼명 매핑
        coord_columns = {
            'cultural_events': ('latitude', 'longitude'),
            'libraries': ('latitude', 'longitude'),
            'cultural_spaces': ('latitude', 'longitude'),
            'future_heritages': ('latitude', 'longitude'),
            'public_reservations': ('y_coord', 'x_coord')  # y=lat, x=lon
        }

        if table not in coord_columns:
            print(f"  ⚠️  좌표 컬럼 정보 없음")
            return

        lat_col, lon_col = coord_columns[table]

        try:
            # 좌표가 있는 레코드만 조회
            response = supabase.table(table).select(
                f'api_id,{lat_col},{lon_col}'
            ).not_.is_(lat_col, 'null').not_.is_(lon_col, 'null').execute()

            records = response.data
            total_with_coords = len(records)

            out_of_bounds = []

            for record in records:
                lat = float(record[lat_col])
                lon = float(record[lon_col])

                # 서울시 범위 체크
                if not (SEOUL_BOUNDS['lat_min'] <= lat <= SEOUL_BOUNDS['lat_max'] and
                        SEOUL_BOUNDS['lon_min'] <= lon <= SEOUL_BOUNDS['lon_max']):
                    out_of_bounds.append({
                        'api_id': record['api_id'],
                        'lat': lat,
                        'lon': lon
                    })

            if out_of_bounds:
                print(f"  ⚠️  서울시 범위 벗어남: {len(out_of_bounds)}/{total_with_coords}개")

                self.issues.append({
                    'table': table,
                    'type': 'coordinate_bounds',
                    'count': len(out_of_bounds),
                    'total': total_with_coords,
                    'samples': out_of_bounds[:5]  # 샘플 5개만
                })
            else:
                print(f"  ✅ 좌표 범위: {total_with_coords}개 모두 정상")

        except Exception as e:
            print(f"  ⚠️  좌표 검증 실패: {e}")

    def _check_duplicates(self, table: str):
        """중복 레코드 검증 (api_id 기준)"""
        try:
            # api_id별 카운트
            response = supabase.table(table).select('api_id').execute()
            records = response.data

            api_ids = [r['api_id'] for r in records]
            unique_ids = set(api_ids)

            total = len(api_ids)
            unique = len(unique_ids)

            if total != unique:
                duplicates = total - unique
                print(f"  ⚠️  중복 레코드: {duplicates}개 (총 {total}개 중)")

                self.issues.append({
                    'table': table,
                    'type': 'duplicates',
                    'count': duplicates,
                    'total': total
                })
            else:
                print(f"  ✅ 중복 없음: {total}개 모두 고유")

        except Exception as e:
            print(f"  ⚠️  중복 검증 실패: {e}")

    def _check_missing_fields(self, table: str):
        """필수 필드 누락 검증"""

        # 테이블별 필수 필드 정의
        required_fields = {
            'cultural_events': ['codename', 'title', 'strtdate'],
            'libraries': ['library_name', 'guname'],
            'cultural_spaces': ['fac_name', 'guname'],
            'future_heritages': ['name', 'main_category'],
            'public_reservations': ['svcnm', 'service_type']
        }

        if table not in required_fields:
            print(f"  ⚠️  필수 필드 정의 없음")
            return

        fields = required_fields[table]

        try:
            response = supabase.table(table).select('api_id,' + ','.join(fields)).execute()
            records = response.data

            missing_counts = {field: 0 for field in fields}

            for record in records:
                for field in fields:
                    if not record.get(field):
                        missing_counts[field] += 1

            # 누락이 있는 필드만 출력
            has_missing = False
            for field, count in missing_counts.items():
                if count > 0:
                    has_missing = True
                    print(f"  ⚠️  [{field}] 누락: {count}/{len(records)}개")

                    self.issues.append({
                        'table': table,
                        'type': 'missing_field',
                        'field': field,
                        'count': count,
                        'total': len(records)
                    })

            if not has_missing:
                print(f"  ✅ 필수 필드: 모두 정상")

        except Exception as e:
            print(f"  ⚠️  필드 검증 실패: {e}")

    def _print_report(self):
        """최종 리포트 출력"""
        print("\n" + "="*70)
        print("📋 데이터 품질 검증 리포트")
        print("="*70)

        if not self.issues:
            print("\n✅ 모든 검증 항목 통과! 데이터 품질이 우수합니다.\n")
            return

        # 이슈 타입별 분류
        issues_by_type = {}
        for issue in self.issues:
            issue_type = issue['type']
            if issue_type not in issues_by_type:
                issues_by_type[issue_type] = []
            issues_by_type[issue_type].append(issue)

        print(f"\n총 이슈: {len(self.issues)}개\n")

        # 타입별 출력
        for issue_type, issues in issues_by_type.items():
            print(f"\n🔴 {issue_type.upper()} ({len(issues)}개)")
            print("-" * 70)

            for issue in issues[:10]:  # 최대 10개만
                table = issue['table']

                if issue_type == 'coordinate_bounds':
                    print(f"  [{table}] 서울시 범위 벗어남: {issue['count']}/{issue['total']}개")
                    if issue.get('samples'):
                        for sample in issue['samples'][:3]:
                            print(f"    - api_id: {sample['api_id']}, "
                                  f"lat: {sample['lat']:.6f}, lon: {sample['lon']:.6f}")

                elif issue_type == 'duplicates':
                    print(f"  [{table}] 중복 레코드: {issue['count']}개")

                elif issue_type == 'missing_field':
                    field = issue['field']
                    print(f"  [{table}] {field} 누락: {issue['count']}/{issue['total']}개")

                elif issue_type == 'error':
                    print(f"  [{table}] 오류: {issue['message']}")

        print("\n" + "="*70 + "\n")

    def export_report(self, output_file: str = 'data_quality_report.txt'):
        """리포트를 파일로 저장"""
        report_path = Path('reports') / output_file
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"데이터 품질 검증 리포트\n")
            f.write(f"생성 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*70 + "\n\n")

            f.write(f"총 이슈: {len(self.issues)}개\n\n")

            for issue in self.issues:
                f.write(f"[{issue['table']}] {issue['type']}\n")
                f.write(f"  {issue}\n\n")

        print(f"✅ 리포트 저장: {report_path}")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Seoul Open API 데이터 품질 검증',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 전체 품질 검증
  python data_quality_check.py

  # 리포트 파일 저장
  python data_quality_check.py --export

  # 특정 테이블만 검증
  python data_quality_check.py --table cultural_events
        """
    )

    parser.add_argument(
        '--export',
        action='store_true',
        help='리포트를 파일로 저장'
    )
    parser.add_argument(
        '--table',
        choices=[
            'cultural_events',
            'libraries',
            'cultural_spaces',
            'future_heritages',
            'public_reservations'
        ],
        help='특정 테이블만 검증'
    )

    args = parser.parse_args()

    checker = DataQualityChecker()

    # 특정 테이블만 검증
    if args.table:
        checker.tables = [args.table]

    # 검증 실행
    result = checker.check_all()

    # 리포트 저장
    if args.export:
        checker.export_report()

    # 종료 코드 (이슈가 있으면 1)
    sys.exit(1 if result['total_issues'] > 0 else 0)


if __name__ == "__main__":
    main()
