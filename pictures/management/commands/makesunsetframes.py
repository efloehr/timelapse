from django.core.management.base import BaseCommand, CommandError
from pictures.tasks import make_sunset_frames
import os.path
from datetime import datetime
from sky import est


class Command(BaseCommand):
    def handle(self, *args, **options):
        basedir = '/var/tlwork/sunset-movies'
        start_day = datetime(2013,7,6,tzinfo=est)
        for time in range(-30,-375,-15):
            print('Making task for {0} minutes before sunset'.format(time))
            directory = os.path.join(basedir, 't{0:+0d}m'.format(time))
            make_sunset_frames.delay(directory, start_day, time * 60)
