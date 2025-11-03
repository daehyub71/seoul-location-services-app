"""
데이터베이스 인덱스 확인 및 최적화 제안 스크립트
Supabase PostgreSQL 인덱스 상태 확인
"""

import asyncio
from app.db.supabase_client import get_supabase_admin_client
from app.core.config import settings


TABLES = [
    'cultural_events',
    'libraries',
    'cultural_spaces',
    'future_heritages',
    'public_reservations'
]


async def check_table_indexes():
    """각 테이블의 인덱스 확인"""
    print("=" * 80)
    print("서울 위치 서비스 - 데이터베이스 인덱스 확인")
    print("=" * 80)
    print()

    supabase = get_supabase_admin_client()

    for table in TABLES:
        print(f"\n📊 테이블: {table}")
        print("-" * 80)

        try:
            # 테이블 데이터 샘플 조회
            response = supabase.table(table).select('*').limit(1).execute()

            if response.data and len(response.data) > 0:
                sample = response.data[0]

                # 좌표 필드 확인
                coord_fields = []
                if 'latitude' in sample and 'longitude' in sample:
                    coord_fields = ['latitude', 'longitude']
                elif 'lat' in sample and 'lot' in sample:
                    coord_fields = ['lat', 'lot']
                elif 'y_coord' in sample and 'x_coord' in sample:
                    coord_fields = ['y_coord', 'x_coord']

                print(f"✓ 좌표 필드: {coord_fields}")

                # 기타 주요 필드 확인
                important_fields = ['id', 'created_at', 'updated_at']
                existing_important = [f for f in important_fields if f in sample]
                print(f"✓ 주요 필드: {existing_important}")

                # 전체 필드 수
                print(f"✓ 전체 필드 수: {len(sample)} 개")

                # 권장 인덱스
                print("\n📝 권장 인덱스:")
                if coord_fields:
                    print(f"   1. CREATE INDEX idx_{table}_coords ON {table} ({coord_fields[0]}, {coord_fields[1]});")
                    print(f"      → 위치 기반 검색 최적화 (ORDER BY distance)")

                if 'id' in sample:
                    print(f"   2. CREATE INDEX idx_{table}_id ON {table} (id);")
                    print(f"      → 상세 조회 최적화 (Primary Key일 경우 자동 생성)")

                if 'created_at' in sample:
                    print(f"   3. CREATE INDEX idx_{table}_created_at ON {table} (created_at DESC);")
                    print(f"      → 최신순 정렬 최적화")

                # 카테고리별 특화 인덱스
                if table == 'cultural_events' and 'start_date' in sample:
                    print(f"   4. CREATE INDEX idx_{table}_start_date ON {table} (start_date);")
                    print(f"      → 날짜 필터링 최적화")

                if table == 'libraries' and 'library_name' in sample:
                    print(f"   4. CREATE INDEX idx_{table}_name ON {table} (library_name);")
                    print(f"      → 이름 검색 최적화")

            else:
                print(f"⚠️  데이터 없음 - 스킵")

        except Exception as e:
            print(f"❌ 에러: {e}")

    print("\n" + "=" * 80)
    print("인덱스 확인 완료")
    print("=" * 80)


async def check_query_performance():
    """주요 쿼리 성능 테스트"""
    print("\n\n" + "=" * 80)
    print("주요 쿼리 성능 테스트")
    print("=" * 80)

    import time
    supabase = get_supabase_admin_client()

    test_cases = [
        {
            'name': '도서관 전체 조회',
            'table': 'libraries',
            'query': lambda: supabase.table('libraries').select('*').execute()
        },
        {
            'name': '도서관 10개 조회',
            'table': 'libraries',
            'query': lambda: supabase.table('libraries').select('*').limit(10).execute()
        },
        {
            'name': '문화행사 전체 조회',
            'table': 'cultural_events',
            'query': lambda: supabase.table('cultural_events').select('*').execute()
        },
        {
            'name': 'ID로 도서관 조회',
            'table': 'libraries',
            'query': lambda: supabase.table('libraries').select('*').eq('id', '1').execute()
        }
    ]

    for test in test_cases:
        try:
            start = time.time()
            response = test['query']()
            elapsed = (time.time() - start) * 1000  # ms

            count = len(response.data) if response.data else 0

            # 성능 평가
            if elapsed < 50:
                status = "🟢 매우 빠름"
            elif elapsed < 100:
                status = "🟡 양호"
            elif elapsed < 200:
                status = "🟠 보통"
            else:
                status = "🔴 느림"

            print(f"\n{test['name']}")
            print(f"  - 응답 시간: {elapsed:.2f}ms {status}")
            print(f"  - 결과 수: {count}개")

        except Exception as e:
            print(f"\n{test['name']}")
            print(f"  - ❌ 에러: {e}")

    print("\n" + "=" * 80)
    print("성능 테스트 완료")
    print("=" * 80)


async def generate_index_sql():
    """인덱스 생성 SQL 스크립트 생성"""
    print("\n\n" + "=" * 80)
    print("인덱스 생성 SQL 스크립트")
    print("=" * 80)
    print()
    print("-- 다음 SQL을 Supabase SQL Editor에서 실행하세요")
    print("-- https://supabase.com/dashboard/project/[PROJECT_ID]/sql")
    print()

    sql_statements = []

    # 공통 인덱스
    for table in TABLES:
        # 좌표 인덱스
        if table == 'cultural_events':
            sql_statements.append(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_coords ON {table} (lat, lot);"
            )
        elif table == 'public_reservations':
            sql_statements.append(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_coords ON {table} (y_coord, x_coord);"
            )
        else:
            sql_statements.append(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_coords ON {table} (latitude, longitude);"
            )

        # created_at 인덱스
        sql_statements.append(
            f"CREATE INDEX IF NOT EXISTS idx_{table}_created_at ON {table} (created_at DESC);"
        )

    # 특화 인덱스
    sql_statements.append(
        "CREATE INDEX IF NOT EXISTS idx_cultural_events_start_date ON cultural_events (start_date);"
    )
    sql_statements.append(
        "CREATE INDEX IF NOT EXISTS idx_libraries_name ON libraries (library_name);"
    )

    # 출력
    for i, sql in enumerate(sql_statements, 1):
        print(f"{i}. {sql}")

    print()
    print("=" * 80)

    # 파일로 저장
    output_file = "scripts/create_indexes.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- Seoul Location Services - Database Indexes\n")
        f.write("-- 생성일: 2025-11-15\n")
        f.write("-- 용도: 공간 검색 및 정렬 성능 최적화\n\n")
        for sql in sql_statements:
            f.write(sql + "\n")

    print(f"✅ SQL 스크립트 저장: {output_file}")
    print("=" * 80)


async def main():
    """메인 실행 함수"""
    print("\n🚀 데이터베이스 최적화 분석 시작\n")

    await check_table_indexes()
    await check_query_performance()
    await generate_index_sql()

    print("\n✅ 모든 분석 완료!\n")


if __name__ == '__main__':
    asyncio.run(main())
