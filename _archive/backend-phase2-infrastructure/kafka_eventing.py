"""
Kafka Event Streaming Service
Enterprise-grade event streaming with topics for integration sync, model training, and DLQ
"""

import os
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, Union, Callable
from dataclasses import dataclass
from enum import Enum
import uuid

from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class EventType(Enum):
    INTEGRATION_SYNC_STARTED = "integration.sync.started"
    INTEGRATION_SYNC_COMPLETED = "integration.sync.completed"
    INTEGRATION_SYNC_FAILED = "integration.sync.failed"
    MODEL_TRAINED = "model.trained"
    MODEL_TRAINING_FAILED = "model.training.failed"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    USER_ACTION = "user.action"
    SYSTEM_ALERT = "system.alert"

class EventPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class EventMetadata:
    """Metadata for event processing"""
    event_id: str
    timestamp: datetime
    source: str
    organization_id: str
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    priority: EventPriority = EventPriority.MEDIUM
    retry_count: int = 0
    max_retries: int = 3

class EventMessage(BaseModel):
    """Event message structure"""
    event_type: str
    metadata: Dict[str, Any]
    payload: Dict[str, Any]
    timestamp: str
    event_id: str
    source: str
    organization_id: str
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None
    priority: str = "medium"
    retry_count: int = 0

class DLQMessage(BaseModel):
    """Dead Letter Queue message"""
    original_event: EventMessage
    error_message: str
    failed_at: str
    retry_count: int
    dlq_reason: str

