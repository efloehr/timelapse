from celery import task
from .models import Info, Normal, Product
from settings import TIMELAPSE_DIR
from datetime import datetime
from sky import sunset, sunrise, est
from util import normalize_time
from PIL import Image, ImageOps, ImageChops
import os.path

APP_DIR = 'images'

@task()
def insert(filepath, check_for_existing=True):
    info = Info.insert(filepath, check_for_existing)
    Normal.match_image(info)


@transaction.atomic
def get_image_product(day_start, start_time, end_time, kind, filepath, filename):
    record, created = Product.objects.get_or_create(filepath = filepath)

    record.day = day_start.date()
    record.start = start_time
    record.end = end_time
    record.kind = kind
    record.filepath = filepath
    record.filename = filename

    record.save()
    return record


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

    img = Image.new("L", (2048,1536), background_color)
    img_light = None

    for time in times:
        source = Image.open(time.picture.filepath)

        # Get the negative
        source_gray = ImageOps.grayscale(source)
        source_neg = ImageOps.invert(source_gray)

        # Threshold white
        source_thresh = Image.eval(source_neg, lambda x: 255*(x>224))

        # Merge in the new image
        img = ImageChops.multiply(img, source_thresh)

        # Make light image
        if img_light is None:
            img_light = source
        else:
            img_light = ImageChops.lighter(img_light, source)


    # Put a date on the image
    daystr = day.strftime('%Y-%m-%d')
    canvas = ImageDraw.Draw(img)
    canvas.text((20,1500), daystr)
    canvas = ImageDraw.Draw(img_light)
    canvas.text((20,1500), daystr)

    # And save
    filename = daystr + '.png'
    filename_light = daystr + '_light.png'
    filename_light_neg = daystr + '_neg.png'

    dirpath = os.path.join(TIMELAPSE_DIR, APP_DIR, 'allnight')
    
    # Make directory if it doesn't exist
    os.makedirs(dirpath, exist_ok=True)

    img.save(os.path.join(dirpath, filename))
    img_light.save(os.path.join(dirpath, filename_light))
    ImageOps.invert(img_light).save(os.path.join(dirpath, filename_light_neg))
