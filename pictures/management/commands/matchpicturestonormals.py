from django.core.management.base import BaseCommand, CommandError
from pictures.models import Normal

class Command(BaseCommand):
    def handle(self, *args, **options):
        Normal.match_pictures()