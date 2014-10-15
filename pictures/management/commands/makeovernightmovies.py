from django.core.management.base import BaseCommand, CommandError
from django.db import models
from pictures.models import Normal
from datetime import datetime, timedelta
from copy import copy
from pictures.tasks import make_overnight_movie

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
            make_overnight_movie.delay(current_day)
            current_day += timedelta(days=1)
