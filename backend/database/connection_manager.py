"""
Database Connection Manager
Handles MongoDB connection with retry logic, timeouts, and pool configuration
"""

import logging
import asyncio
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from core.retry_logic import retry_database_operation, RetryConfig

logger = logging.getLogger(__name__)


class DatabaseConnectionManager:
    """Manages MongoDB connections with retry and timeout handling"""
    
    def __init__(
        self,
        mongo_url: str,
        db_name: str,
        max_pool_size: int = 100,
        min_pool_size: int = 10,
        max_idle_time_ms: int = 45000,
        connect_timeout_ms: int = 20000,
        socket_timeout_ms: int = 30000,
        server_selection_timeout_ms: int = 5000,
        retry_config: Optional[RetryConfig] = None
    ):
        """
        Initialize database connection manager
        
        Args:
            mongo_url: MongoDB connection URL
            db_name: Database name
            max_pool_size: Maximum connection pool size
            min_pool_size: Minimum connection pool size
            max_idle_time_ms: Maximum idle time for connections
            connect_timeout_ms: Connection timeout in milliseconds
            socket_timeout_ms: Socket timeout in milliseconds
            server_selection_timeout_ms: Server selection timeout in milliseconds
            retry_config: Retry configuration for connection attempts
        """
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
        # Connection pool settings
        self.max_pool_size = max_pool_size
        self.min_pool_size = min_pool_size
        self.max_idle_time_ms = max_idle_time_ms
        self.connect_timeout_ms = connect_timeout_ms
        self.socket_timeout_ms = socket_timeout_ms
        self.server_selection_timeout_ms = server_selection_timeout_ms
        
        # Retry configuration
        if retry_config is None:
            retry_config = RetryConfig(
                max_attempts=3,
                initial_delay=1.0,
                max_delay=5.0
            )
        self.retry_config = retry_config
    
    async def connect(self) -> AsyncIOMotorClient:
        """
        Connect to MongoDB with retry logic
        
        Returns:
            MongoDB client
            
        Raises:
            Exception: If connection fails after all retries
        """
        async def connect_operation():
            try:
                client = AsyncIOMotorClient(
                    self.mongo_url,
                    maxPoolSize=self.max_pool_size,
                    minPoolSize=self.min_pool_size,
                    maxIdleTimeMS=self.max_idle_time_ms,
                    connectTimeoutMS=self.connect_timeout_ms,
                    socketTimeoutMS=self.socket_timeout_ms,
                    serverSelectionTimeoutMS=self.server_selection_timeout_ms
                )
                
                # Test connection
                await client.admin.command('ping')
                
                self.client = client
                self.db = client[self.db_name]
                
                logger.info(f"Connected to MongoDB: {self.db_name}")
                return client
                
            except Exception as e:
                logger.error(f"MongoDB connection failed: {e}")
                raise
        
        # Retry connection with exponential backoff
        client = await retry_database_operation(
            connect_operation,
            self.retry_config,
            "MongoDB connection"
        )
        
        return client
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def health_check(self) -> bool:
        """
        Check database connection health
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            if not self.client:
                return False
            
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_database(self):
        """Get database instance"""
        if not self.db:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self.db
    
    def get_client(self) -> AsyncIOMotorClient:
        """Get MongoDB client"""
        if not self.client:
            raise RuntimeError("Database client not connected. Call connect() first.")
        return self.client

