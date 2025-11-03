"""
API Dependencies
FastAPI 의존성 주입
"""

from typing import Generator
from functools import lru_cache

from app.db.supabase_client import get_supabase_client, get_supabase_admin_client
from app.core.services.redis_service import get_redis_service
from app.core.services.kakao_map_service import get_kakao_map_service
from app.core.workflow.service_graph import get_service_graph


# Supabase Client Dependencies

async def get_db():
    """
    Supabase 클라이언트 의존성

    Usage:
        @app.get("/items")
        async def read_items(supabase: Client = Depends(get_db)):
            response = supabase.table("items").select("*").execute()
            return response.data
    """
    return get_supabase_client()


async def get_db_admin():
    """
    Supabase Admin 클라이언트 의존성 (Service Role Key 사용)

    Usage:
        @app.post("/admin/items")
        async def create_item(supabase: Client = Depends(get_db_admin)):
            # Admin-level operations
            pass
    """
    return get_supabase_admin_client()


# Redis Service Dependencies

async def get_redis():
    """
    Redis 서비스 의존성

    Usage:
        @app.get("/cached")
        async def cached_endpoint(redis: RedisService = Depends(get_redis)):
            cached = redis.get("key")
            if cached:
                return cached
            # ... compute result
            redis.set("key", result, ttl=300)
            return result
    """
    return get_redis_service()


# Kakao Map Service Dependencies

async def get_kakao():
    """
    Kakao Map 서비스 의존성

    Usage:
        @app.get("/geocode")
        async def geocode(address: str, kakao: KakaoMapService = Depends(get_kakao)):
            coords = await kakao.address_to_coordinates(address)
            return coords
    """
    return get_kakao_map_service()


# Workflow Service Dependencies

async def get_workflow(use_llm: bool = False):
    """
    LangGraph 워크플로우 의존성

    Usage:
        @app.get("/search")
        async def search(
            lat: float,
            lon: float,
            workflow: ServiceSearchGraph = Depends(get_workflow)
        ):
            query = LocationQuery(latitude=lat, longitude=lon)
            state = await workflow.run(query)
            return state.response
    """
    return get_service_graph(use_llm=use_llm)


# Configuration Dependencies

@lru_cache()
def get_settings():
    """
    Settings 의존성

    Usage:
        @app.get("/config")
        async def get_config(settings: Settings = Depends(get_settings)):
            return {
                "environment": settings.ENVIRONMENT,
                "cache_enabled": settings.CACHE_ENABLED
            }
    """
    from app.core.config import settings
    return settings


# Pagination Dependencies

class PaginationParams:
    """페이지네이션 파라미터"""

    def __init__(
        self,
        skip: int = 0,
        limit: int = 50,
        max_limit: int = 200
    ):
        self.skip = max(0, skip)
        self.limit = min(limit, max_limit)


def get_pagination(skip: int = 0, limit: int = 50) -> PaginationParams:
    """
    페이지네이션 의존성

    Usage:
        @app.get("/items")
        async def list_items(
            pagination: PaginationParams = Depends(get_pagination)
        ):
            return {
                "skip": pagination.skip,
                "limit": pagination.limit
            }
    """
    return PaginationParams(skip=skip, limit=limit)


# Authentication Dependencies (Placeholder)

async def get_current_user():
    """
    현재 사용자 의존성 (Placeholder)

    TODO: Implement authentication logic
    """
    # For now, return None (no authentication)
    return None


async def get_current_active_user():
    """
    현재 활성 사용자 의존성 (Placeholder)

    TODO: Implement authentication logic
    """
    # For now, return None (no authentication)
    return None
