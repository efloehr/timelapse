from django.core.management.base import BaseCommand, CommandError
from datetime import date, timedelta
from copy import copy
from image.tasks import make_all_night_image, make_daystrip, make_daystrip_picture, make_all_day_image
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
            make_all_night_image.delay(day)
            make_all_day_image.delay(day)
            make_daystrip.delay(day)
            make_daystrip_picture.delay(day)
