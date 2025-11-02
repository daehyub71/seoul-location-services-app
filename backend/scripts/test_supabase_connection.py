"""
Supabase 연결 테스트 스크립트
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client, Client
import psycopg2
from psycopg2 import sql

# Load environment variables
load_dotenv()


def test_supabase_client():
    """Supabase Python 클라이언트 연결 테스트"""
    print("\n" + "="*60)
    print("1️⃣  Supabase Python Client 연결 테스트")
    print("="*60)

    try:
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')

        if not url or not key:
            print("❌ 환경변수가 설정되지 않았습니다!")
            print(f"   SUPABASE_URL: {url}")
            print(f"   SUPABASE_KEY: {'설정됨' if key else '없음'}")
            return False

        print(f"📍 Supabase URL: {url}")
        print(f"🔑 API Key: {key[:20]}...")

        # Create client
        supabase: Client = create_client(url, key)
        print("✅ Supabase 클라이언트 생성 성공!")

        # Test simple query (should work even with empty table)
        result = supabase.table('cultural_events').select('count', count='exact').execute()
        print(f"✅ 테이블 접근 성공! (cultural_events 레코드 수: {result.count})")

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {type(e).__name__}")
        print(f"   메시지: {str(e)}")
        return False


def test_postgresql_connection():
    """PostgreSQL 직접 연결 테스트"""
    print("\n" + "="*60)
    print("2️⃣  PostgreSQL 직접 연결 테스트")
    print("="*60)

    try:
        db_url = os.getenv('SUPABASE_DATABASE_URL')

        if not db_url:
            print("❌ SUPABASE_DATABASE_URL이 설정되지 않았습니다!")
            return False

        print(f"📍 Database URL: {db_url.split('@')[1] if '@' in db_url else 'hidden'}")

        # Connect to PostgreSQL
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        print("✅ PostgreSQL 연결 성공!")

        # Test PostGIS extension
        cursor.execute("SELECT PostGIS_version();")
        postgis_version = cursor.fetchone()
        print(f"✅ PostGIS 확장 활성화됨! (버전: {postgis_version[0]})")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {type(e).__name__}")
        print(f"   메시지: {str(e)}")
        return False


def test_tables_exist():
    """테이블 존재 여부 확인"""
    print("\n" + "="*60)
    print("3️⃣  데이터베이스 테이블 확인")
    print("="*60)

    try:
        db_url = os.getenv('SUPABASE_DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Expected tables
        expected_tables = [
            'cultural_events',
            'libraries',
            'cultural_spaces',
            'public_reservations',
            'future_heritages',
            'collection_logs'
        ]

        all_exist = True

        for table_name in expected_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name = %s
                );
            """, (table_name,))

            exists = cursor.fetchone()[0]

            if exists:
                # Get row count
                cursor.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(
                    sql.Identifier(table_name)
                ))
                count = cursor.fetchone()[0]
                print(f"✅ {table_name:<25} (레코드: {count}개)")
            else:
                print(f"❌ {table_name:<25} (존재하지 않음)")
                all_exist = False

        cursor.close()
        conn.close()

        return all_exist

    except Exception as e:
        print(f"❌ 오류 발생: {type(e).__name__}")
        print(f"   메시지: {str(e)}")
        return False


