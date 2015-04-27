#!/bin/bash
source ./globalvars.sh

# Check for existence of pics RAMdisk
if [ ! -d "$RAMDISK" ]; then
  sudo mkdir -p $RAMDISK
  sudo chmod 777 $RAMDISK
fi

# Mount RAMdisk if not already mounted
mountpoint -q $RAMDISK || sudo mount -t tmpfs -o size=384m tmpfs $RAMDISK

# Check for older picture files existing in RAMdisk and move to server
for image in `find $RAMDISK -name "*.jpg" -mmin +5 | sort`; do
  ./copyimage.sh $image
done

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

