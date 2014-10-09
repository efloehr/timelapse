from django.core.management.base import BaseCommand, CommandError
from pictures.models import Normal
from pictures.tasks import make_mosaic_frame
from datetime import datetime, timedelta
from sky import est

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Make it easy, start on August 1 and get all normalized times to cycle through
        start = datetime(2013,8,1).replace(tzinfo=est)
        end = start + timedelta(days=1)
        
        frames = Normal.objects.filter(timestamp__gte=start, timestamp__lt=end)
        
        for sequence_no, frame in enumerate(frames):
            make_mosaic_frame.delay('/var/tlwork/mosaic', sequence_no+1, frame.timestamp, 20, 1920, True, 36)
