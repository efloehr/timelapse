from celery import task
from .models import Picture, Normal
import pyxif
from util import get_fstop_exposure, normalize_time
from datetime import datetime, timedelta
#from sky import est
from PIL import Image
import os.path

@task()
def insert(filepath, check_for_existing):
    Picture.insert(filepath, check_for_existing)
    

@task()
def fix_fstop_exposure(picture_id):
    pic = Picture.objects.get(pk=picture_id)
    dummy, exif_dict, dummy = pyxif.load(pic.filepath)
    
    pic.fstop, pic.exposure = get_fstop_exposure(exif_dict)
    
    pic.save()
    
    
@task()
def make_mosaic_frame(directory, sequence_no, start_time, columns, frame_width, hd_ratio=False, start_row=0):
    normalized_start = normalize_time(start_time)
    times = Normal.objects.filter(timestamp__gte=normalized_start,
                                  timestamp__hour=normalized_start.hour,
                                  timestamp__minute=normalized_start.minute,
                                  timestamp__second=normalized_start.second).iterator()
    
    scale_width = int(round(float(frame_width) / columns))
    scale_ratio = (9.0 / 16.0) if hd_ratio else (3.0 / 4.0)
    scale_height = int(round(scale_width * scale_ratio))
    frame_height = int(round(frame_width * scale_ratio))
    rows = int(round(frame_height / float(scale_height)))
    
    #print (frame_width, frame_height, rows, scale_width, scale_height)
    frameimg = Image.new("RGB", (frame_width, frame_height))
    #print(frameimg.size)

    for row_no in range(0,rows):
        row_offset = row_no * scale_height
        for column_no in range(0,columns):
            column_offset = column_no * scale_width
            #try:
            time = next(times)
            #except:
            #    continue
            if time.picture is not None:
                img = Image.open(time.picture.filepath)
                imgwidth, imgheight = img.size
                cropbox = (0, start_row, imgwidth, start_row + int(round(imgwidth * scale_ratio)))
                img = img.crop(cropbox)
                img = img.resize((scale_width, scale_height))
                imgloc = (column_offset, row_offset)
                frameimg.paste(img, imgloc)
    
    frameimg.save(os.path.join(directory, "{0:08d}.jpg".format(sequence_no)))
                
                
