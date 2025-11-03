"""
Unit tests for Redis Service
"""

import pytest
import json
from unittest.mock import Mock, patch
from app.core.services.redis_service import RedisService, get_redis_service


class TestRedisService:
    """Redis 서비스 테스트"""

    @pytest.fixture
    def redis_service(self):
        """Redis 서비스 인스턴스 (모킹)"""
        with patch('app.core.services.redis_service.redis.from_url') as mock_redis:
            # Mock Redis client
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client

            service = RedisService()
            service.client = mock_client
            service.enabled = True
            return service

    def test_round_coordinate(self, redis_service):
        """좌표 반올림 테스트"""
        # 기본 4자리
        assert redis_service._round_coordinate(37.566535, 4) == 37.5665
        assert redis_service._round_coordinate(126.978038, 4) == 126.9780

        # 2자리
        assert redis_service._round_coordinate(37.566535, 2) == 37.57

    def test_generate_cache_key_basic(self, redis_service):
        """기본 캐시 키 생성"""
        key = redis_service.generate_cache_key(
            latitude=37.5665,
            longitude=126.9780,
            radius=1000
        )
        # Default precision is 4 decimal places
        assert key == "location:37.5665:126.978:1000"

    def test_generate_cache_key_with_category(self, redis_service):
        """카테고리 포함 캐시 키"""
        key = redis_service.generate_cache_key(
            latitude=37.5665,
            longitude=126.9780,
            radius=1000,
            category="libraries"
        )
        # Default precision is 4 decimal places
        assert key == "location:37.5665:126.978:1000:libraries"

    def test_generate_cache_key_rounding(self, redis_service):
        """좌표 반올림 적용"""
        key1 = redis_service.generate_cache_key(
            latitude=37.56651,
            longitude=126.97801,
            radius=1000
        )
        key2 = redis_service.generate_cache_key(
            latitude=37.56652,
            longitude=126.97802,
            radius=1000
        )
        # 반올림 후 같은 키
        assert key1 == key2

    def test_get_hit(self, redis_service):
        """캐시 HIT 테스트"""
        test_data = {"name": "Test", "value": 123}
        redis_service.client.get.return_value = json.dumps(test_data)

        result = redis_service.get("test:key")

        assert result == test_data
        redis_service.client.get.assert_called_once_with("test:key")

    def test_get_miss(self, redis_service):
        """캐시 MISS 테스트"""
        redis_service.client.get.return_value = None

        result = redis_service.get("test:key")

        assert result is None
        redis_service.client.get.assert_called_once_with("test:key")

    def test_set_success(self, redis_service):
        """캐시 SET 성공 테스트"""
        test_data = {"name": "Test", "value": 123}
        redis_service.client.setex.return_value = True

        success = redis_service.set("test:key", test_data, ttl=300)

        assert success is True
        redis_service.client.setex.assert_called_once()
        # 호출 인자 확인
        call_args = redis_service.client.setex.call_args[0]
        assert call_args[0] == "test:key"
        assert call_args[1] == 300
        assert json.loads(call_args[2]) == test_data

    def test_set_default_ttl(self, redis_service):
        """기본 TTL 사용"""
        redis_service.ttl = 300
        redis_service.client.setex.return_value = True

        redis_service.set("test:key", {"data": "test"})

        call_args = redis_service.client.setex.call_args[0]
        assert call_args[1] == 300  # 기본 TTL

    def test_delete_success(self, redis_service):
        """캐시 DELETE 성공"""
        redis_service.client.delete.return_value = 1

        success = redis_service.delete("test:key")

        assert success is True
        redis_service.client.delete.assert_called_once_with("test:key")

    def test_delete_not_found(self, redis_service):
        """존재하지 않는 키 삭제"""
        redis_service.client.delete.return_value = 0

        success = redis_service.delete("nonexistent:key")

        assert success is False

    def test_delete_pattern(self, redis_service):
        """패턴 매칭 삭제"""
        redis_service.client.keys.return_value = ["loc:1", "loc:2", "loc:3"]
        redis_service.client.delete.return_value = 3

        deleted = redis_service.delete_pattern("loc:*")

        assert deleted == 3
        redis_service.client.keys.assert_called_once_with("loc:*")
        redis_service.client.delete.assert_called_once_with("loc:1", "loc:2", "loc:3")

    def test_delete_pattern_no_match(self, redis_service):
        """매칭되는 키 없음"""
        redis_service.client.keys.return_value = []

        deleted = redis_service.delete_pattern("nonexistent:*")

        assert deleted == 0

    def test_flush_all(self, redis_service):
        """전체 캐시 삭제"""
        redis_service.client.flushdb.return_value = True

        success = redis_service.flush_all()

        assert success is True
        redis_service.client.flushdb.assert_called_once()

    def test_get_stats(self, redis_service):
        """Redis 통계 조회"""
        redis_service.client.info.return_value = {
            "connected_clients": 5,
            "used_memory_human": "1.5M",
            "total_commands_processed": 1000,
            "keyspace_hits": 750,
            "keyspace_misses": 250
        }

        stats = redis_service.get_stats()

        assert stats["enabled"] is True
        assert stats["connected_clients"] == 5
        assert stats["used_memory_human"] == "1.5M"
        assert stats["hit_rate"] == "75.0%"

    def test_get_stats_no_hits(self, redis_service):
        """히트율 0% (hits/misses 모두 0)"""
        redis_service.client.info.return_value = {
            "keyspace_hits": 0,
            "keyspace_misses": 0
        }

        stats = redis_service.get_stats()

        assert stats["hit_rate"] == "0.0%"

    def test_calculate_hit_rate(self, redis_service):
        """히트율 계산"""
        assert redis_service._calculate_hit_rate(75, 25) == "75.0%"
        assert redis_service._calculate_hit_rate(50, 50) == "50.0%"
        assert redis_service._calculate_hit_rate(0, 100) == "0.0%"
        assert redis_service._calculate_hit_rate(100, 0) == "100.0%"
        assert redis_service._calculate_hit_rate(0, 0) == "0.0%"


