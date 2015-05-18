from django.db import transaction
from celery import task
from .models import Info, Normal, Product
from timelapse.settings import TIMELAPSE_DIR
from datetime import datetime, timedelta
from sky import sunset, sunrise, est, get_observer
from util import normalize_time, record_size
from PIL import Image, ImageOps, ImageChops, ImageDraw
import os.path
import math
import shutil

APP_DIR = 'images'

@task()
def insert(filepath, check_for_existing=True):
    info = Info.insert(filepath, check_for_existing)
    Normal.match_image(info)


@transaction.atomic
def get_image_product(day_start, start_time, end_time, kind, filepath, filename):
    try:
        record = Product.objects.get(filepath = filepath)
    except Product.DoesNotExist:
        record = Product(filepath = filepath)

    record.day = day_start.date()
    record.start = start_time
    record.end = end_time
    record.kind = kind
    record.filepath = filepath
    record.filename = filename

    record.save()
    return record


@task()
def make_all_night_image(day):
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

    normals = Normal.objects.filter(timestamp__gte=start_time, timestamp__lte=end_time, info__isnull=False)

    img_light = None

    for normal in normals:
        source = Image.open(normal.info.filepath)

        # Make light image
        if img_light is None:
            img_light = source
        else:
            img_light = ImageChops.lighter(img_light, source)


    # Put a date on the image
    daystr = day.strftime('%Y-%m-%d')
    canvas = ImageDraw.Draw(img_light)
    canvas.text((20,1500), daystr)

    # And save
    filename = daystr + '.png'
    filename_neg = daystr + '_neg.png'

    imagepath = os.path.join(TIMELAPSE_DIR, APP_DIR, 'allnight')
    
    # Make directory if it doesn't exist
    if not os.path.exists(imagepath):
        os.makedirs(imagepath)

    img_filepath = os.path.join(imagepath, filename)
    img_light.save(img_filepath)
    image_record = get_image_product(day_start, start_time, end_time, Product.ALLNIGHT, imagepath, filename)
    record_size(img_filepath, image_record)

    img_neg_filepath = os.path.join(imagepath, filename_neg)
    ImageOps.invert(img_light).save(img_neg_filepath)
    image_record_neg = get_image_product(day_start, start_time, end_time, Product.ALLNIGHT_NEG, imagepath, filename_neg)
    record_size(img_neg_filepath, image_record_neg)


@task()
def make_daystrip(day):
    # Normalize to midnight
    day_start = datetime(day.year, day.month, day.day, tzinfo=est)
    day_end = day_start + timedelta(days=1)
    dayname = day.strftime('%Y-%m-%d')

    normals = Normal.objects.filter(timestamp__gte=day_start, timestamp__lt=day_end)

    img = Image.new("RGB", (2048,8640))

    for row, normal in enumerate(normals):
        if normal.info is None:
            continue

        picture = Image.open(normal.info.filepath)
        img.paste(picture.crop((0,400,2048,401)),(0,row))

    imagepath = os.path.join(TIMELAPSE_DIR, APP_DIR, 'daystrip')

    # Make directory if it doesn't exist
    if not os.path.exists(imagepath):
        os.makedirs(imagepath)

    filename = '{0}.png'.format(dayname)
    img_filepath = os.path.join(imagepath, filename)
    img.save(img_filepath)
    image_record = get_image_product(day_start, day_start, day_end, Product.DAYSTRIP, imagepath, filename)
    record_size(img_filepath, image_record)


@task()
def make_daystrip_picture(day):
    # Normalize to midnight
    day_start = datetime(day.year, day.month, day.day, tzinfo=est)
    day_end = day_start + timedelta(days=1)
    dayname = day.strftime('%Y-%m-%d')

    normals = Normal.objects.filter(timestamp__gte=day_start, timestamp__lt=day_end)

    img = Image.new("RGB", (2048,1536))

    current_col = None
    for normal_no, normal in enumerate(normals):
        if normal.info is None:
            continue

        column = int(math.floor(2048 * (normal_no / 8640.0)))

        if column == current_col:
            continue

        current_col = column
        picture = Image.open(normal.info.filepath)
        img.paste(picture.crop((column,0,column+1,1536)),(column,0))

    imagepath = os.path.join(TIMELAPSE_DIR, APP_DIR, 'daypic')

    # Make directory if it doesn't exist
    if not os.path.exists(imagepath):
        os.makedirs(imagepath)

    filename = '{0}.png'.format(dayname)
    img_filepath = os.path.join(imagepath, filename)
    img.save(img_filepath)
    image_record = get_image_product(day_start, day_start, day_end, Product.DAYSTRIP_PIC, imagepath, filename)
    record_size(img_filepath, image_record)


@task()
def make_all_day_image(day):
    background_color = 255 # White

    # Normalize to midnight
    day_start = datetime(day.year, day.month, day.day, tzinfo=est)

    # Find that day's sunrise and sunset
    obs = get_observer()
    sunrise_time = sunrise(obs, day_start)
    sunset_time = sunset(obs, day_start)

    start_time = sunrise_time + timedelta(minutes=60)
    end_time = sunset_time - timedelta(minutes=60)

    normals = Normal.objects.filter(timestamp__gte=start_time, timestamp__lte=end_time, info__isnull=False)

    img = Image.new("L", (2048,1536), background_color)
    img_light = None
    img_dark = None
    
    for normal in normals:
        source = Image.open(normal.info.filepath)

        # Make light image
        if img_light is None:
            img_light = source
        else:
            img_light = ImageChops.lighter(img_light, source)

        # Make dark image
        if img_dark is None:
            img_dark = source
        else:
            img_dark = ImageChops.darker(img_dark, source)

    # Put a date on the image
    daystr = day.strftime('%Y-%m-%d')
    canvas = ImageDraw.Draw(img_light)
    canvas.text((20,1500), daystr)
    canvas = ImageDraw.Draw(img_dark)
    canvas.text((20,1500), daystr)

    # And save
    filename_light = daystr + '_light.png'
    filename_dark = daystr + '_dark.png'

    imagepath = os.path.join(TIMELAPSE_DIR, APP_DIR, 'allday')

    # Make directory if it doesn't exist
    if not os.path.exists(imagepath):
        os.makedirs(imagepath)

    img_filepath = os.path.join(imagepath, filename_light)
    img_light.save(img_filepath)
    image_record = get_image_product(day_start, start_time, end_time, Product.ALLDAY_LIGHT, imagepath, filename_light)
    record_size(img_filepath, image_record)

    img_filepath = os.path.join(imagepath, filename_dark)
    img_dark.save(img_filepath)
    image_record = get_image_product(day_start, start_time, end_time, Product.ALLDAY_DARK, imagepath, filename_dark)
    record_size(img_filepath, image_record)


@task
def copy_all_day_images(day, dirpath):
    # Normalize to midnight
    day_start = datetime(day.year, day.month, day.day, tzinfo=est)

    # Find that day's sunrise and sunset
    obs = get_observer()
    sunrise_time = sunrise(obs, day_start)
    sunset_time = sunset(obs, day_start)

    start_time = sunrise_time + timedelta(minutes=60)
    end_time = sunset_time - timedelta(minutes=60)

    normals = Normal.objects.filter(timestamp__gte=start_time, timestamp__lte=end_time, info__isnull=False)

    for normal in normals:
        print normal.info.filename
        shutil.copyfile(normal.info.filepath, os.path.join(dirpath, normal.info.filename))
