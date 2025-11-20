"""
Database connection and utilities for Discord bot.
"""
import asyncpg
from typing import Optional
from contextlib import asynccontextmanager

from config import settings
from utils.logger import log


class DatabaseManager:
    """Manages database connections and operations."""

    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Establish database connection pool."""
        try:
            self.pool = await asyncpg.create_pool(
                dsn=settings.database_url.replace("+asyncpg", ""),
                min_size=2,
                max_size=settings.database_pool_size,
                command_timeout=60,
            )
            log.info("Database connection pool established")
        except Exception as e:
            log.error(f"Failed to connect to database: {e}")
            raise

    async def disconnect(self):
        """Close database connection pool."""
        if self.pool:
            await self.pool.close()
            log.info("Database connection pool closed")

    @asynccontextmanager
    async def acquire(self):
        """Acquire a database connection from the pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        async with self.pool.acquire() as connection:
            yield connection

    async def execute(self, query: str, *args):
        """Execute a query without returning results."""
        async with self.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args):
        """Fetch multiple rows from a query."""
        async with self.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        """Fetch a single row from a query."""
        async with self.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetchval(self, query: str, *args):
        """Fetch a single value from a query."""
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args)


# Global database manager instance
db = DatabaseManager()
