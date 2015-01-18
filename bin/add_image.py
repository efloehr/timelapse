#!/usr/bin/env python
# Takes as input a fully-qualified file name of an image to
# be processed by the timelapse system. Either will come in
# from stdin or as command line arguments
import fileinput
from image.models import Normal

# Make sure our normals are up-to-date
Normal.update_normals()

# Go through the list of files
for line in fileinput.input():
    # Remove spaces and new lines
    line = line.strip()
    # If this line was from the command line, it will have spaces
    for filename in line.split():
        print filename
