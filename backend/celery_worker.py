from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

@celery_app.task
def process_image(image_url):
    # Simulated image processing task
    return {"classification": "Urban", "confidence": 98.2}