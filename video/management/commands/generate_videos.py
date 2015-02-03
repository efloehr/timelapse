from django.core.management.base import BaseCommand, CommandError
from datetime import date, timedelta
from copy import copy
from video.tasks import make_daylight_video, make_overnight_video


class Command(BaseCommand):
    args = '<start date> <end date>'
    help = 'Makes day and night videos for dates between the two dates. If only one date, it will make for that day, if none, for yesterday.'
    
    def handle(self, *args, **options):
        if len(args) == 0:
            start_date = date.today() - timedelta(day=1)
        elif len(args) > 0:
            year, month, day = [ int(x) for x in args[0].split('-') ]
            start_date = date(year, month, day)
        
        if len(args) > 1:
            year, month, day = [ int(x) for x in args[1].split('-') ]
            end_date = date(year, month, day)
        else:
            end_date = start_date
            
        current_day = copy(start_date)
        
        while current_day <= end_date:
            print('Making task for {0}'.format(current_day))
            make_daylight_video.delay(current_day)
            make_overnight_video.delay(current_day)
            current_day += timedelta(days=1)
        
        
