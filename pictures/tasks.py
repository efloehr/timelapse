from celery import task
from .models import Picture, Normal
import pyxif
from util import get_fstop_exposure, normalize_time
from datetime import datetime, timedelta
from sky import est, get_observer, sunset
from PIL import Image
import os.path
from copy import copy


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
    
    frameimg = make_mosaic_image(times, frame_width, columns, hd_ratio, start_row)
    frameimg.save(os.path.join(directory, "{0:08d}.jpg".format(sequence_no)))
                
                
@task()
def make_sunset_synchro_frame(directory, sequence_no, start_day, seconds_until_set, columns, frame_width, hd_ratio=False, start_row=0):
    obs = get_observer()
    frameimg = make_mosaic_image(sunset_times(obs, start_day, -seconds_until_set), frame_width, columns, hd_ratio, start_row)
    frameimg.save(os.path.join(directory, "{0:08d}.jpg".format(sequence_no)))


def sunset_times(observer, start_date, offset_seconds=0):
    # offset negative before, positive after
    current_date = copy(start_date)
    while True:
        sunset_time = normalize_time(sunset(observer, current_date) + timedelta(seconds=offset_seconds))
        try:
            normal_time = Normal.objects.get(timestamp=sunset_time)
        except:
            normal_time = None
        yield normal_time
        current_date += timedelta(days=1)
                
                
def make_mosaic_image(times, frame_width, columns, hd_ratio, start_row):
    scale_width = int(round(float(frame_width) / columns))
    scale_ratio = (9.0 / 16.0) if hd_ratio else (3.0 / 4.0)
    scale_height = int(round(scale_width * scale_ratio))
    frame_height = int(round(frame_width * scale_ratio))
    rows = int(round(frame_height / float(scale_height)))
    
    frameimg = Image.new("RGB", (frame_width, frame_height))

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
    return frameimg
                
                
