from django.core.management.base import BaseCommand, CommandError
from pictures.models import Normal
from pictures.tasks import make_mosaic_frame, make_sunset_synchro_frame, make_moonset_synchro_frame
from datetime import datetime, timedelta
from sky import est
from optparse import make_option

class Command(BaseCommand):
    help = 'Generates a set of mosaic images synchronized to set times'
    option_list = BaseCommand.option_list + (
            make_option('--body',
                dest='body',
                default='sun',
                help='Which celestial body to synch set to. Current options are "moon" and "sun"'
                ),
            )
    
    def handle(self, *args, **options):
        # Make it easy, start on August 1 and get all normalized times to cycle through
        start = datetime(2013,8,1,tzinfo=est)
        # From 3 hours before to 1 hour after set
        for sequence_no, seconds_before_sunset in enumerate(range(5*60*60, -2*60*60, -10)):
            if options['body'] == 'moon':
                make_moonset_synchro_frame.delay('/var/tlwork/moonset', sequence_no+1, start, seconds_before_sunset, 30, 1920, False, 0,12)
            else:
                make_sunset_synchro_frame.delay('/var/tlwork/sunset', sequence_no+1, start, seconds_before_sunset, 20, 1920, True, 140)
