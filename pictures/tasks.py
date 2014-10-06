from celery import task
from models import Picture

@task()
def insert(filepath):
    Picture.insert(filepath)