from django.core.management.base import BaseCommand, CommandError
from pictures.models import Picture
import pictures.tasks as tasks

class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Loading pictures...")
        pictures = Picture.objects.all()
        self.stdout.write("Loaded {0} pictures".format(len(pictures)))
        for picture in pictures:
            tasks.fix_fstop_exposure.delay(picture.id)
        self.stdout.write("Complete")