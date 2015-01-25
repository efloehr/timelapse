from datetime import timedelta
import math
import subprocess
import os.path

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
    

def make_movie(imagelistfile, framerate, moviefilepath, name):
    subprocess.check_call(['mencoder',
                           'mf://@{0}'.format(imagelistfile),
                           '-mf', 'fps={0}:type=jpg'.format(framerate),
                           '-ovc', 'x264',
                           '-lavcopts',
                           'vcodec=mpeg4:mbd=2:trell',
                           '-oac',
                           'copy',
                           '-o',
                           os.path.join(moviefilepath, name + '.avi')
                           ])
