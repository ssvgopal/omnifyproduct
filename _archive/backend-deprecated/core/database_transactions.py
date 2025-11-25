"""
MongoDB Transaction Support
Provides transaction management for multi-document operations
"""

import logging
from typing import Dict, Any, Callable, Awaitable, TypeVar
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

T = TypeVar('T')


class TransactionManager:
    """Manages MongoDB transactions"""
    
    def __init__(self, client: AsyncIOMotorClient):
        """
        Initialize transaction manager
        
        Args:
            client: MongoDB client (must be a replica set for transactions)
        """
        self.client = client
    
    @asynccontextmanager
    async def start_transaction(self):
        """
        Start a MongoDB transaction
        
        Yields:
            Client session for transaction
            
        Raises:
            RuntimeError: If client is not a replica set
        """
        # Check if replica set (required for transactions)
        try:
            server_status = await self.client.admin.command('replSetGetStatus')
            is_replica_set = True
        except Exception:
            # Not a replica set - transactions won't work
            logger.warning(
                "MongoDB is not a replica set. Transactions are not available. "
                "Consider using a replica set for production."
            )
            is_replica_set = False
        
        if not is_replica_set:
            # Return a no-op context manager
            from contextlib import nullcontext
            async with nullcontext() as session:
                yield session
            return
        
        # Start session
        async with await self.client.start_session() as session:
            # Start transaction
            async with session.start_transaction():
                try:
                    yield session
                    # Transaction will commit automatically on exit
                except Exception as e:
                    # Transaction will abort automatically on exception
                    logger.error(f"Transaction aborted: {e}")
                    raise
    
    async def execute_in_transaction(
        self,
        operation: Callable[[Any], Awaitable[T]],
        *args,
        **kwargs
    ) -> T:
        """
        Execute operation within a transaction
        
        Args:
            operation: Async function to execute
            *args: Positional arguments for operation
            **kwargs: Keyword arguments for operation
            
        Returns:
            Result of operation
        """
        async with self.start_transaction() as session:
            # Pass session to operation if it accepts it
            if 'session' in operation.__code__.co_varnames:
                kwargs['session'] = session
            
            result = await operation(*args, **kwargs)
            return result


def get_transaction_manager(client: AsyncIOMotorClient) -> TransactionManager:
    """Get transaction manager instance"""
    return TransactionManager(client)

