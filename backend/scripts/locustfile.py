"""
Locust Load Testing Configuration
서울 위치 서비스 API 동시 요청 부하 테스트
"""

from locust import HttpUser, task, between, events
import json
import time
from typing import Dict, Any


class ServiceAPIUser(HttpUser):
    """
    서비스 API 사용자 시뮬레이션

    목표:
    - 동시 사용자 100명 시뮬레이션
    - 평균 응답 시간 < 200ms (캐시 미스)
    - 평균 응답 시간 < 50ms (캐시 히트)
    - 에러율 < 1%
    """

    # 요청 간격 (초): 1~3초 대기
    wait_time = between(1, 3)

    # API 기본 경로
    host = "http://localhost:8000"

    def on_start(self):
        """테스트 시작 시 초기화"""
        self.api_base = "/api/v1"

        # 테스트용 좌표 (서울 주요 지역)
        self.test_coordinates = [
            {"lat": 37.5665, "lon": 126.9780, "name": "서울시청"},
            {"lat": 37.5172, "lon": 127.0473, "name": "강남역"},
            {"lat": 37.5510, "lon": 126.9882, "name": "명동"},
            {"lat": 37.5660, "lon": 126.9014, "name": "홍대입구"},
            {"lat": 37.5797, "lon": 126.9770, "name": "경복궁"},
        ]

        self.categories = [
            "cultural_events",
            "libraries",
            "cultural_spaces",
            "future_heritages",
            "public_reservations"
        ]

        self.current_coord_idx = 0
        self.current_category_idx = 0

    def _get_next_coordinate(self) -> Dict[str, Any]:
        """다음 테스트 좌표 반환 (순환)"""
        coord = self.test_coordinates[self.current_coord_idx]
        self.current_coord_idx = (self.current_coord_idx + 1) % len(self.test_coordinates)
        return coord

    def _get_next_category(self) -> str:
        """다음 카테고리 반환 (순환)"""
        category = self.categories[self.current_category_idx]
        self.current_category_idx = (self.current_category_idx + 1) % len(self.categories)
        return category

    @task(5)
    def get_categories_list(self):
        """
        카테고리 목록 조회 (가중치 5)
        가장 빈번한 요청 - 캐시 히트 기대
        목표: < 50ms
        """
        with self.client.get(
            f"{self.api_base}/services/categories/list",
            name="카테고리 목록 조회",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "categories" in data and len(data["categories"]) == 5:
                    response.success()
                else:
                    response.failure("Invalid response structure")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(10)
    def search_nearby_services(self):
        """
        근처 서비스 검색 (가중치 10)
        가장 일반적인 사용 케이스
        목표: < 200ms (캐시 미스), < 50ms (캐시 히트)
        """
        coord = self._get_next_coordinate()
        category = self._get_next_category()

        params = {
            "lat": coord["lat"],
            "lon": coord["lon"],
            "radius": 2000,
            "category": category,
            "limit": 20
        }

        with self.client.get(
            f"{self.api_base}/services/nearby",
            params=params,
            name=f"근처 검색 ({coord['name']})",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "locations" in data:
                    # 성능 평가
                    elapsed_ms = response.elapsed.total_seconds() * 1000
                    if elapsed_ms < 200:
                        response.success()
                    else:
                        response.failure(f"Slow response: {elapsed_ms:.0f}ms")
                else:
                    response.failure("Invalid response structure")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(3)
    def search_cultural_events(self):
        """
        문화행사 검색 (가중치 3)
        카테고리별 전용 엔드포인트
        목표: < 200ms
        """
        coord = self._get_next_coordinate()

        params = {
            "lat": coord["lat"],
            "lon": coord["lon"],
            "radius": 3000,
            "limit": 30
        }

        with self.client.get(
            f"{self.api_base}/services/cultural_events",
            params=params,
            name=f"문화행사 검색",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Invalid response")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(3)
    def search_libraries(self):
        """
        도서관 검색 (가중치 3)
        목표: < 200ms
        """
        coord = self._get_next_coordinate()

        params = {
            "lat": coord["lat"],
            "lon": coord["lon"],
            "radius": 2000,
            "limit": 20
        }

        with self.client.get(
            f"{self.api_base}/services/libraries",
            params=params,
            name=f"도서관 검색",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    response.success()
                else:
                    response.failure("Invalid response")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(2)
    def geocode_address(self):
        """
        주소 지오코딩 (가중치 2)
        목표: < 200ms
        """
        addresses = [
            "서울시청",
            "강남역",
            "명동",
            "홍대입구",
            "경복궁"
        ]

        address = addresses[self.current_coord_idx % len(addresses)]

        with self.client.post(
            f"{self.api_base}/geocode",
            json={"address": address},
            name="주소 지오코딩",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "latitude" in data:
                    response.success()
                else:
                    response.failure("Invalid response")
            else:
                response.failure(f"Got status {response.status_code}")

    @task(1)
    def reverse_geocode(self):
        """
        역방향 지오코딩 (가중치 1)
        목표: < 200ms
        """
        coord = self._get_next_coordinate()

        with self.client.post(
            f"{self.api_base}/geocode/reverse",
            json={"latitude": coord["lat"], "longitude": coord["lon"]},
            name="역방향 지오코딩",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "address" in data:
                    response.success()
                else:
                    response.failure("Invalid response")
            else:
                response.failure(f"Got status {response.status_code}")


# Performance metrics collection
response_times = []
error_count = 0
success_count = 0


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """각 요청의 응답 시간 기록"""
    global response_times, error_count, success_count

    if exception:
        error_count += 1
    else:
        success_count += 1
        response_times.append(response_time)


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """테스트 종료 시 통계 출력"""
    if response_times:
        import statistics

        avg_response = statistics.mean(response_times)
        median_response = statistics.median(response_times)
        p95_response = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_response = sorted(response_times)[int(len(response_times) * 0.99)]

        total_requests = success_count + error_count
        error_rate = (error_count / total_requests * 100) if total_requests > 0 else 0

        print("\n" + "=" * 80)
        print("부하 테스트 결과 요약")
        print("=" * 80)
        print(f"총 요청 수: {total_requests}")
        print(f"성공: {success_count}")
        print(f"실패: {error_count}")
        print(f"에러율: {error_rate:.2f}%")
        print()
        print(f"평균 응답 시간: {avg_response:.2f}ms")
        print(f"중간값 응답 시간: {median_response:.2f}ms")
        print(f"95th percentile: {p95_response:.2f}ms")
        print(f"99th percentile: {p99_response:.2f}ms")
        print()

        # 목표 달성 여부
        goals_met = []
        if avg_response < 200:
            goals_met.append("✅ 평균 응답 < 200ms")
        else:
            goals_met.append(f"❌ 평균 응답 {avg_response:.0f}ms (목표: 200ms)")

        if p95_response < 300:
            goals_met.append("✅ 95th percentile < 300ms")
        else:
            goals_met.append(f"❌ 95th percentile {p95_response:.0f}ms (목표: 300ms)")

        if error_rate < 1:
            goals_met.append("✅ 에러율 < 1%")
        else:
            goals_met.append(f"❌ 에러율 {error_rate:.1f}% (목표: < 1%)")

        print("목표 달성:")
        for goal in goals_met:
            print(f"  {goal}")

        print("=" * 80)
