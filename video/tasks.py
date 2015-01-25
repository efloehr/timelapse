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
    make_standard_movie(start_time, end_time, subdir)


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
    make_standard_movie(start_time, end_time, subdir)

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
    make_standard_movie(start_time, end_time, subdir)


def make_standard_movie(start_time, end_time, subdir):
    daystr = start_time.strftime('%Y-%m-%d')
    moviepath = os.path.join(VIDEO_DIR, subdir)
    imagelistdir = os.path.join(moviepath, 'lists')
    movie_name = daystr
    
    # Make directory if it doesn't exist
    if not os.path.exists(imagelistdir):
        os.makedirs(imagelistdir)

    # Get normal times/images
    normals = Normal.objects.filter(timestamp__gte=start_time, timestamp__lt=end_time)

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

