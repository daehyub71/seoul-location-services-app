"""
Supabase Client Module
Provides singleton Supabase client instance
"""

from supabase import create_client, Client
from functools import lru_cache
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache()
def get_supabase_client() -> Client:
    """
    Get cached Supabase client instance (Singleton pattern)

    Returns:
        Client: Supabase client instance
    """
    try:
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_KEY
        )
        logger.info("Supabase client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        raise


def get_supabase_admin_client() -> Client:
    """
    Get Supabase client with service role key (for admin operations)

    Returns:
        Client: Supabase admin client instance
    """
    try:
        client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
        )
        logger.info("Supabase admin client initialized successfully")
        return client
    except Exception as e:
        logger.error(f"Failed to initialize Supabase admin client: {e}")
        raise


# FastAPI dependency for Supabase client
async def get_db() -> Client:
    """
    FastAPI dependency to get Supabase client

    Yields:
        Client: Supabase client instance
    """
    return get_supabase_client()


# Pre-initialize client on module import (optional)
try:
    supabase_client = get_supabase_client()
    logger.info("Supabase client pre-initialized")
except Exception as e:
    logger.warning(f"Failed to pre-initialize Supabase client: {e}")
    supabase_client = None
