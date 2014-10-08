from django.core.management.base import BaseCommand, CommandError
from pictures.models import Picture
import pictures.tasks as tasks

class Command(BaseCommand):
    def handle(self, *args, **options):
        pictures = Picture.objects.all()
        for picture in pictures:
            tasks.fix_fstop_exposure.delay(picture.id)
