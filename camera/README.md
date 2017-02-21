This directory contains the files that go on the Raspberry Pi.

They are in transition... the only thing you really need right now is the timelapse.sh file
in this directory.

As the pi user:

```
# sudo aptitude update
# sudo aptitude upgrade
# sudo apt-get install ntp tmux gphoto2 rsync sendmail inotify-tools python-dev python-setuptools
# sudo easy_install pip
# sudo pip install pillow
# add ~/.forward to point email address cron errors should go to
```

Copy the crontab and timelapse.sh files to the home directory of the pi user.

```
# crontab <crontab
```

Finally, when you attach the camera, put the mode to "view" mode, not "camera" mode.
