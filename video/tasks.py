from django.db import transaction
from celery import task
from .models import Info
from image.models import Normal
from sky import est, get_observer, sunset, sunrise
from util import make_movie
from timelapse.settings import TIMELAPSE_DIR
import os.path
import os
from datetime import datetime, timedelta

VIDEO_DIR = os.path.join(TIMELAPSE_DIR, 'videos')

@task()
def make_all_day_movie(day):
    # Normalize to midnight
    start_time = datetime(day.year, day.month, day.day, tzinfo=est)
    end_time = start_time + timedelta(days=1)
    
    subdir = 'all_day'
    make_standard_movie(start_time, start_time, end_time, subdir, Info.ALL_DAY)


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
    
    subdir = 'daylight'
    make_standard_movie(day_start, start_time, end_time, subdir, Info.DAYLIGHT)

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
    
    subdir = 'overnight'
    make_standard_movie(day_start, start_time, end_time, subdir, Info.NIGHT)


@transaction.atomic
def get_movie_record(day_start, start_time, end_time, kind, filepath, filename):
    record, created = Info.objects.get_or_create(filepath = filepath)
    
    record.day = day_start.date()
    record.start = start_time
    record.end = end_time
    record.kind = kind
    record.filepath = filepath
    record.filename = filename
    
    record.save()
    return record


def make_standard_movie(day_start, start_time, end_time, subdir, kind):
    daystr = start_time.strftime('%Y-%m-%d')
    moviepath = os.path.join(VIDEO_DIR, subdir)
    imagelistdir = os.path.join(moviepath, 'lists')
    movie_name = daystr + '.avi'
    
    # Make directory if it doesn't exist
    if not os.path.exists(imagelistdir):
        os.makedirs(imagelistdir)

    # Get normal times/images
    normals = Normal.objects.filter(timestamp__gte=start_time, timestamp__lt=end_time)

    # Make the movie record
    movie_record = get_movie_record(day_start, start_time, end_time, kind, moviepath, movie_name)
    
    # Make image file
    imagelistfilename = os.path.join(imagelistdir, '{0}.txt'.format(daystr))
    with open(imagelistfilename, 'w') as imagelistfile:
        current_image = None
        for normal in normals:
            if normal.info is not None:
                current_image = normal.info.filepath
                imagelistfile.write(current_image + os.linesep)
            elif current_image is not None:
                imagelistfile.write(current_image + os.linesep)
            
    # Make the movie
    make_movie(imagelistfilename, 24, moviepath, movie_name)

    if os.path.exists(moviepath):
        movie_record.size = os.stat(moviepath).st_size
    else:
        movie_record.size = -1
    
    pic.size = filestat.st_size
    