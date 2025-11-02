"""
Supabase 테이블 컬럼명 확인 (테스트 데이터 삽입 후 조회)
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


def get_columns_for_cultural_events(supabase):
    """Cultural Events 테이블 컬럼명 확인"""
    table = 'cultural_events'
    print(f"\n{'='*70}")
    print(f"테이블: {table}")
    print('='*70)

    # 테스트 데이터
    test_data = {
        'api_id': 'test_001',
        'title': '테스트 행사',
        'codename': '테스트',
        'guname': '강남구',
        'place': '테스트 장소',
        'org_name': '주최기관',
        'use_trgt': '일반',
        'use_fee': '무료',
        'player': '출연자',
        'program': '프로그램',
        'etc_desc': '비고',
        'org_link': 'http://test.com',
        'main_img': 'http://test.com/img.jpg',
        'start_date': '2025-11-02',
        'end_date': '2025-11-03',
        'themecode': 'TEST',
        'lat': 37.5,
        'lot': 127.0,
        'is_free': True,
        'hmpg_addr': 'http://homepage.com'
    }

    try:
        # 삽입
        response = supabase.table(table).insert(test_data).execute()
        if response.data:
            print("✅ 테스트 데이터 삽입 성공")
            record = response.data[0]
            print(f"\n컬럼 목록 ({len(record.keys())}개):")
            for i, key in enumerate(sorted(record.keys()), 1):
                print(f"  {i:2d}. {key}")

            # 삭제
            supabase.table(table).delete().eq('api_id', 'test_001').execute()
            print("\n✅ 테스트 데이터 삭제 완료")
    except Exception as e:
        print(f"❌ 에러: {e}")


def get_columns_for_libraries(supabase):
    """Libraries 테이블 컬럼명 확인"""
    table = 'libraries'
    print(f"\n{'='*70}")
    print(f"테이블: {table}")
    print('='*70)

    test_data = {
        'api_id': 'test_lib_001',
        'library_name': '테스트 도서관',
        'library_type': 'public',
        'address': '서울시 강남구',
        'phone': '02-1234-5678',
        'homepage': 'http://test.com',
        'closed_days': '월요일',
        'operating_hours': '09:00-18:00',
        'latitude': 37.5,
        'longitude': 127.0,
        'facilities': '열람실',
        'book_count': 10000,
        'seat_count': 100
    }

    try:
        response = supabase.table(table).insert(test_data).execute()
        if response.data:
            print("✅ 테스트 데이터 삽입 성공")
            record = response.data[0]
            print(f"\n컬럼 목록 ({len(record.keys())}개):")
            for i, key in enumerate(sorted(record.keys()), 1):
                print(f"  {i:2d}. {key}")

            supabase.table(table).delete().eq('api_id', 'test_lib_001').execute()
            print("\n✅ 테스트 데이터 삭제 완료")
    except Exception as e:
        print(f"❌ 에러: {e}")


def get_columns_for_cultural_spaces(supabase):
    """Cultural Spaces 테이블 컬럼명 확인"""
    table = 'cultural_spaces'
    print(f"\n{'='*70}")
    print(f"테이블: {table}")
    print('='*70)

    test_data = {
        'api_id': 'test_space_001',
        'fac_name': '테스트 문화공간',
        'subjcode': '문화',
        'codename': '박물관',
        'addr': '서울시 강남구',
        'tel_no': '02-1234-5678',
        'homepage': 'http://test.com',
        'restde_guid_cn': '휴관일',
        'oper_time': '09:00-18:00',
        'entrn_fee_info': '무료',
        'main_img_url': 'http://test.com/img.jpg',
        'lat': 37.5,
        'lot': 127.0,
        'is_free': True,
        'rsrv_link': 'http://reservation.com'
    }

    try:
        response = supabase.table(table).insert(test_data).execute()
        if response.data:
            print("✅ 테스트 데이터 삽입 성공")
            record = response.data[0]
            print(f"\n컬럼 목록 ({len(record.keys())}개):")
            for i, key in enumerate(sorted(record.keys()), 1):
                print(f"  {i:2d}. {key}")

            supabase.table(table).delete().eq('api_id', 'test_space_001').execute()
            print("\n✅ 테스트 데이터 삭제 완료")
    except Exception as e:
        print(f"❌ 에러: {e}")


def get_columns_for_future_heritages(supabase):
    """Future Heritages 테이블 컬럼명 확인"""
    table = 'future_heritages'
    print(f"\n{'='*70}")
    print(f"테이블: {table}")
    print('='*70)

    test_data = {
        'api_id': 'test_heritage_001',
        'name': '테스트 미래유산',
        'category': '건축물',
        'era': '근대',
        'address': '서울시 강남구',
        'content': '설명',
        'main_purpose': '주요용도',
        'registered_at': '2025-11-02',
        'main_image': 'http://test.com/img.jpg',
        'lat': 37.5,
        'lot': 127.0
    }

    try:
        response = supabase.table(table).insert(test_data).execute()
        if response.data:
            print("✅ 테스트 데이터 삽입 성공")
            record = response.data[0]
            print(f"\n컬럼 목록 ({len(record.keys())}개):")
            for i, key in enumerate(sorted(record.keys()), 1):
                print(f"  {i:2d}. {key}")

            supabase.table(table).delete().eq('api_id', 'test_heritage_001').execute()
            print("\n✅ 테스트 데이터 삭제 완료")
    except Exception as e:
        print(f"❌ 에러: {e}")


def get_columns_for_public_reservations(supabase):
    """Public Reservations 테이블 컬럼명 확인"""
    table = 'public_reservations'
    print(f"\n{'='*70}")
    print(f"테이블: {table}")
    print('='*70)

    test_data = {
        'api_id': 'test_reservation_001',
        'service_name': '테스트 예약',
        'category': 'medical',
        'place_name': '테스트 장소',
        'payment_method': '무료',
        'reception_start': '2025-11-02',
        'reception_end': '2025-11-03',
        'service_start': '2025-11-04',
        'service_end': '2025-11-05',
        'district': '강남구',
        'description': '설명',
        'phone': '02-1234-5678',
        'max_capacity': 20,
        'min_capacity': 5,
        'reservation_deadline': '1일 전',
        'image_url': 'http://test.com/img.jpg',
        'lat': 37.5,
        'lot': 127.0,
        'service_url': 'http://service.com',
        'service_status': 'active',
        'target_audience': '일반',
        'cost_info': '무료',
        'notice': '공지사항',
        'operation_hours': '09:00-18:00',
        'facilities': '주차',
        'reservation_url': 'http://reservation.com'
    }

    try:
        response = supabase.table(table).insert(test_data).execute()
        if response.data:
            print("✅ 테스트 데이터 삽입 성공")
            record = response.data[0]
            print(f"\n컬럼 목록 ({len(record.keys())}개):")
            for i, key in enumerate(sorted(record.keys()), 1):
                print(f"  {i:2d}. {key}")

            supabase.table(table).delete().eq('api_id', 'test_reservation_001').execute()
            print("\n✅ 테스트 데이터 삭제 완료")
    except Exception as e:
        print(f"❌ 에러: {e}")


def main():
    """메인 함수"""
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ SUPABASE_URL 또는 SUPABASE_KEY가 설정되지 않았습니다.")
        sys.exit(1)

    supabase = create_client(supabase_url, supabase_key)

    print("\n" + "="*70)
    print("Supabase 테이블 컬럼 확인 (테스트 데이터 삽입)")
    print("="*70)

    get_columns_for_cultural_events(supabase)
    get_columns_for_libraries(supabase)
    get_columns_for_cultural_spaces(supabase)
    get_columns_for_future_heritages(supabase)
    get_columns_for_public_reservations(supabase)

    print("\n" + "="*70)
    print("컬럼 확인 완료")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
