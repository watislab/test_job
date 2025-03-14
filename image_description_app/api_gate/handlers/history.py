from typing import List

from fastapi import HTTPException
from ..models import history as history_models
import asyncio
import logging
from aiokafka import AIOKafkaProducer
from ..producers import history_producer
from .. import config
import httpx

async def handle_load_history(offset: int, limit: int) -> List[history_models.HistoryItem]:
    """Handles the request to load more history items."""
    try:
        request_id = await history_producer.send_history_request(offset, limit) # Отправляем запрос истории
        if request_id is None:
            raise HTTPException(status_code=500, detail="Failed to send history request")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{config.UPLOAD_SERVICE_URL}/api/history/results/{request_id}",  # Send request to the result retrieval service
                    timeout=30  # Set a timeout
                )
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                results = response.json()
                history_items = [history_models.HistoryItem(**item) for item in results]
                return history_items

            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP error during result retrieval: {e}")
                raise HTTPException(status_code=e.response.status_code, detail=f"Error retrieving result: {e}")
            except httpx.TimeoutException:
                logging.error("Timeout during result retrieval")
                return []
            except Exception as e:
                logging.error(f"Error during result retrieval: {e}")
                return []
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading history: {e}")