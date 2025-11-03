"""
Cache Decorator and Utilities
Redis 기반 캐싱 데코레이터
"""

import json
import logging
import functools
from typing import Callable, Optional, Any
import hashlib

from app.core.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


def generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """
    함수 호출 인자 기반 캐시 키 생성

    Args:
        func_name: 함수명
        *args: 위치 인자
        **kwargs: 키워드 인자

    Returns:
        캐시 키
    """
    # 인자를 문자열로 변환
    args_str = json.dumps(args, sort_keys=True, default=str)
    kwargs_str = json.dumps(kwargs, sort_keys=True, default=str)

    # 해시 생성 (긴 키 방지)
    key_content = f"{func_name}:{args_str}:{kwargs_str}"
    key_hash = hashlib.md5(key_content.encode()).hexdigest()

    return f"cache:{func_name}:{key_hash}"


def cache_response(
    ttl: Optional[int] = None,
    key_prefix: Optional[str] = None
):
    """
    함수 응답 캐싱 데코레이터

    Args:
        ttl: Time To Live (초), None이면 Redis 서비스 기본값 사용
        key_prefix: 캐시 키 접두사

    Example:
        @cache_response(ttl=300, key_prefix="location")
        def get_nearby_locations(lat, lon, radius):
            # Expensive computation
            return results
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            redis = get_redis_service()

            # Redis 비활성화 시 함수 직접 실행
            if not redis.enabled:
                logger.debug(f"Cache disabled, executing {func.__name__} directly")
                return func(*args, **kwargs)

            # 캐시 키 생성
            func_name = f"{key_prefix}.{func.__name__}" if key_prefix else func.__name__
            cache_key = generate_cache_key(func_name, *args, **kwargs)

            # 캐시 조회
            cached_result = redis.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache HIT: {func.__name__}")
                return cached_result

            # 캐시 미스: 함수 실행
            logger.info(f"Cache MISS: {func.__name__}, executing...")
            result = func(*args, **kwargs)

            # 결과 캐싱
            redis.set(cache_key, result, ttl=ttl)

            return result

        # Async 버전
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            redis = get_redis_service()

            if not redis.enabled:
                logger.debug(f"Cache disabled, executing {func.__name__} directly")
                return await func(*args, **kwargs)

            func_name = f"{key_prefix}.{func.__name__}" if key_prefix else func.__name__
            cache_key = generate_cache_key(func_name, *args, **kwargs)

            cached_result = redis.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache HIT: {func.__name__}")
                return cached_result

            logger.info(f"Cache MISS: {func.__name__}, executing...")
            result = await func(*args, **kwargs)

            redis.set(cache_key, result, ttl=ttl)

            return result

        # 함수가 코루틴인지 확인
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return wrapper

    return decorator


def invalidate_cache(pattern: str = "*") -> int:
    """
    캐시 무효화

    Args:
        pattern: 삭제할 캐시 키 패턴 (예: "location:*")

    Returns:
        삭제된 키 개수
    """
    redis = get_redis_service()

    if not redis.enabled:
        logger.warning("Cache disabled, invalidation skipped")
        return 0

    deleted = redis.delete_pattern(f"cache:{pattern}")
    logger.info(f"Invalidated {deleted} cache entries matching '{pattern}'")

    return deleted


def cache_location_query(ttl: int = 300):
    """
    위치 쿼리 전용 캐싱 데코레이터

    Args:
        ttl: Time To Live (초), 기본 5분

    Example:
        @cache_location_query(ttl=300)
        def find_nearby_libraries(lat, lon, radius):
            return results
    """
    return cache_response(ttl=ttl, key_prefix="location")


def cache_supabase_query(ttl: int = 600):
    """
    Supabase 쿼리 전용 캐싱 데코레이터

    Args:
        ttl: Time To Live (초), 기본 10분

    Example:
        @cache_supabase_query(ttl=600)
        def get_all_libraries():
            return supabase.table('libraries').select('*').execute()
    """
    return cache_response(ttl=ttl, key_prefix="supabase")


class CacheManager:
    """
    캐시 관리 클래스

    Features:
    - 캐시 통계 조회
    - 패턴별 캐시 무효화
    - 캐시 전체 삭제
    """

    def __init__(self):
        self.redis = get_redis_service()

    def get_stats(self) -> dict:
        """Redis 캐시 통계 조회"""
        return self.redis.get_stats()

    def invalidate_pattern(self, pattern: str) -> int:
        """특정 패턴의 캐시 무효화"""
        return invalidate_cache(pattern)

    def invalidate_all(self) -> bool:
        """모든 캐시 삭제 (주의!)"""
        if not self.redis.enabled:
            return False

        confirm = input("Are you sure you want to flush all cache? (yes/no): ")
        if confirm.lower() == 'yes':
            return self.redis.flush_all()
        else:
            logger.info("Cache flush cancelled")
            return False

    def get_cache_info(self, func_name: str, *args, **kwargs) -> Optional[dict]:
        """특정 함수 호출의 캐시 정보 조회"""
        cache_key = generate_cache_key(func_name, *args, **kwargs)
        cached = self.redis.get(cache_key)

        if cached:
            return {
                "key": cache_key,
                "exists": True,
                "data": cached
            }
        else:
            return {
                "key": cache_key,
                "exists": False,
                "data": None
            }


# Convenience instance
cache_manager = CacheManager()


def warm_up_cache(data_dict: dict, ttl: Optional[int] = None):
    """
    캐시 워밍업 (사전 데이터 로딩)

    Args:
        data_dict: {cache_key: data} 형태의 딕셔너리
        ttl: Time To Live (초)

    Example:
        warm_up_cache({
            "location:popular:gangnam": gangnam_data,
            "location:popular:hongdae": hongdae_data
        }, ttl=3600)
    """
    redis = get_redis_service()

    if not redis.enabled:
        logger.warning("Cache disabled, warm-up skipped")
        return

    success_count = 0
    for key, data in data_dict.items():
        if redis.set(f"cache:{key}", data, ttl=ttl):
            success_count += 1

    logger.info(f"Cache warm-up: {success_count}/{len(data_dict)} entries loaded")


def cache_with_location_key(
    lat: float,
    lon: float,
    radius: int,
    category: Optional[str] = None,
    ttl: int = 300
):
    """
    위치 기반 캐시 키를 사용하는 데코레이터

    Args:
        lat: 위도
        lon: 경도
        radius: 반경 (미터)
        category: 카테고리
        ttl: Time To Live (초)

    Example:
        @cache_with_location_key(lat=37.5665, lon=126.9780, radius=1000, category="libraries")
        def get_nearby_data():
            return data
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            redis = get_redis_service()

            if not redis.enabled:
                return func(*args, **kwargs)

            # 위치 기반 캐시 키 생성
            cache_key = redis.generate_cache_key(lat, lon, radius, category)

            cached_result = redis.get(cache_key)
            if cached_result is not None:
                logger.info(f"Location cache HIT: {cache_key}")
                return cached_result

            logger.info(f"Location cache MISS: {cache_key}, executing...")
            result = func(*args, **kwargs)

            redis.set(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator
