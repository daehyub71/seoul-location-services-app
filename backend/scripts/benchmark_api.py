"""
API 응답 속도 벤치마크 스크립트
캐시 히트/미스 시나리오별 성능 측정
"""

import asyncio
import time
import statistics
from typing import List, Dict, Any
import httpx


# API 설정
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_ITERATIONS = 10  # 각 테스트 10회 반복


class APIBenchmark:
    """API 벤치마크 클래스"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.results: List[Dict[str, Any]] = []

    async def measure_request(
        self,
        method: str,
        endpoint: str,
        params: Dict = None,
        json_data: Dict = None
    ) -> float:
        """단일 요청 응답 시간 측정 (밀리초)"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            start = time.time()

            if method.upper() == 'GET':
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    params=params or {}
                )
            elif method.upper() == 'POST':
                response = await client.post(
                    f"{self.base_url}{endpoint}",
                    json=json_data or {}
                )

            elapsed = (time.time() - start) * 1000  # Convert to ms

            if response.status_code == 200:
                return elapsed
            else:
                raise Exception(f"Request failed: {response.status_code}")

    async def run_test(
        self,
        name: str,
        method: str,
        endpoint: str,
        params: Dict = None,
        json_data: Dict = None,
        iterations: int = TEST_ITERATIONS,
        cache_warmup: bool = False
    ):
        """테스트 실행"""
        print(f"\n📊 {name}")
        print("-" * 80)

        times: List[float] = []

        # Cache warmup (첫 요청은 측정 제외)
        if cache_warmup:
            try:
                await self.measure_request(method, endpoint, params, json_data)
                print("   🔥 캐시 워밍업 완료")
            except Exception as e:
                print(f"   ⚠️  워밍업 실패: {e}")

        # 실제 측정
        for i in range(iterations):
            try:
                elapsed = await self.measure_request(method, endpoint, params, json_data)
                times.append(elapsed)
                print(f"   #{i+1}: {elapsed:.2f}ms", end="")

                # 성능 표시
                if elapsed < 50:
                    print(" 🟢")
                elif elapsed < 100:
                    print(" 🟡")
                elif elapsed < 200:
                    print(" 🟠")
                else:
                    print(" 🔴")

            except Exception as e:
                print(f"   #{i+1}: ❌ 실패 - {e}")

        if times:
            # 통계 계산
            avg = statistics.mean(times)
            median = statistics.median(times)
            min_time = min(times)
            max_time = max(times)
            stdev = statistics.stdev(times) if len(times) > 1 else 0

            # 목표 달성 여부
            target = 50 if cache_warmup else 200
            achieved = "✅" if avg < target else "❌"

            print("\n   통계:")
            print(f"   - 평균: {avg:.2f}ms {achieved} (목표: <{target}ms)")
            print(f"   - 중간값: {median:.2f}ms")
            print(f"   - 최소: {min_time:.2f}ms")
            print(f"   - 최대: {max_time:.2f}ms")
            print(f"   - 표준편차: {stdev:.2f}ms")

            # 결과 저장
            self.results.append({
                'name': name,
                'avg': avg,
                'median': median,
                'min': min_time,
                'max': max_time,
                'stdev': stdev,
                'target': target,
                'achieved': avg < target
            })

    def print_summary(self):
        """전체 결과 요약"""
        print("\n\n" + "=" * 80)
        print("벤치마크 결과 요약")
        print("=" * 80)

        for result in self.results:
            status = "✅ 달성" if result['achieved'] else "❌ 미달성"
            print(f"\n{result['name']}")
            print(f"  평균: {result['avg']:.2f}ms (목표: <{result['target']}ms) {status}")

        # 전체 달성률
        achieved_count = sum(1 for r in self.results if r['achieved'])
        total_count = len(self.results)
        achievement_rate = (achieved_count / total_count * 100) if total_count > 0 else 0

        print(f"\n전체 달성률: {achieved_count}/{total_count} ({achievement_rate:.1f}%)")
        print("=" * 80)


async def main():
    """메인 벤치마크 실행"""
    print("=" * 80)
    print("서울 위치 서비스 API - 성능 벤치마크")
    print("=" * 80)
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"반복 횟수: {TEST_ITERATIONS}회")
    print()

    benchmark = APIBenchmark()

    # 테스트 케이스
    tests = [
        {
            'name': '카테고리 목록 조회 (캐시)',
            'method': 'GET',
            'endpoint': '/services/categories/list',
            'cache_warmup': True
        },
        {
            'name': '근처 도서관 검색 - 좌표 (캐시 미스)',
            'method': 'GET',
            'endpoint': '/services/nearby',
            'params': {
                'lat': 37.5665,
                'lon': 126.9780,
                'radius': 2000,
                'category': 'libraries',
                'limit': 20
            },
            'cache_warmup': False
        },
        {
            'name': '근처 도서관 검색 - 좌표 (캐시 히트)',
            'method': 'GET',
            'endpoint': '/services/nearby',
            'params': {
                'lat': 37.5665,
                'lon': 126.9780,
                'radius': 2000,
                'category': 'libraries',
                'limit': 20
            },
            'cache_warmup': True
        },
        {
            'name': '주소 지오코딩 (캐시 미스)',
            'method': 'POST',
            'endpoint': '/geocode',
            'json_data': {'address': '서울시청'},
            'cache_warmup': False
        },
        {
            'name': '주소 지오코딩 (캐시 히트)',
            'method': 'POST',
            'endpoint': '/geocode',
            'json_data': {'address': '서울시청'},
            'cache_warmup': True
        },
        {
            'name': '역방향 지오코딩',
            'method': 'POST',
            'endpoint': '/geocode/reverse',
            'json_data': {'latitude': 37.5665, 'longitude': 126.9780},
            'cache_warmup': False
        },
        {
            'name': '문화행사 검색 (캐시 미스)',
            'method': 'GET',
            'endpoint': '/services/cultural_events',
            'params': {
                'lat': 37.5665,
                'lon': 126.9780,
                'radius': 3000,
                'limit': 30
            },
            'cache_warmup': False
        },
        {
            'name': '문화행사 검색 (캐시 히트)',
            'method': 'GET',
            'endpoint': '/services/cultural_events',
            'params': {
                'lat': 37.5665,
                'lon': 126.9780,
                'radius': 3000,
                'limit': 30
            },
            'cache_warmup': True
        }
    ]

    # 테스트 실행
    for test in tests:
        await benchmark.run_test(
            name=test['name'],
            method=test['method'],
            endpoint=test['endpoint'],
            params=test.get('params'),
            json_data=test.get('json_data'),
            cache_warmup=test.get('cache_warmup', False)
        )

        # 테스트 간 대기 (API 부하 방지)
        await asyncio.sleep(1)

    # 결과 요약
    benchmark.print_summary()

    print("\n✅ 벤치마크 완료!\n")


if __name__ == '__main__':
    asyncio.run(main())
