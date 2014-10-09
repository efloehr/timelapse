from django.db import models
from PIL import Image, ImageStat
import pyxif
import os.path
from datetime import datetime, timedelta
from pytz import utc
from django.utils import timezone
from util import rgb_to_int, normalize_time, get_fstop_exposure
from copy import copy

# Create your models here.
class Picture(models.Model):
    # File info
    filepath = models.CharField(max_length=1024, unique=True)
    filename = models.CharField(max_length=255, unique=True, null=True)
    size = models.IntegerField(default=0)
    timestamp = models.DateTimeField(db_index=True, unique=True, null=True)

    # Exif Info
    fstop = models.IntegerField(null=True) # * 100
    exposure = models.IntegerField(null=True) # in microseconds

    # Color Info (on clouds only)
    center_color = models.IntegerField(null=True)
    mean_color = models.IntegerField(null=True)
    median_color = models.IntegerField(null=True)

    stddev_red = models.IntegerField(null=True)
    stddev_green = models.IntegerField(null=True)
    stddev_blue = models.IntegerField(null=True)

    min_color = models.IntegerField(null=True)
    max_color = models.IntegerField(null=True)

    valid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['timestamp']

    @classmethod
    def insert(cls, filepath, check_for_existing):
        if check_for_existing:
            (pic, created) = cls.objects.get_or_create(filepath=filepath)
        else:
            pic = cls()
        try:
            # Load image, exif, and file information
            im = Image.open(filepath)
            dummy, exif_dict, dummy = pyxif.load(filepath)
            filestat = os.stat(filepath)
            
            # Image stats for calculations
            width = 2048
            height = 1536
            top_row = 36
            hd_height = int(round((width * 1080) / 1920))
            bottom_row = hd_height + top_row
    
            # File stats
            pic.filepath = filepath
            pic.filename = os.path.basename(filepath)
            pic.size = filestat.st_size
    
            # Timestamp (UTC) 2014-06-16-00-00-02.jpg
            timestamp = datetime.strptime(pic.filename.split('.')[0], '%Y-%m-%d-%H-%M-%S')
            pic.timestamp = timezone.make_aware(timestamp, utc)
            
            # Exif Info
            pic.fstop, pic.exposure = get_fstop_exposure(exif_dict)
    
            # Color info (Clouds only)
            imclouds = im.crop((0,top_row,width,bottom_row))
            cloudstats = ImageStat.Stat(imclouds)
            exc = cloudstats.extrema
    
            pic.center_color = rgb_to_int(imclouds.getpixel((int(round(width / 2.0)),int(round(hd_height / 2.0)))))
            pic.mean_color = rgb_to_int(cloudstats.mean)
            pic.median_color = rgb_to_int(cloudstats.median)
            pic.stddev_red = int(round(cloudstats.stddev[0]))
            pic.stddev_green = int(round(cloudstats.stddev[1]))
            pic.stddev_blue = int(round(cloudstats.stddev[2]))
            pic.min_color = rgb_to_int((exc[0][0], exc[1][0], exc[2][0]))
            pic.max_color = rgb_to_int((exc[0][1], exc[1][1], exc[2][1]))
    
            pic.valid = True
    
            if im.size != (2048,1536):
                pic.valid = False
        except:
            pic.valid = False

        pic.save()


class Normal(models.Model):
    timestamp = models.DateTimeField(db_index=True)
    picture = models.ForeignKey(Picture, null=True)
    
    class Meta:
        ordering = ['timestamp']


    @classmethod
    def insert_normals(cls):
        bounds = Picture.objects.all().aggregate(models.Min('timestamp'), models.Max('timestamp'))
        start = bounds['timestamp__min']
        end = bounds['timestamp__max']

        normalized_start = normalize_time(start, 10)
        normalized_end = normalize_time(end, 10)
        
        current_time = copy(normalized_start)
        
        while current_time <= normalized_end:
            time_entry, created = cls.objects.get_or_create(timestamp=current_time)
            current_time = current_time + timedelta(seconds=10)
        

    @classmethod
    def match_pictures(cls):
        pictures = Picture.objects.all()
        
        for picture in pictures:
            normalized_time = normalize_time(picture.timestamp, 10)
            time_entry, created = cls.objects.get_or_create(timestamp=normalized_time)
            if time_entry.picture is not None:
                # Is the previous normalized time entry there, if so, move current to that one and place this one here
                previous_time_entry, created = cls.objects.get_or_create(timestamp=normalized_time - timedelta(seconds=10))
                if previous_time_entry.picture is None:
                    previous_time_entry.picture = time_entry.picture
                    time_entry.picture = picture
                    previous_time_entry.save()
                    time_entry.save()
                else:
                    print("Existing picture at {0} ({2}) and at {1} ({3})".format(
                        time_entry.timestamp, previous_time_entry.timestamp, time_entry.picture_id, previous_time_entry.id))
                    print("    Won't enter {0} ({1})".format(picture.timestamp, picture.id))
            else:
                time_entry.picture = picture
                time_entry.save()
                if created:
                    print("Had to create normal entry for {0}".format(normalized_time))
            