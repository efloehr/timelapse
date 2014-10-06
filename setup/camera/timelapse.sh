#!/bin/bash

RAMDISK=/pics
GPHOTO=gphoto2

# Check for existence of pics RAMdisk
if [ ! -d "$RAMDISK" ]; then
  sudo mkdir -p $RAMDISK
  sudo chmod 777 $RAMDISK
fi

# Mount RAMdisk if not already mounted
mountpoint -q $RAMDISK || sudo mount -t tmpfs -o size=250m tmpfs $RAMDISK

# Check for picture files existing in RAMdisk and move to server
if [ "$(ls -A $RAMDISK | sort | head -n -1)" ]; then
  for image in `ls $RAMDISK/*.jpg | sort | head -n -1`; do
    imagefile=`basename $image`
    daydir=`echo $imagefile | cut -d"-" -f-3`
    hourdir=`echo $imagefile | cut -d"-" -f4`
    datedir=$daydir/$hourdir
    ssh -c arcfour timelapse@eve "mkdir -p $datedir" && scp -c arcfour -q $image timelapse@eve:$datedir && rm $image
  done
  # Link to most current image
  ssh -c arcfour timelapse@eve "ln -sf $datedir/$imagefile current.jpg"
else
    echo "No image files found!"
fi

# Only run gphoto timelapse if not already
if [ -z "$(pgrep $GPHOTO)" ]; then
  # Turn on lens and other options
  $GPHOTO --set-config capture=1

  # Lock focus to infinity, don't save to card, just memory, superfine, no AF assist light or flash
  $GPHOTO --set-config focuslock=1 --set-config capturetarget=1 --set-config imagequality=2 --set-config assistlight=0 --set-config flashmode=0

  # Run forever
  cd $RAMDISK
  $GPHOTO --capture-image-and-download --filename "%Y-%m-%d-%H-%M-%S.jpg" --quiet -I 10 >> /dev/null &
fi

