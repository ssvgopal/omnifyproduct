"""
Database Connection Management
Provides global database instance for dependency injection
"""

from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

# Global database instance
_global_db: Optional[AsyncIOMotorDatabase] = None


def set_global_db(db: AsyncIOMotorDatabase):
    """Set the global database instance"""
    global _global_db
    _global_db = db


def get_global_db() -> Optional[AsyncIOMotorDatabase]:
    """Get the global database instance"""
    return _global_db

