from celery import Celery
from os import path
from dotenv import load_dotenv
import logging

# Create the Celery app
celery = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

# Set up Celery logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ensure tasks are registered
import app.tasks as tasks  # This will make sure tasks are registered with Celery

# Configure periodic task for Celery Beat
celery.conf.beat_schedule = {
    'fetch-events-every-30-seconds': {
        'task': 'app.tasks.fetch_and_process_data',
        'schedule': 30.0,  # Execute every 30 seconds
        'args': ('https://provider.code-challenge.feverup.com/api/events',)
    },
}
celery.conf.timezone = 'UTC'
