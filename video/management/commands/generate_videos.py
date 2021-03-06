from django.core.management.base import BaseCommand, CommandError
from datetime import date, timedelta
from copy import copy
from video.tasks import make_daylight_video, make_overnight_video
from util import day_generator


class Command(BaseCommand):
    args = '<start date> <end date>'
    help = 'Makes day and night videos for dates between the two dates. If only one date, it will make for that day, if none, for yesterday.'
    
    def handle(self, *args, **options):
        start_day = end_day = None
        
        if len(args) > 0:
            start_day = args[0]
        
        if len(args) > 1:
            end_day = args[1]

        for day in day_generator(start_day, end_day):
            make_daylight_video.delay(day)
            make_overnight_video.delay(day)
        
        
