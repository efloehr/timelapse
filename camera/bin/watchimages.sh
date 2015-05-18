#!/bin/bash
source ./globalvars.sh

inotifywait -m --format '%w %f' -e close_write $RAMDISK | while read dir file; do
    echo $dir/$file
    # ./copyimage.sh $dir/$file &
done
