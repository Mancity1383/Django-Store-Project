from celery import shared_task
import time 

@shared_task
def send_kiss(name):
    print(f"kissing {name} 💋")
    return f"kissed {name}"