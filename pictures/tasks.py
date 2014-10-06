from celery import task
from .models import Picture

@task()
def insert(filepath, check_for_existing):
    Picture.insert(filepath, check_for_existing)