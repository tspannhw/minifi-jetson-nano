#!/bin/bash

#DATE=$(date +"%Y-%m-%d_%H%M")

#fswebcam -q -r 1280x720 --no-banner /opt/demo/images/$DATE.jpg

python3 -W ignore /opt/demo/2019/jetson-inference/build/aarch64/bin/demo.py   2>/dev/null