def test_spatial_functions():
    """PostGIS 공간 함수 테스트"""
    print("\n" + "="*60)
    print("4️⃣  PostGIS 공간 함수 테스트")
    print("="*60)

    try:
        db_url = os.getenv('SUPABASE_DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Test calculate_distance function
        print("📍 거리 계산 함수 테스트...")
        cursor.execute("""
            SELECT calculate_distance(
                37.5665::DECIMAL,  -- 서울시청 위도
                126.9780::DECIMAL, -- 서울시청 경도
                37.5511::DECIMAL,  -- 남산타워 위도
                126.9882::DECIMAL  -- 남산타워 경도
            );
        """)

        distance = cursor.fetchone()[0]
        print(f"✅ 거리 계산 성공! 서울시청 ↔ 남산타워: {distance:.2f}m")

        # Test spatial index
        print("\n📍 공간 인덱스 확인...")
        cursor.execute("""
            SELECT
                schemaname,
                tablename,
                indexname
            FROM pg_indexes
            WHERE indexname LIKE 'idx_%_location';
        """)

        indexes = cursor.fetchall()

        if indexes:
            print(f"✅ 공간 인덱스 {len(indexes)}개 발견:")
            for schema, table, index in indexes:
                print(f"   - {index} (테이블: {table})")
        else:
            print("⚠️  공간 인덱스가 없습니다. init_supabase_schema.sql을 실행해주세요.")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        print(f"❌ 오류 발생: {type(e).__name__}")
        print(f"   메시지: {str(e)}")
        return False


def test_triggers():
    """트리거 동작 테스트"""
    print("\n" + "="*60)
    print("5️⃣  자동 location 업데이트 트리거 테스트")
    print("="*60)

    try:
        db_url = os.getenv('SUPABASE_DATABASE_URL')
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()

        # Insert test record
        print("📍 테스트 레코드 삽입...")
        cursor.execute("""
            INSERT INTO cultural_events (
                api_id, title, lat, lot
            ) VALUES (
                'test_001',
                '테스트 문화행사',
                37.5665,  -- 서울시청 위도
                126.9780  -- 서울시청 경도
            )
            RETURNING id, location IS NOT NULL as has_location;
        """)

        result = cursor.fetchone()
        test_id = result[0]
        has_location = result[1]

        if has_location:
            print("✅ 트리거 동작 성공! location 필드가 자동으로 생성되었습니다.")

            # Verify location value
            cursor.execute("""
                SELECT ST_AsText(location::geometry)
                FROM cultural_events
                WHERE id = %s;
            """, (test_id,))

            location_text = cursor.fetchone()[0]
            print(f"   Location: {location_text}")
        else:
            print("❌ 트리거가 동작하지 않았습니다!")

        # Clean up test record
        cursor.execute("DELETE FROM cultural_events WHERE id = %s;", (test_id,))
        conn.commit()
        print("🧹 테스트 레코드 삭제 완료")

        cursor.close()
        conn.close()

        return has_location

    except Exception as e:
        print(f"❌ 오류 발생: {type(e).__name__}")
        print(f"   메시지: {str(e)}")

        # Rollback on error
        try:
            conn.rollback()
        except:
            pass

        return False


def print_summary(results):
    """테스트 결과 요약"""
    print("\n" + "="*60)
    print("📊 테스트 결과 요약")
    print("="*60)

    test_names = [
        "Supabase Client 연결",
        "PostgreSQL 직접 연결",
        "테이블 존재 확인",
        "PostGIS 공간 함수",
        "Location 트리거"
    ]

    total = len(results)
    passed = sum(results)

    for i, (name, result) in enumerate(zip(test_names, results), 1):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i}. {name:<30} {status}")

    print("\n" + "-"*60)
    print(f"총 {total}개 테스트 중 {passed}개 성공 ({passed/total*100:.1f}%)")
    print("-"*60)

    if passed == total:
        print("\n🎉 모든 테스트 통과! Supabase 설정이 완료되었습니다.")
        print("\n다음 단계:")
        print("1. Day 2 작업 계속 진행")
        print("2. 데이터 수집 스크립트 작성 (Day 3-5)")
        return True
    else:
        print("\n⚠️  일부 테스트가 실패했습니다.")
        print("\n문제 해결 방법:")
        if not results[0] or not results[1]:
            print("- .env 파일의 Supabase 정보를 다시 확인하세요")
        if not results[2]:
            print("- Supabase SQL Editor에서 init_supabase_schema.sql을 실행하세요")
        if not results[3]:
            print("- PostGIS 확장이 활성화되지 않았습니다")
        if not results[4]:
            print("- 트리거가 생성되지 않았습니다. SQL 스크립트를 다시 실행하세요")
        return False


def main():
    """메인 실행 함수"""
    print("\n" + "🚀"*30)
    print("Seoul Location Services - Supabase 연결 테스트")
    print("🚀"*30)

    # Run all tests
    results = [
        test_supabase_client(),
        test_postgresql_connection(),
        test_tables_exist(),
        test_spatial_functions(),
        test_triggers()
    ]

    # Print summary
    success = print_summary(results)

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
