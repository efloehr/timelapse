from django.core.management.base import BaseCommand, CommandError
from pictures.models import Normal
from pictures.tasks import make_mosaic_frame, make_sunset_synchro_frame
from datetime import datetime, timedelta
from sky import est

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Make it easy, start on August 1 and get all normalized times to cycle through
        start = datetime(2013,8,1,0,0,0).replace(tzinfo=est)
        # From 3 hours before to 1 hour after sunset
        for sequence_no, seconds_before_sunset in enumerate(range(3*60*60, -1*60*60, -1)):
            make_sunset_synchro_frame.delay('/var/tlwork/sunset', sequence_no+1, start, seconds_before_sunset, 20, 1920, True, 140)
