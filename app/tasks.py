# from celery_worker import celery
from celery import Celery

import requests
from app.processors.event_processor import process_and_store_events_stream
import logging

celery = Celery(
    "tasks", broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1"
)

logger = logging.getLogger(__name__)


@celery.task(bind=True, max_retries=3, default_retry_delay=60)
def fetch_and_process_data(self, endpoint):
    """
    Celery task to fetch event data from an external API and store
    it in PostgreSQL.
    Uses streaming parsing to handle large XML data efficiently.
    """
    logger.info(f"Fetching data from {endpoint}...")
    try:
        response = requests.get(
            endpoint, stream=True
        )  # Stream the response to handle large XML files
        if response.status_code == 200:
            xml_data = response.content  # Byte string from the API response
            # Ensure the content is in bytes, if it's not already
            if isinstance(xml_data, str):
                xml_data = xml_data.encode("utf-8")
            logger.info(f"Fetched data from {endpoint}. Length: \
                        {len(xml_data)}")
            process_and_store_events_stream(xml_data)
            logger.info("Data processed successfully.")
        else:
            raise Exception(
                f"Failed to fetch data from {endpoint}, \
                    status: {response.status_code}"
            )
    except Exception as exc:
        logger.error(f"Error fetching data: {str(exc)}")
        self.retry(exc=exc)
