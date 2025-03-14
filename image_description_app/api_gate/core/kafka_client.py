import asyncio
import json
import logging
from aiokafka import AIOKafkaProducer
from .exceptions import KafkaConnectionError
from api_gateway import config

async def create_producer():
    """Creates and returns a Kafka producer."""
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=config.KAFKA_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        return producer
    except Exception as e:
        logging.error(f"Error creating Kafka producer: {e}")
        raise KafkaConnectionError("Failed to create Kafka producer")