class TestRedisServiceDisabled:
    """Redis 비활성화 시 동작 테스트"""

    @pytest.fixture
    def disabled_redis_service(self):
        """Redis 비활성화 서비스"""
        with patch('app.core.services.redis_service.redis.from_url') as mock_redis:
            mock_redis.side_effect = Exception("Connection failed")
            service = RedisService()
            return service

    def test_get_returns_none(self, disabled_redis_service):
        """비활성화 시 GET → None"""
        result = disabled_redis_service.get("test:key")
        assert result is None

    def test_set_returns_false(self, disabled_redis_service):
        """비활성화 시 SET → False"""
        success = disabled_redis_service.set("test:key", {"data": "test"})
        assert success is False

    def test_delete_returns_false(self, disabled_redis_service):
        """비활성화 시 DELETE → False"""
        success = disabled_redis_service.delete("test:key")
        assert success is False

    def test_get_stats_disabled(self, disabled_redis_service):
        """비활성화 시 통계"""
        stats = disabled_redis_service.get_stats()
        assert stats == {"enabled": False}


class TestGetRedisServiceSingleton:
    """싱글톤 패턴 테스트"""

    def test_singleton_returns_same_instance(self):
        """같은 인스턴스 반환"""
        service1 = get_redis_service()
        service2 = get_redis_service()
        assert service1 is service2


class TestRedisServiceIntegration:
    """통합 시나리오 테스트"""

    @pytest.fixture
    def redis_service(self):
        with patch('app.core.services.redis_service.redis.from_url') as mock_redis:
            mock_client = Mock()
            mock_client.ping.return_value = True
            mock_redis.return_value = mock_client

            service = RedisService()
            service.client = mock_client
            service.enabled = True
            return service

    def test_cache_workflow(self, redis_service):
        """캐시 워크플로우: SET → GET → DELETE"""
        test_data = {
            "locations": [
                {"name": "Library A", "distance": 500},
                {"name": "Library B", "distance": 1000}
            ]
        }

        # 1. SET
        redis_service.client.setex.return_value = True
        success = redis_service.set("location:37.5665:126.9780:1000", test_data)
        assert success is True

        # 2. GET
        redis_service.client.get.return_value = json.dumps(test_data)
        cached = redis_service.get("location:37.5665:126.9780:1000")
        assert cached == test_data

        # 3. DELETE
        redis_service.client.delete.return_value = 1
        deleted = redis_service.delete("location:37.5665:126.9780:1000")
        assert deleted is True

    def test_invalidate_category_cache(self, redis_service):
        """카테고리별 캐시 무효화"""
        # libraries 카테고리 캐시 무효화
        redis_service.client.keys.return_value = [
            "location:37.5665:126.9780:1000:libraries",
            "location:37.5700:126.9800:2000:libraries"
        ]
        redis_service.client.delete.return_value = 2

        deleted = redis_service.delete_pattern("location:*:libraries")

        assert deleted == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
