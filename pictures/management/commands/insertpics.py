from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
import os
import fnmatch
import pictures.tasks


class Command(BaseCommand):
    args = '<directory of pictures>'
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
    
    def handle(self, directory, *args, **options):
        for dirpath, dirs, files in os.walk(directory):
            for f in sorted(fnmatch.filter(files, '2*.jpg')):
                filepath = os.path.join(dirpath, f)
                pictures.tasks.insert.delay(filepath, options['check'])
            self.stdout.write(dirpath)
        self.stdout.write('Complete')

