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
    os.makedirs(imagepath, exist_ok=True)

    img_filepath = os.path.join(imagepath, filename)
    img_light.save(img_filepath)
    image_record = get_video_product(day_start, start_time, end_time, Product.ALLNIGHT, imagepath, filename)
    record_size(img_filepath, image_record)

    img_neg_filepath = os.path.join(imagepath, filename_neg)
    ImageOps.invert(img_light).save(img_neg_filepath)
    image_record_neg = get_video_product(day_start, start_time, end_time, Product.ALLNIGHT_NEG, imagepath, filename_neg)
    record_size(img_neg_filepath, image_record_neg)