class KafkaService:
    """
    Kafka Event Streaming Service
    Manages event production, consumption, and dead letter queue handling
    """

    def __init__(self):
        self.enable_kafka = os.getenv("ENABLE_KAFKA", "false").lower() == "true"
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
        self.topic_integration_sync = os.getenv("KAFKA_TOPIC_INTEGRATION_SYNC", "integration.sync")
        self.topic_model_trained = os.getenv("KAFKA_TOPIC_MODEL_TRAINED", "model.trained")
        self.topic_dlq = os.getenv("KAFKA_TOPIC_DLQ", "dlq.integration")
        self.consumer_group = os.getenv("KAFKA_CONSUMER_GROUP", "omnify-consumer-group")
        
        # Kafka clients
        self.producer: Optional[KafkaProducer] = None
        self.consumers: Dict[str, KafkaConsumer] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # DLQ processing
        self.dlq_enabled = True
        self.max_retries = 3

        logger.info(f"Kafka Service initialized", extra={
            "enabled": self.enable_kafka,
            "bootstrap_servers": self.bootstrap_servers,
            "topics": {
                "integration_sync": self.topic_integration_sync,
                "model_trained": self.topic_model_trained,
                "dlq": self.topic_dlq
            }
        })

    async def connect(self) -> bool:
        """Connect to Kafka cluster"""
        try:
            if not self.enable_kafka:
                logger.info("Kafka is disabled")
                return False

            # Create producer
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                retries=3,
                retry_backoff_ms=1000,
                request_timeout_ms=30000,
                api_version=(2, 5, 0)
            )

            logger.info("Connected to Kafka cluster")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Kafka: {str(e)}")
            return False

    async def create_topics(self) -> bool:
        """Create required topics"""
        try:
            if not self.enable_kafka:
                return False

            from kafka.admin import KafkaAdminClient, NewTopic
            
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='omnify-admin'
            )

            topics = [
                NewTopic(
                    name=self.topic_integration_sync,
                    num_partitions=3,
                    replication_factor=1
                ),
                NewTopic(
                    name=self.topic_model_trained,
                    num_partitions=2,
                    replication_factor=1
                ),
                NewTopic(
                    name=self.topic_dlq,
                    num_partitions=1,
                    replication_factor=1
                )
            ]

            admin_client.create_topics(new_topics=topics, validate_only=False)
            admin_client.close()

            logger.info("Kafka topics created successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to create Kafka topics: {str(e)}")
            return False

    async def produce_event(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        metadata: EventMetadata
    ) -> bool:
        """Produce an event to Kafka"""
        try:
            if not self.producer:
                raise RuntimeError("Kafka producer not connected")

            # Determine topic based on event type
            topic = self._get_topic_for_event_type(event_type)
            
            # Create event message
            event_message = EventMessage(
                event_type=event_type.value,
                metadata={
                    "event_id": metadata.event_id,
                    "timestamp": metadata.timestamp.isoformat(),
                    "source": metadata.source,
                    "organization_id": metadata.organization_id,
                    "user_id": metadata.user_id,
                    "correlation_id": metadata.correlation_id,
                    "priority": metadata.priority.value,
                    "retry_count": metadata.retry_count
                },
                payload=payload,
                timestamp=metadata.timestamp.isoformat(),
                event_id=metadata.event_id,
                source=metadata.source,
                organization_id=metadata.organization_id,
                user_id=metadata.user_id,
                correlation_id=metadata.correlation_id,
                priority=metadata.priority.value,
                retry_count=metadata.retry_count
            )

            # Produce message
            future = self.producer.send(
                topic,
                key=metadata.event_id,
                value=event_message.dict()
            )

            # Wait for confirmation
            record_metadata = future.get(timeout=10)
            
            logger.info(f"Event produced to Kafka", extra={
                "event_type": event_type.value,
                "topic": topic,
                "partition": record_metadata.partition,
                "offset": record_metadata.offset,
                "event_id": metadata.event_id,
                "organization_id": metadata.organization_id
            })

            return True

        except Exception as e:
            logger.error(f"Failed to produce event: {str(e)}")
            return False

    def _get_topic_for_event_type(self, event_type: EventType) -> str:
        """Get topic name for event type"""
        if event_type in [EventType.INTEGRATION_SYNC_STARTED, EventType.INTEGRATION_SYNC_COMPLETED, EventType.INTEGRATION_SYNC_FAILED]:
            return self.topic_integration_sync
        elif event_type in [EventType.MODEL_TRAINED, EventType.MODEL_TRAINING_FAILED]:
            return self.topic_model_trained
        else:
            return self.topic_integration_sync  # Default topic

    async def start_consumer(self, topic: str, handler: Callable) -> bool:
        """Start a Kafka consumer for a topic"""
        try:
            if not self.enable_kafka:
                return False

            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.consumer_group,
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda m: m.decode('utf-8') if m else None,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                auto_commit_interval_ms=1000,
                session_timeout_ms=30000,
                heartbeat_interval_ms=10000
            )

            self.consumers[topic] = consumer
            
            # Register handler
            if topic not in self.event_handlers:
                self.event_handlers[topic] = []
            self.event_handlers[topic].append(handler)

            # Start consumer in background
            asyncio.create_task(self._consume_messages(topic, consumer, handler))

            logger.info(f"Kafka consumer started for topic: {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to start Kafka consumer: {str(e)}")
            return False

    async def _consume_messages(self, topic: str, consumer: KafkaConsumer, handler: Callable):
        """Consume messages from Kafka topic"""
        try:
            for message in consumer:
                try:
                    # Parse event message
                    event_data = message.value
                    event_message = EventMessage(**event_data)
                    
                    # Process event
                    await self._process_event(event_message, handler)
                    
                except Exception as e:
                    logger.error(f"Error processing message from {topic}: {str(e)}")
                    # Send to DLQ if enabled
                    if self.dlq_enabled:
                        await self._send_to_dlq(event_data, str(e))

        except Exception as e:
            logger.error(f"Consumer error for topic {topic}: {str(e)}")

    async def _process_event(self, event_message: EventMessage, handler: Callable):
        """Process an event message"""
        try:
            # Call the handler
            await handler(event_message)
            
            logger.info(f"Event processed successfully", extra={
                "event_type": event_message.event_type,
                "event_id": event_message.event_id,
                "organization_id": event_message.organization_id
            })

        except Exception as e:
            logger.error(f"Event processing failed: {str(e)}")
            
            # Check retry count
            if event_message.retry_count < self.max_retries:
                # Retry the event
                await self._retry_event(event_message)
            else:
                # Send to DLQ
                await self._send_to_dlq(event_message.dict(), str(e))

    async def _retry_event(self, event_message: EventMessage):
        """Retry a failed event"""
        try:
            # Increment retry count
            event_message.retry_count += 1
            
            # Create new metadata
            metadata = EventMetadata(
                event_id=event_message.event_id,
                timestamp=datetime.utcnow(),
                source=event_message.source,
                organization_id=event_message.organization_id,
                user_id=event_message.user_id,
                correlation_id=event_message.correlation_id,
                priority=EventPriority(event_message.priority),
                retry_count=event_message.retry_count
            )
            
            # Reproduce event
            event_type = EventType(event_message.event_type)
            await self.produce_event(event_type, event_message.payload, metadata)
            
            logger.info(f"Event retried", extra={
                "event_id": event_message.event_id,
                "retry_count": event_message.retry_count
            })

        except Exception as e:
            logger.error(f"Failed to retry event: {str(e)}")

    async def _send_to_dlq(self, original_event: Union[Dict, EventMessage], error_message: str):
        """Send failed event to Dead Letter Queue"""
        try:
            if not self.producer:
                return

            if isinstance(original_event, dict):
                event_message = EventMessage(**original_event)
            else:
                event_message = original_event

            dlq_message = DLQMessage(
                original_event=event_message,
                error_message=error_message,
                failed_at=datetime.utcnow().isoformat(),
                retry_count=event_message.retry_count,
                dlq_reason="max_retries_exceeded" if event_message.retry_count >= self.max_retries else "processing_error"
            )

            # Send to DLQ topic
            future = self.producer.send(
                self.topic_dlq,
                key=event_message.event_id,
                value=dlq_message.dict()
            )

            future.get(timeout=10)
            
            logger.warning(f"Event sent to DLQ", extra={
                "event_id": event_message.event_id,
                "error_message": error_message,
                "retry_count": event_message.retry_count,
                "dlq_reason": dlq_message.dlq_reason
            })

        except Exception as e:
            logger.error(f"Failed to send event to DLQ: {str(e)}")

    async def get_topic_stats(self, topic: str) -> Dict[str, Any]:
        """Get topic statistics"""
        try:
            if not self.enable_kafka:
                return {"error": "Kafka is disabled"}

            from kafka.admin import KafkaAdminClient
            from kafka.structs import TopicPartition
            
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='omnify-stats'
            )

            # Get topic metadata
            metadata = admin_client.describe_topics([topic])
            topic_metadata = metadata.get(topic)
            
            if not topic_metadata:
                return {"error": f"Topic {topic} not found"}

            # Get consumer group offsets
            consumer = KafkaConsumer(
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.consumer_group
            )
            
            partitions = [TopicPartition(topic, p) for p in topic_metadata.partitions]
            committed_offsets = consumer.committed(partitions)
            end_offsets = consumer.end_offsets(partitions)
            
            consumer.close()
            admin_client.close()

            # Calculate lag
            total_lag = 0
            partition_stats = []
            
            for partition in partitions:
                committed = committed_offsets.get(partition, 0)
                end = end_offsets.get(partition, 0)
                lag = end - committed
                total_lag += lag
                
                partition_stats.append({
                    "partition": partition.partition,
                    "committed_offset": committed,
                    "end_offset": end,
                    "lag": lag
                })

            return {
                "topic": topic,
                "partitions": len(topic_metadata.partitions),
                "total_lag": total_lag,
                "partition_stats": partition_stats,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get topic stats: {str(e)}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """Health check for Kafka service"""
        try:
            if not self.enable_kafka:
                return {
                    "status": "disabled",
                    "kafka_enabled": False,
                    "timestamp": datetime.utcnow().isoformat()
                }

            if not self.producer:
                return {
                    "status": "unhealthy",
                    "error": "Kafka producer not connected",
                    "timestamp": datetime.utcnow().isoformat()
                }

            # Test producer
            test_event = EventMessage(
                event_type="health.check",
                metadata={},
                payload={"test": True},
                timestamp=datetime.utcnow().isoformat(),
                event_id=str(uuid.uuid4()),
                source="kafka-service",
                organization_id="system"
            )

            future = self.producer.send("__health_check__", value=test_event.dict())
            future.get(timeout=5)

            return {
                "status": "healthy",
                "kafka_enabled": self.enable_kafka,
                "producer_connected": True,
                "active_consumers": len(self.consumers),
                "topics": {
                    "integration_sync": self.topic_integration_sync,
                    "model_trained": self.topic_model_trained,
                    "dlq": self.topic_dlq
                },
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Kafka health check failed: {str(e)}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }

    async def close(self):
        """Close Kafka connections"""
        try:
            if self.producer:
                self.producer.close()

            for consumer in self.consumers.values():
                consumer.close()

            logger.info("Kafka service closed")

        except Exception as e:
            logger.error(f"Error closing Kafka service: {str(e)}")

# Global instance
kafka_service = KafkaService()
