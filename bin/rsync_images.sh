#! /usr/bin/bash
SOURCE_DIR=/misc/timelapse/
DEST_DIR  = /mnt/timelapse/

# Set up environment
workon time
cd /home/efloehr/dev/timelapse/

# Copy new files
rsync -ai $SOURCE_DIR $DEST_DIR | bin/rsync_get_files.py $DEST_DIR | python manage.py insert_images