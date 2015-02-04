from datetime import timedelta, date
import math
import subprocess
import os.path
import os
from copy import copy


def rgb_to_int(rgb_tuple):
    return int(round(rgb_tuple[0]*256*256 + rgb_tuple[1]*256 + rgb_tuple[2]))

def int_to_rgb(rgb_int):
    r = (rgb_int >> 16) & 255
    g = (rgb_int >> 8) & 255
    b = rgb_int & 255
    return (r,g,b)

def normalize_time(timestamp, seconds_base=10):
    # Normalize to seconds_base seconds
    normalized_timestamp = timestamp
    #start_second = seconds_base * int(round(timestamp.second / float(seconds_base)))
    # Can't use above because round, when presented with equal distance up or down, rounds to nearest even number
    # Which causes things like 25 -> 30 but 35 -> 40
    start_second = seconds_base * int(math.floor(timestamp.second / float(seconds_base) + 0.5))
    if start_second >= 60:
        normalized_timestamp = timestamp + timedelta(minutes=1)
        start_second = 0
    normalized_timestamp = normalized_timestamp.replace(second=start_second).replace(microsecond=0)
    return normalized_timestamp
    
def get_fstop_exposure(exif_dict):
    # Return fstop*100 and exposure in microseconds (millis * 1000)
    fstop = int(round((exif_dict[33437][1][0] / float(exif_dict[33437][1][1])) * 100))
    exposure = int(round((exif_dict[33434][1][0] / float(exif_dict[33434][1][1])) * 1000000))
    return fstop, exposure
    

def make_video(imagelistfile, framerate, moviefilepath):
    subprocess.check_call(['mencoder',
                           '-really-quiet',
                           'mf://@{0}'.format(imagelistfile),
                           '-mf', 'fps={0}:type=jpg'.format(framerate),
                           '-ovc', 'x264',
                           '-lavcopts',
                           'vcodec=mpeg4:mbd=2:trell',
                           '-vf',
                           'scale=1440:1080',
                           '-oac',
                           'copy',
                           '-o',
                           moviefilepath
                           ])


def record_size(filepath, product_record):
    if os.path.exists(filepath):
        product_record.size = os.stat(filepath).st_size
    else:
        product_record.size = -1

    product_record.save()


# Takes either string in form "2014-01-01" or date, and return days with day_step in between
# If start is after end and day_step is not specified, it will change it to -1 automatically, otherwise
# day_step defaults to 1 day
def day_generator(start_day=None, end_day=None, day_step=None):
    if start_day is None:
        start_day = date.today() - timedelta(day=1)
    elif type(start_day) == str:
        year, month, day = [ int(x) for x in start_day.split('-') ]
        start_day = date(year, month, day)

    if end_day is None:
        end_day = start_day
    elif type(end_day) == str:
        year, month, day = [ int(x) for x in end_day.split('-') ]
        end_day = date(year, month, day)

    current_day = copy(start_day)
    
    if day_step is None:
        if end_day < start_day:
            day_step = -1
        else:
            day_step = 1
    
    range_start = min(start_day, end_day)
    range_end = max(start_day, end_day)
    
    while current_day >= range_start and current_day <= range_end:
        yield current_day
        current_day += timedelta(days=day_step)
