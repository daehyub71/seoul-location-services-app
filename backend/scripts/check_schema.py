"""
Supabase 테이블 스키마 확인 스크립트
각 테이블의 컬럼명과 타입을 조회
"""

import os
import sys
from pathlib import Path
from supabase import create_client

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_table_schema(supabase, table_name):
    """테이블의 첫 번째 레코드를 조회하여 스키마 확인"""
    print(f"\n{'='*70}")
    print(f"테이블: {table_name}")
    print('='*70)

    try:
        # 첫 번째 레코드 조회 (없으면 빈 결과)
        response = supabase.table(table_name).select("*").limit(1).execute()

        if response.data and len(response.data) > 0:
            # 데이터가 있으면 컬럼명 출력
            record = response.data[0]
            print(f"✅ 레코드 수: {len(response.data)}")
            print(f"\n컬럼 목록 ({len(record.keys())}개):")
            for i, key in enumerate(sorted(record.keys()), 1):
                value = record[key]
                value_type = type(value).__name__
                value_preview = str(value)[:50] if value is not None else "NULL"
                print(f"  {i:2d}. {key:<30} [{value_type:<10}] = {value_preview}")
        else:
            # 데이터가 없으면 INSERT 시도하여 에러 메시지로 컬럼 파악
            print("⚠️  레코드 없음 - 빈 INSERT로 스키마 확인")
            try:
                supabase.table(table_name).insert({}).execute()
            except Exception as e:
                error_msg = str(e)
                print(f"\n에러 메시지 (스키마 힌트):")
                print(f"  {error_msg}")

                # 테이블 정보 조회 (RPC 사용)
                # Note: Supabase Python Client는 정보 스키마 직접 조회 불가
                print(f"\n⚠️  데이터 삽입을 통해 컬럼명을 확인해야 합니다.")

    except Exception as e:
        print(f"❌ 에러: {e}")


def main():
    """메인 함수"""
    # Supabase 클라이언트 생성
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다.")
        print("   backend/.env 파일을 확인하세요.")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)

    print("\n" + "="*70)
    print("Supabase 테이블 스키마 확인")
    print("="*70)
    print(f"URL: {supabase_url}")
    print("="*70)

    # 확인할 테이블 목록
    tables = [
        'cultural_events',
        'libraries',
        'cultural_spaces',
        'public_reservations',
        'future_heritages',
        'collection_logs'
    ]

    for table in tables:
        check_table_schema(supabase, table)

    print("\n" + "="*70)
    print("스키마 확인 완료")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
