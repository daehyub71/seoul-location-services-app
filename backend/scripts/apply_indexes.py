#!/usr/bin/env python3
"""
Supabase 데이터베이스 인덱스 생성 스크립트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from supabase import create_client, Client

# .env 파일 로드
load_dotenv()


def create_indexes():
    """데이터베이스 인덱스 생성"""

    # Supabase 클라이언트 생성
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL 또는 SUPABASE_KEY가 .env 파일에 없습니다.")
        sys.exit(1)

    print(f"📡 Connecting to Supabase: {supabase_url}")
    supabase: Client = create_client(supabase_url, supabase_key)

    # 인덱스 생성 SQL 목록
    index_queries = [
        # Cultural Events
        "CREATE INDEX IF NOT EXISTS idx_cultural_events_coords ON cultural_events (lat, lot);",
        "CREATE INDEX IF NOT EXISTS idx_cultural_events_created_at ON cultural_events (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_cultural_events_start_date ON cultural_events (start_date);",

        # Libraries
        "CREATE INDEX IF NOT EXISTS idx_libraries_coords ON libraries (latitude, longitude);",
        "CREATE INDEX IF NOT EXISTS idx_libraries_created_at ON libraries (created_at DESC);",
        "CREATE INDEX IF NOT EXISTS idx_libraries_name ON libraries (library_name);",

        # Cultural Spaces
        "CREATE INDEX IF NOT EXISTS idx_cultural_spaces_coords ON cultural_spaces (latitude, longitude);",
        "CREATE INDEX IF NOT EXISTS idx_cultural_spaces_created_at ON cultural_spaces (created_at DESC);",

        # Future Heritages
        "CREATE INDEX IF NOT EXISTS idx_future_heritages_coords ON future_heritages (latitude, longitude);",
        "CREATE INDEX IF NOT EXISTS idx_future_heritages_created_at ON future_heritages (created_at DESC);",

        # Public Reservations
        "CREATE INDEX IF NOT EXISTS idx_public_reservations_coords ON public_reservations (y_coord, x_coord);",
        "CREATE INDEX IF NOT EXISTS idx_public_reservations_created_at ON public_reservations (created_at DESC);",
    ]

    print(f"\n🔧 Creating {len(index_queries)} indexes...\n")

    success_count = 0
    error_count = 0

    for i, query in enumerate(index_queries, 1):
        # 인덱스 이름 추출
        index_name = query.split("idx_")[1].split(" ")[0] if "idx_" in query else f"index_{i}"

        try:
            # Supabase REST API를 통해 SQL 실행
            # Note: Supabase Python 클라이언트는 직접 SQL 실행을 지원하지 않으므로
            # postgrest API를 사용하거나 RPC 함수를 사용해야 합니다.

            print(f"[{i}/{len(index_queries)}] Creating idx_{index_name}...", end=" ")

            # RPC를 통해 SQL 실행 (Supabase에 exec_sql 함수가 있다고 가정)
            # 없다면 아래 대안 사용
            try:
                result = supabase.rpc('exec_sql', {'sql': query}).execute()
                print("✅ Success")
                success_count += 1
            except Exception as e:
                if "does not exist" in str(e):
                    print("⚠️  RPC function not available - manual creation needed")
                    print(f"   SQL: {query}")
                    error_count += 1
                else:
                    raise

        except Exception as e:
            print(f"❌ Error: {e}")
            error_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Success: {success_count}/{len(index_queries)}")
    print(f"❌ Errors: {error_count}/{len(index_queries)}")
    print(f"{'='*60}\n")

    if error_count > 0:
        print("⚠️  일부 인덱스 생성 실패")
        print("\n수동으로 Supabase SQL Editor에서 실행해주세요:")
        print("https://supabase.com/dashboard/project/xptueenuumxhmhkantdl/sql/new\n")
        print("SQL 파일 위치:")
        print("  scripts/create_indexes.sql\n")
        return False

    return True


if __name__ == "__main__":
    print("="*60)
    print("Seoul Location Services - Database Index Creation")
    print("="*60)

    try:
        success = create_indexes()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
