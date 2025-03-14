from fastapi import HTTPException
from ..models import image as image_models
import asyncio
import logging
import uuid
from aiokafka import AIOKafkaProducer
from ..producers import image_producer
from .. import config
import httpx

async def handle_upload_image(request: image_models.ImageUploadRequest):
    """Handles the image upload request."""
    try:
        message = {
            "file_content": request.file_content.decode('latin-1'),
            "model_name": request.model_name
        }
        request_id = await image_producer.send_image(message)
        if request_id is None:
            raise HTTPException(status_code=500, detail="Failed to send image message")
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{config.UPLOAD_SERVICE_URL}/api/results/{request_id}",  # Send request to the result retrieval service
                    timeout=30  # Set a timeout
                )
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                result = response.json()
                description = result.get("description")  # Get the description from the response
                return request_id, description  # Return request_id and the description

            except httpx.HTTPStatusError as e:
                logging.error(f"HTTP error during result retrieval: {e}")
                raise HTTPException(status_code=e.response.status_code, detail=f"Error retrieving result: {e}")
            except httpx.TimeoutException:
                logging.error("Timeout during result retrieval")
                return request_id, "Timeout waiting for description"
            except Exception as e:
                logging.error(f"Error during result retrieval: {e}")
                return request_id, "Error receiving description"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send upload message: {e}")