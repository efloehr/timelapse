from celery import task
from .models import Info, Normal


@task()
def insert(filepath, check_for_existing=True):
    info = Info.insert(filepath, check_for_existing)
    Normal.match_image(info)
