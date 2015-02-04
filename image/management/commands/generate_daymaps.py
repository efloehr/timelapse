from django.core.management.base import BaseCommand, CommandError
from django.db import models
from image.models import Normal
from PIL import Image, ImageDraw
from sky import est
from util import int_to_rgb
from datetime import datetime, time
import os.path
from image.tasks import APP_DIR
from timelapse.settings import TIMELAPSE_DIR


class Command(BaseCommand):
    def handle(self, *args, **options):
        normals = Normal.objects.all()
        bounds = normals.aggregate(models.Min('timestamp'), models.Max('timestamp'))
        start = bounds['timestamp__min'].astimezone(est)
        end = bounds['timestamp__max'].astimezone(est)
        days = (end - start).days + 1
        start_day = start.date()
        start_date = datetime.combine(start_day, time(tzinfo=est))

        # Images will be 8640 pixels across and down the number of days in the set
        #center_color = models.IntegerField(null=True)
        im_center = Image.new('RGB', (8640,days))

        #mean_color = models.IntegerField(null=True)
        im_mean = Image.new('RGB', (8640,days))

        #median_color = models.IntegerField(null=True)
        im_median = Image.new('RGB', (8640,days))

        #min_color = models.IntegerField(null=True)
        im_min = Image.new('RGB', (8640,days))

        #max_color = models.IntegerField(null=True)
        im_max = Image.new('RGB', (8640,days))

        for normal in normals:
            if normal.info is None:
                continue

            timestamp = normal.timestamp.astimezone(est)
            datestamp = datetime.combine(timestamp.date(), time(tzinfo=est))

            y = (timestamp - start_date).days
            x = int(round((timestamp - datestamp).seconds / 10))
            pos = (x,y)

            # Paint pixels
            color_center = int_to_rgb(normal.info.center_color)
            im_center.putpixel(pos, color_center)

            #mean_color = models.IntegerField(null=True)
            color_mean = int_to_rgb(normal.info.mean_color)
            im_mean.putpixel(pos, color_mean)

            #median_color = models.IntegerField(null=True)
            color_median = int_to_rgb(normal.info.median_color)
            im_median.putpixel(pos, color_median)

            #min_color = models.IntegerField(null=True)
            color_min = int_to_rgb(normal.info.min_color)
            im_min.putpixel(pos, color_min)

            #max_color = models.IntegerField(null=True)
            color_max = int_to_rgb(normal.info.max_color)
            im_max.putpixel(pos, color_max)

        # All done, save
        imagepath = os.path.join(TIMELAPSE_DIR, APP_DIR, 'daymaps')

        # Make directory if it doesn't exist
        if not os.path.exists(imagepath):
            os.makedirs(imagepath)

        im_center.save(os.path.join(imagepath, 'center_raw.png'))
        im_mean.save(os.path.join(imagepath, 'mean_raw.png'))
        im_median.save(os.path.join(imagepath, 'median_raw.png'))
        im_min.save(os.path.join(imagepath, 'min_raw.png'))
        im_max.save(os.path.join(imagepath, 'max_raw.png'))

        # Scale
        im_center.resize((1920,1080), Image.BICUBIC).save(os.path.join(imagepath, 'center_hd.png'))
        im_mean.resize((1920,1080), Image.BICUBIC).save(os.path.join(imagepath, 'mean_hd.png'))
        im_median.resize((1920,1080), Image.BICUBIC).save(os.path.join(imagepath, 'median_hd.png'))
        im_min.resize((1920,1080), Image.BICUBIC).save(os.path.join(imagepath, 'min_hd.png'))
        im_max.resize((1920,1080), Image.BICUBIC).save(os.path.join(imagepath, 'max_hd.png'))


