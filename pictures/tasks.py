from celery import task
from .models import Picture, Normal
import pyxif
from util import get_fstop_exposure, normalize_time, make_video
from datetime import datetime, timedelta, time
from sky import est, get_observer, sunset, sunrise, moonset
from PIL import Image, ImageOps, ImageChops, ImageDraw
import os.path
from copy import copy
import itertools
from pytz import utc
import math
from glob import iglob


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
def make_sunset_synchro_frame(directory, sequence_no, start_day, seconds_until_set, columns, frame_width, hd_ratio=False, start_row=0, rows=None):
    make_set_synchro_frame(sunset_times, directory, sequence_no, start_day, seconds_until_set, columns, frame_width, hd_ratio, start_row, rows)


@task()
def make_moonset_synchro_frame(directory, sequence_no, start_day, seconds_until_set, columns, frame_width, hd_ratio=False, start_row=0, rows=None):
    make_set_synchro_frame(moonset_times, directory, sequence_no, start_day, seconds_until_set, columns, frame_width, hd_ratio, start_row, rows)


@task()
def make_sunset_frames(directory, start_date, seconds_until_sunset):
    obs = get_observer()
    os.makedirs(directory, exist_ok=True)
    for sequence_no, time in enumerate(sunset_times(obs, start_date, seconds_until_sunset)):
        if time.picture is None:
            continue
        img = Image.open(time.picture.filepath)
        img = Image.eval(img, lambda x: 255*math.pow((x/255.0),6))
        img = img.resize((1920,1080))
        img.save(os.path.join(directory, "{0:08d}.jpg".format(sequence_no)))
        

def make_set_synchro_frame(setgen, directory, sequence_no, start_day, seconds_until_set, columns, frame_width, hd_ratio, start_row, rows=None):
    obs = get_observer()
    frameimg = make_mosaic_image(setgen(obs, start_day, -seconds_until_set), frame_width, columns, hd_ratio, start_row, rows)
    frameimg.save(os.path.join(directory, "{0:08d}.jpg".format(sequence_no)))


def sunset_times(observer, start_date, offset_seconds=0):
    return set_times(sunset, observer, start_date, offset_seconds)


def moonset_times(observer, start_date, offset_seconds=0):
    return set_times(moonset, observer, start_date, offset_seconds)


def set_times(setfunc, observer, start_date, offset_seconds=0):
    # offset negative before, positive after
    current_date = copy(start_date)
    while True:
        sunset_time = normalize_time(setfunc(observer, current_date) + timedelta(seconds=offset_seconds))
        try:
            normal_time = Normal.objects.get(timestamp=sunset_time)
        except:
            normal_time = None
        yield normal_time
        current_date += timedelta(days=1)
                
                
def make_mosaic_image(times, frame_width, columns, hd_ratio, start_row, rows=None):
    scale_width = int(round(float(frame_width) / columns))
    scale_ratio = (9.0 / 16.0) if hd_ratio else (3.0 / 4.0)
    scale_height = int(round(scale_width * scale_ratio))
    if rows == None:
        frame_height = int(round(frame_width * scale_ratio))
        rows = int(round(frame_height / float(scale_height)))
    else:
        frame_height = rows * scale_height
    
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


@task()
def make_year_stripe_frame(directory, sequence_no, start_time):
    start_day = datetime.combine(start_time, time(0, tzinfo=est)).astimezone(utc)
    end_day = start_day - timedelta(days=1)
    
    normalized_start = normalize_time(start_time.astimezone(utc))
    first_times = Normal.objects.filter(timestamp__gte=start_day, timestamp__lte='2014-09-27',
                                        timestamp__hour=normalized_start.hour,
                                        timestamp__minute=normalized_start.minute,
                                        timestamp__second=normalized_start.second).iterator()
    second_times = Normal.objects.filter(timestamp__gt='2013-09-27', timestamp__lte=end_day,
                                         timestamp__hour=normalized_start.hour,
                                         timestamp__minute=normalized_start.minute,
                                         timestamp__second=normalized_start.second).iterator()
    
    normals = itertools.chain(first_times, second_times)
    
    frameimg = Image.new("RGB", (2048,1536))
    strip_width = 2048.0 / 365
    for day_no, normal in enumerate(normals):
        if normal.picture is not None:
            img = Image.open(normal.picture.filepath)
        else:
            img = Image.new("RGB", (2048,1536))
        start_column = (int(round(strip_width * day_no)))
        img = img.crop((start_column,0,2048,1536))
        frameimg.paste(img, (start_column,0))
    
    frameimg = frameimg.crop((0,456,2048,1536))
    frameimg = frameimg.resize((1920,1080))
    frameimg.save(os.path.join(directory, "{0:08d}.jpg".format(sequence_no)))

    
    
# /var/tlwork/dailies
# ... all_day
base_daily_dir = '/var/tlwork/dailies'

@task()
def make_1080p_image(filepath, savedir, sequence_no):
    frameimg = Image.open(filepath)
    frameimg = frameimg.resize((1440,1080))
    frameimg.save(os.path.join(savedir, "{0:08d}.jpg".format(sequence_no)))

@task()
def make_black_1080p_image(timestamp, savedir, sequence_no):
    frameimg = Image.new("RGB", (1440,1080))
    frameimg.save(os.path.join(savedir, "{0:08d}.jpg".format(sequence_no)))


@task()
def make_daystrip_picture(dirpath, day):
    # Normalize to midnight
    day_start = datetime(day.year, day.month, day.day, tzinfo=est)
    dayname = day.strftime('%Y-%m-%d')

    day_end = day_start + timedelta(days=1)
    
    normals = Normal.objects.filter(timestamp__gte=day_start, timestamp__lt=day_end)

    img = Image.new("RGB", (2048,1536))

    current_row = None
    for normal_no, normal in enumerate(normals):
        if normal.picture is None:
            continue
    
        row = int(math.floor(1536 * (normal_no / 8640.0)))
        
        if row == current_row:
            continue
        
        current_row = row
        picture = Image.open(normal.picture.filepath)
        img.paste(picture.crop((0,row,2048,row+1)),(0,row))

    img.save(os.path.join(dirpath, '{0}.png'.format(dayname)))


@task()
def make_sun_path(directory):
    images = iglob(os.path.join(directory,'*.jpg'))
    lightimg = Image.open(next(images))
    for imagepath in images:
        img = Image.open(imagepath)
        img = Image.eval(img, lambda x: 255*math.pow((x/255.0),8))
        lightimg = ImageChops.lighter(lightimg, img)
            
    lightimg = Image.eval(lightimg, lambda x: 255*math.pow((x/255.0),8))
    lightimg.save(os.path.join(directory, 'sunpath.png'))
