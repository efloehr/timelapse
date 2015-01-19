from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import fileinput
from image.models import Normal
import image.tasks as tasks

class Command(BaseCommand):
    args = 'None'
    help = 'Imports a set of timestamped timelapse pictures'
    option_list = BaseCommand.option_list + (
            make_option('--nocheck',
                action='store_false',
                dest='check',
                help='Don\'t check that picture already exists in the database'
                ),
            make_option('--check',
                action='store_true',
                dest='check',
                default=True,
                help='Check if picture already exists in the database (default)'
                )
            )
    
    def handle(self, *args, **options):
        # Make sure our normals are up-to-date
        Normal.update_normals()
        
        # Go through the list of files
        for line in fileinput.input(args):
            # Remove spaces and new lines
            line = line.strip()
            tasks.insert.delay(line)
        

