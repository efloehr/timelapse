#!/usr/bin/env python
# Takes output of rsync -i and uses it to generate tasks
# to process timelapse image files
import sys
import os.path

# First argument should be the base directory for the files from rsync
base_dir = ''
if len(sys.argv) > 1:
    base_dir = sys.argv[1]

for line in sys.stdin:
    # Remove spaces and new lines
    line = line.strip()
    # We only care about files being created with extension .jpg
    if line.startswith('>f') and line.endswith('.jpg'):
        # The file name starts after the status flags
        status, filename = line.split()
        # return filename only
        print(os.path.join(base_dir,filename))