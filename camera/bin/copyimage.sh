#!/bin/bash
source ./globalvars.sh

image=$1
imagefile=`basename $image`
datedir=`echo $imagefile | cut -d"-" -f-3,4 | sed -r "s/-([0-9]*)$/\/\1/"`

ssh -c arcfour $NASUSER@$NASSERVER "mkdir -p $datedir" && scp -c arcfour -q $image $NASUSER@$NASSERVER:$datedir && rm $image
