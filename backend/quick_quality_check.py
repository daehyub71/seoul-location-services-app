#!/usr/bin/env python
"""Quick data quality check"""

from clients.supabase_client import get_supabase_client

def main():
    supabase = get_supabase_client()

    print('='*70)
    print('📊 데이터 품질 리포트 - Day 7')
    print('='*70)

    tables = [
        'cultural_events',
        'libraries',
        'cultural_spaces',
        'future_heritages',
        'public_reservations'
    ]

    total_records = 0
    total_with_coords = 0

    for table in tables:
        # 총 레코드 수
        count_result = supabase.table(table).select('*', count='exact').limit(0).execute()
        total = count_result.count

        # 좌표 있는 레코드 수
        if table == 'public_reservations':
            coords_result = supabase.table(table).select('*', count='exact').not_.is_('x_coord', 'null').not_.is_('y_coord', 'null').limit(0).execute()
        else:
            coords_result = supabase.table(table).select('*', count='exact').not_.is_('latitude', 'null').not_.is_('longitude', 'null').limit(0).execute()

        with_coords = coords_result.count
        percent = (with_coords / total * 100) if total > 0 else 0

        print(f'\n{table}:')
        print(f'  총 레코드: {total:,}')
        print(f'  좌표 보유: {with_coords:,} ({percent:.1f}%)')

        total_records += total
        total_with_coords += with_coords

    print('\n' + '='*70)
    print(f'전체 총계:')
    print(f'  총 레코드: {total_records:,}')
    print(f'  좌표 보유: {total_with_coords:,} ({total_with_coords/total_records*100:.1f}%)')
    print('='*70)

if __name__ == '__main__':
    main()
