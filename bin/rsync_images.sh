#! /usr/bin/bash
SOURCE_DIR=/misc/timelapse/
DEST_DIR  = /mnt/timelapse/

# Set up environment
workon time
cd /home/efloehr/dev/timelapse/bin

# Copy new files
rsync -ai $SOURCE_DIR $DEST_DIR | ./rsync_get_files.py $DEST_DIR | ./add_image.py