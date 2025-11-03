"""
Redis Caching Service
Upstash Redis 기반 캐싱 레이어
"""

import json
import logging
from typing import Optional, Any
from functools import lru_cache
import redis
from redis.asyncio import Redis as AsyncRedis

from app.core.config import settings

logger = logging.getLogger(__name__)


class RedisService:
    """
    Redis 캐싱 서비스

    Features:
    - Upstash Redis 연결
    - 캐시 키 생성 전략 (좌표 반올림)
    - TTL 5분 기본 설정
    - Get/Set/Delete 메서드
    """

    def __init__(self):
        """Redis 클라이언트 초기화"""
        self.enabled = settings.CACHE_ENABLED
        self.ttl = settings.REDIS_CACHE_TTL
        self.client: Optional[redis.Redis] = None
        self.async_client: Optional[AsyncRedis] = None

        if self.enabled:
            try:
                # Check if REDIS_URL uses HTTP/HTTPS (Upstash REST API)
                if settings.REDIS_URL.startswith(('http://', 'https://')):
                    logger.warning(
                        "Redis URL uses HTTP(S) scheme. "
                        "For Upstash REST API, please use redis:// or rediss:// scheme instead. "
                        "Caching disabled."
                    )
                    self.enabled = False
                    return

                # Sync client
                self.client = redis.from_url(
                    settings.REDIS_URL,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5
                )

                # Test connection
                self.client.ping()
                logger.info("Redis client initialized successfully")

            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Caching disabled.")
                self.enabled = False
                self.client = None

    def _round_coordinate(self, value: float, precision: int = 4) -> float:
        """
        좌표 반올림 (캐시 키 최적화)

        Args:
            value: 좌표값 (위도/경도)
            precision: 소수점 자릿수 (기본 4자리 = 약 11m 정밀도)

        Returns:
            반올림된 좌표값
        """
        return round(value, precision)

    def generate_cache_key(
        self,
        latitude: float,
        longitude: float,
        radius: int,
        category: Optional[str] = None,
        precision: int = 4
    ) -> str:
        """
        캐시 키 생성

        Args:
            latitude: 위도
            longitude: 경도
            radius: 반경 (미터)
            category: 카테고리 (cultural_events, libraries, etc.)
            precision: 좌표 반올림 자릿수

        Returns:
            캐시 키 (예: "location:37.5665:126.9780:1000:cultural_events")
        """
        lat_rounded = self._round_coordinate(latitude, precision)
        lon_rounded = self._round_coordinate(longitude, precision)

        key_parts = [
            "location",
            f"{lat_rounded}",
            f"{lon_rounded}",
            f"{radius}"
        ]

        if category:
            key_parts.append(category)

        return ":".join(key_parts)

    def get(self, key: str) -> Optional[Any]:
        """
        캐시에서 데이터 조회

        Args:
            key: 캐시 키

        Returns:
            캐시된 데이터 (JSON 디코딩) 또는 None
        """
        if not self.enabled or not self.client:
            return None

        try:
            cached = self.client.get(key)
            if cached:
                logger.debug(f"Cache HIT: {key}")
                return json.loads(cached)
            else:
                logger.debug(f"Cache MISS: {key}")
                return None
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {e}")
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        캐시에 데이터 저장

        Args:
            key: 캐시 키
            value: 저장할 데이터 (JSON 직렬화 가능)
            ttl: Time To Live (초) - None이면 기본값 사용

        Returns:
            성공 여부
        """
        if not self.enabled or not self.client:
            return False

        try:
            ttl = ttl or self.ttl
            serialized = json.dumps(value, ensure_ascii=False)
            self.client.setex(key, ttl, serialized)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {e}")
            return False

    def delete(self, key: str) -> bool:
        """
        캐시에서 데이터 삭제

        Args:
            key: 캐시 키

        Returns:
            성공 여부
        """
        if not self.enabled or not self.client:
            return False

        try:
            result = self.client.delete(key)
            logger.debug(f"Cache DELETE: {key} (result: {result})")
            return result > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {e}")
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        패턴에 매칭되는 모든 키 삭제

        Args:
            pattern: 키 패턴 (예: "location:*:cultural_events")

        Returns:
            삭제된 키 개수
        """
        if not self.enabled or not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"Cache DELETE pattern '{pattern}': {deleted} keys")
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Redis DELETE_PATTERN error for '{pattern}': {e}")
            return 0

    def flush_all(self) -> bool:
        """
        모든 캐시 삭제 (주의: 전체 Redis DB 삭제)

        Returns:
            성공 여부
        """
        if not self.enabled or not self.client:
            return False

        try:
            self.client.flushdb()
            logger.warning("Cache FLUSH: All keys deleted")
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHDB error: {e}")
            return False

    def get_stats(self) -> dict:
        """
        Redis 통계 정보 조회

        Returns:
            통계 딕셔너리
        """
        if not self.enabled or not self.client:
            return {"enabled": False}

        try:
            info = self.client.info()
            return {
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                )
            }
        except Exception as e:
            logger.error(f"Redis STATS error: {e}")
            return {"enabled": True, "error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> str:
        """캐시 히트율 계산"""
        total = hits + misses
        if total == 0:
            return "0.0%"
        return f"{(hits / total * 100):.1f}%"

    def close(self):
        """Redis 연결 종료"""
        if self.client:
            try:
                self.client.close()
                logger.info("Redis client closed")
            except Exception as e:
                logger.error(f"Redis close error: {e}")


@lru_cache()
def get_redis_service() -> RedisService:
    """
    Redis 서비스 싱글톤 인스턴스

    Returns:
        RedisService 인스턴스
    """
    return RedisService()


# FastAPI dependency
async def get_redis() -> RedisService:
    """
    FastAPI 의존성: Redis 서비스

    Yields:
        RedisService 인스턴스
    """
    return get_redis_service()


# Pre-initialize on module import
try:
    redis_service = get_redis_service()
    logger.info("Redis service pre-initialized")
except Exception as e:
    logger.warning(f"Failed to pre-initialize Redis service: {e}")
    redis_service = None
