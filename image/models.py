from django.db import models, transaction
from PIL import Image, ImageStat
import pyxif
import os.path
from datetime import datetime, timedelta
from pytz import utc
from django.utils import timezone
from util import rgb_to_int, normalize_time, get_fstop_exposure
from copy import copy
from sky import est

# Create your models here.
class Info(models.Model):
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
    def insert(cls, filepath, check_for_existing=True):
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
        return pic


class Normal(models.Model):
    timestamp = models.DateTimeField(db_index=True)
    info = models.ForeignKey(Info, null=True)
    
    SECONDS_BASE = 10
    
    class Meta:
        ordering = ['timestamp']


    @classmethod
    @transaction.atomic
    def insert_normals(cls, start_time=None, end_time=None):
        if start_time is None:
            bounds = Info.objects.all().aggregate(models.Min('timestamp'))
            if len(bounds) == 0:
                return
            start_time = bounds['timestamp__min']
            
        if end_time is None:
            end_time = datetime.utcnow().replace(tzinfo=utc)

        normalized_start = normalize_time(start_time, cls.SECONDS_BASE)
        normalized_end = normalize_time(end_time, cls.SECONDS_BASE)
        
        current_time = copy(normalized_start)
        print current_time, normalized_end 
        while current_time <= normalized_end:
            time_entry, created = cls.objects.get_or_create(timestamp=current_time)
            current_time = current_time + timedelta(seconds=cls.SECONDS_BASE)
    
    
    @classmethod
    @transaction.atomic
    def update_normals(cls):
        bounds = cls.objects.all().aggregate(models.Max('timestamp'))
        if len(bounds) == 0:
            return
        start_time = bounds['timestamp__max']
        return cls.insert_normals(start_time)
    

    @classmethod
    @transaction.atomic
    def match_image(cls, image_info, normal_entry=None, rejected_normal=None):
        # Get the normalized time for the image
        normalized_time = normalize_time(image_info.timestamp, cls.SECONDS_BASE)

        # Get a normal entry if not provided one
        if normal_entry is None:
            normal_entry, created = cls.objects.get_or_create(timestamp=normalized_time)
            
        # If the normal doesn't already have an associated image, we are done
        if normal_entry.info is None:
            normal_entry.info = image_info
            normal_entry.save()
            return normal_entry
        # Or if the normal already has the one we are looking to match
        elif normal_entry.info == normal_entry:
            return normal_entry

        # We have to decide which is better
        new_diff = abs(normal_entry.timestamp - image_info.timestamp)
        old_diff = abs(normal_entry.timestamp - normal_entry.info.timestamp)
        rejected_image = image_info
        
        # Replace the existing image if the new one is closer
        if new_diff < old_diff:
            rejected_image = normal_entry.info
            normal_entry.info = image_info
            normal_entry.save()
            
        # We now have a rejected image to deal with, do we go up or down?
        if image_info.timestamp < normalized_time:
            new_normalized_time = normalized_time - timedelta(seconds=cls.SECONDS_BASE)
        elif image_info.timestamp > normalized_time:
            new_normalized_time = normalized_time + timedelta(seconds=cls.SECONDS_BASE)
        else:
            # If we reject and it's equal, give up, we can't do better
            return None
        
        # Try with new normal
        new_normal_entry, created = cls.objects.get_or_create(timestamp=new_normalized_time)
        
        # But only if the new normal isn't the one we just rejected
        if new_normal_entry == normal_entry:
            return None
        
        return cls.match_image(image_info, normal_entry=new_normal_entry, rejected_normal=normal_entry)

    @classmethod
    def match_images(cls, start_normal=None, end_normal=None, dryrun=False):
        bounds = Info.objects.all().aggregate(models.Min('timestamp'), models.Max('timestamp'))
        last_info_timestamp = Normal.objects.all().aggregate(models.Max('info__timestamp'))
        if start_normal is None:
            try:
                start_time = last_info_timestamp['info__timestamp__max']
            except KeyError:
                if len(bounds) == 0:
                    return
                start_time = bounds['timestamp__min']
        else:
            start_time = start_normal.timestamp
            
        if end_normal is None:
            end_time = bounds['timestamp__max']
        else:
            end_time = end_normal.timestamp
            
        print("Matching from {0} to {1}".format(start_time, end_time))
        
        normals = Normal.objects.filter(timestamp__gte=start_time, timestamp__lte=end_time)
        images = Info.objects.filter(timestamp__gte=start_time - timedelta(seconds=cls.SECONDS_BASE),
                                     timestamp__lte=end_time + timedelta(seconds=cls.SECONDS_BASE))

        if len(images) == 0:
            print("No images for range {0} to {1}".format(start_time, end_time))
            return
        
        if len(normals) == 0:
            cls.insert_normals(start_time, end_time)
            normals = Normal.objects.filter(timestamp__gte=start_time, timestamp__lte=end_time)
            
        image_index = 0
        current_image = images[image_index]
        previous_image = None
        normal = normals[0]
        
        # First normal want to get as close as possible
        normalized_image_timestamp = normalize_time(current_image.timestamp, cls.SECONDS_BASE)
        while normalized_image_timestamp != normal.timestamp:
            try:
                image_index += 1
                current_image = images[image_index]
                normalized_image_timestamp = normalize_time(current_image.timestamp, cls.SECONDS_BASE)
            except IndexError:
                return
        
        if normal.info is not None:
            previous_normal_info_timestamp = normal.info.timestamp
        else:
            previous_normal_info_timestamp = None
        
        if previous_image is None or \
           abs(normal.timestamp - current_image.timestamp) <= abs(normal.timestamp - previous_image.timestamp):
            normal.info = current_image
            image_index += 1
            current_image = images[image_index]
        else:
            normal.info = previous_image
            
        print("{0} from {1} to {2}".format(normal.timestamp, previous_normal_info_timestamp, normal.info.timestamp))
        if not dryrun:
            normal.save()
        
        # Now just keep going and don't skip until we have a delta greater than SECONDS_BASE
        normal_iterator = iter(normals[1:])
        for normal in normal_iterator:
            diff_seconds = (current_image.timestamp - normal.timestamp).total_seconds()
            if abs(diff_seconds) <= cls.SECONDS_BASE:
                # That's exactly what we want
                pass
            else:
                if current_image.timestamp < normal.timestamp:
                    # Walk up the image to the normal
                    while normalize_time(current_image.timestamp, cls.SECONDS_BASE) < normal.timestamp:
                        image_index += 1
                        print("Incrementing current image from {0} to next".format(normal.timestamp))
                        current_image = images[image_index]
                    # Now we may need to walk the normal to the image

                # Walk up the normal to the image
                normalized_image_timestamp = normalize_time(current_image.timestamp, cls.SECONDS_BASE)
                while normalized_image_timestamp != normal.timestamp:
                    print("Walking normal from {0} to {1}".format(normal.timestamp, normalized_image_timestamp))
                    if normal.info is not None:
                        previous_normal_info_timestamp = normal.info.timestamp
                    else:
                        previous_normal_info_timestamp = None
                    normal.info = None
                    if not dryrun:
                        normal.save()
                    print("{0} from {1} to {2}".format(normal.timestamp, previous_normal_info_timestamp, None))
                    normal = next(normal_iterator)
           
            if normal.info is not None:
                previous_normal_info_timestamp = normal.info.timestamp
            else:
                previous_normal_info_timestamp = None

            normal.info = current_image
            image_index += 1
            current_image = images[image_index]
            print("{0} from {1} to {2} [{3}]".format(normal.timestamp, previous_normal_info_timestamp,
                                                     normal.info.timestamp, diff_seconds))
            if not dryrun:
                normal.save()
            
            
class Product(models.Model):
    ALLNIGHT     = 1
    ALLNIGHT_NEG = 2
    DAYSTRIP     = 3
    DAYSTRIP_PIC = 4
    ALLDAY_LIGHT = 5
    ALLDAY_DARK  = 6
    KINDS = (
        (ALLNIGHT,     "All-night overlay image"),
        (ALLNIGHT_NEG, "All-night overlay image negative"),
        (DAYSTRIP,     "Classic daystrip"),
        (DAYSTRIP_PIC, "Daystrip that goes from left to right and is each column in the image"),
        (ALLDAY_LIGHT, "All-day lightest overlay image"),
        (ALLDAY_DARK, "All-day darkest overlay image negative"),
    )

    # Metadata
    day = models.DateField(db_index=True, null=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    kind = models.SmallIntegerField(choices=KINDS)

    # File Info
    filepath = models.CharField(max_length=1024, unique=True)
    filename = models.CharField(max_length=255)
    size = models.BigIntegerField(default=-1)

    class Meta:
        ordering = ['day']
