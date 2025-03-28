from celery import Celery
import requests
import random

celery = Celery(
    'celery_worker',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0'
)

@celery.task(bind=True)
def process_image(self, image_url):
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code != 200:
            raise Exception("Failed to retrieve image.")

        # Simulate image classification (Replace with ML model inference)
        categories = ["Cloud", "Forest", "Water", "Urban"]
        classification = random.choice(categories)
        confidence = round(random.uniform(70, 99), 2)

        return {"classification": classification, "confidence": confidence}
    except Exception as e:
        self.update_state(state='FAILURE', meta={'error': str(e)})
        raise
