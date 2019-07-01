#!/bin/bash



DATE=$(date +"%Y-%m-%d_%H%M")



fswebcam -q -r 1280x720 --no-banner /opt/demo/images/$DATE.jpg



/opt/demo/jetson-inference/build/aarch64/bin/imagenet-console  /opt/demo/images/$DATE.jpg  /opt/demo/images/out_$DATE.jpg
