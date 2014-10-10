from celery import task
from .models import Picture, Normal
import pyxif
from util import get_fstop_exposure, normalize_time, make_movie
from datetime import datetime, timedelta
from sky import est, get_observer, sunset, sunrise
from PIL import Image, ImageOps, ImageChops, ImageDraw
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
def make_all_day_movie(day):
    # Normalize to midnight
    start_time = datetime(day.year, day.month, day.day, tzinfo=est)
    end_time = start_time + timedelta(days=1)
    make_standard_movie(start_time, end_time, 'all_day')


# ... daylight
@task()
def make_daylight_movie(day):
    # Normalize to midnight
    day_start = datetime(day.year, day.month, day.day, tzinfo=est)
    
    # Find that day's sunrise and sunset
    obs = get_observer()
    sunrise_time = sunrise(obs, day_start)
    sunset_time = sunset(obs, day_start)
    
    start_time = sunrise_time - timedelta(minutes=60)
    end_time = sunset_time + timedelta(minutes=60)
    
    make_standard_movie(start_time, end_time, 'daylight')

# ... overnight
@task()
def make_overnight_movie(day):
    # Normalize to midnight
    day_start = datetime(day.year, day.month, day.day, tzinfo=est)
    
    # Find that day's sunset
    obs = get_observer()
    sunset_time = sunset(obs, day_start)

    # And next day's sunrise
    sunrise_time = sunrise(obs, sunset_time)
    
    start_time = sunset_time
    end_time = sunrise_time
    
    make_standard_movie(start_time, end_time, 'overnight')

# /var/tlwork/allnight
@task()
def make_all_night_image(day):
    background_color = 255 # White

    # Normalize to midnight
    day_start = datetime(day.year, day.month, day.day, tzinfo=est)
    
    # Find that day's sunset
    obs = get_observer()
    sunset_time = sunset(obs, day_start)

    # And next day's sunrise
    sunrise_time = sunrise(obs, sunset_time)
    
    # One hour after and before to remove all light
    start_time = normalize_time(sunset_time + timedelta(hours=1))
    end_time = normalize_time(sunrise_time - timedelta(hours=1))
    
    times = Normal.objects.filter(timestamp__gte=start_time, timestamp__lte=end_time, picture__id__isnull=False)
    
    img = Image.new("L", (1440,1080), background_color)

    for time in times:
        source = Image.open(time.picture.filepath)
    
        # Get the negative
        source_gray = ImageOps.grayscale(source)
        source_neg = ImageOps.invert(source_gray)

        # Threshold white
        source_thresh = Image.eval(source_neg, lambda x: 255*(x>210))
        
        # Scale
        source_scaled = source_thresh.resize((1440,1080))
        
        # Merge in the new image
        img = ImageChops.multiply(img, source_scaled)

    # Put a date on the image
    canvas = ImageDraw.Draw(img)
    canvas.text((20,1050), day.strftime("%Y-%m-%d"))

    # And save
    dirpath = '/var/tlwork/allnight'
    filename = start_time.strftime('%Y-%m-%d') + '.jpg'
    
    # Make directory if it doesn't exist
    os.makedirs(dirpath, exist_ok=True)

    img.save(os.path.join(dirpath, filename))


def make_standard_movie(start_time, end_time, subdir):
    day_dir = start_time.strftime('%Y-%m-%d')
    dirpath = os.path.join(base_daily_dir, day_dir, subdir)
    movie_name = day_dir
 
    # Make directory if it doesn't exist
    os.makedirs(dirpath, exist_ok=True)

    # Get normal times/images
    normals = Normal.objects.filter(timestamp__gte=start_time, timestamp__lt=end_time)
    
    # go through and make image frames (1080p)
    for sequence_no, normal in enumerate(normals):
        if normal.picture is not None:
            make_1080p_image(normal.picture.filepath, dirpath, sequence_no+1)
        else:
            make_black_1080p_image(normal.timestamp, dirpath, sequence_no+1)

    # Make the movie
    make_movie(dirpath, movie_name, 24)
