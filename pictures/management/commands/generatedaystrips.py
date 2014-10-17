from django.core.management.base import BaseCommand, CommandError
from django.db import models
from pictures.models import Normal
from pictures.tasks import make_daystrip, make_daystrip_picture, make_daystrip_picture_vert
from datetime import datetime, timedelta
from sky import est
from copy import copy


class Command(BaseCommand):
    def handle(self, *args, **options):
        bounds = Normal.objects.all().aggregate(models.Min('timestamp'), models.Max('timestamp'))
        start = bounds['timestamp__min']
        end = bounds['timestamp__max']

        start_day = datetime(year=start.year, month=start.month, day=start.day)
        end_day = datetime(year=end.year, month=end.month, day=end.day)
        
        current_day = copy(start_day)
        
        while current_day < end_day:
            print('Making task for {0}'.format(current_day))
            make_daystrip.delay('/var/tlwork/daystrip', current_day)
            make_daystrip_picture.delay('/var/tlwork/daystrip_pict', current_day)
            make_daystrip_picture_vert.delay('/var/tlwork/daystrip_pict_vert', current_day)
            current_day += timedelta(days=1)
