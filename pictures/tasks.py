from celery import task
from .models import Picture
import pyxif
from util import get_fstop_exposure


@task()
def insert(filepath, check_for_existing):
    Picture.insert(filepath, check_for_existing)
    

@task()
def fix_fstop_exposure(picture_id):
    pic = Picture.objects.get(pk=picture_id)
    dummy, exif_dict, dummy = pyxif.load(pic.filepath)
    
    pic.fstop, pic.exposure = get_fstop_exposure(exif_dict)
    
    pic.save()