import time
import sys
import datetime
import subprocess
import sys
import os
import datetime
import traceback
import math
import base64
import json
from time import gmtime, strftime
import random, string
import time
from time import gmtime, strftime
import random, string
import psutil
import base64
import uuid
# Importing socket library 
import socket 

import jetson.inference
import jetson.utils

import argparse

external_IP_and_port = ('198.41.0.4', 53)  # a.root-servers.net
socket_family = socket.AF_INET

def IP_address():
        try:
            s = socket.socket(socket_family, socket.SOCK_DGRAM)
            s.connect(external_IP_and_port)
            answer = s.getsockname()
            s.close()
            return answer[0] if answer else None
        except socket.error:
            return None

# Get MAC address of a local interfaces
def psutil_iface(iface):
    # type: (str) -> Optional[str]
    import psutil
    nics = psutil.net_if_addrs()
    if iface in nics:
        nic = nics[iface]
        for i in nic:
            if i.family == psutil.AF_LINK:
                return i.address
# Random Word
def randomword(length):
 return ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ".lower()) for i in range(length))

# Timer
start = time.time()
packet_size=3000

# Create unique id
uniqueid = 'nano_uuid_{0}_{1}'.format(randomword(3),strftime("%Y%m%d%H%M%S",gmtime()))
uuid = '{0}_{1}'.format(strftime("%Y%m%d%H%M%S",gmtime()),uuid.uuid4())

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)

# image output
filename = '/opt/demo/images/image_{0}_{1}.jpg'.format(randomword(3),strftime("%Y%m%d%H%M%S",gmtime()))
filename2 = '/opt/demo/images/out_{0}_{1}.jpg'.format(randomword(3),strftime("%Y%m%d%H%M%S",gmtime()))

# CPU Temp
f = open("/sys/devices/virtual/thermal/thermal_zone1/temp","r")
cputemp = str( f.readline() )
cputemp = cputemp.replace('\n','')
cputemp = cputemp.strip()
cputemp = str(round(float(cputemp)) / 1000)
cputempf = str(round(9.0/5.0 * float(cputemp) + 32))
f.close()
# GPU Temp
f = open("/sys/devices/virtual/thermal/thermal_zone2/temp","r")
gputemp = str( f.readline() )
gputemp = gputemp.replace('\n','')
gputemp = gputemp.strip()
gputemp = str(round(float(gputemp)) / 1000)
gputempf = str(round(9.0/5.0 * float(gputemp) + 32))
f.close()
 
width = 1280
height=720
camera = "/dev/video0"

# create the camera and display
camera = jetson.utils.gstCamera(width, height, camera)
camera.Open()
img, width, height = camera.CaptureRGBA(zeroCopy=1)

ipaddress = IP_address()

network="ssd-mobilenet-v2"
overlay="box,labels,conf"
threshold = 0.5
argv =[]

# load the object detection network
net = jetson.inference.detectNet(network, argv, threshold)

# detect objects in the image (with overlay)
detections = net.Detect(img, width, height, overlay)

# print the detections
print("detected {:d} objects in image".format(len(detections)))

dconfidence = 0
dleft = 0
dtop = 0
dright = 0
dbottom = 0
dwidth = 0
dheight = 0
darea = 0
dcenter = 0

for detection in detections:
        print(detection)
        dconfidence = detection.Confidence
        dleft = detection.Left

# print out timing info
net.PrintProfilerTimes()

   # -- Center:  (674.339, 367.445)



jetson.utils.cudaDeviceSynchronize()
jetson.utils.saveImageRGBA(filename2, img, width, height)
net.PrintProfilerTimes()
end = time.time()
row = { }

row['uuid'] =  uniqueid
row['ipaddress']=ipaddress
row['networktime'] = net.GetNetworkTime() 
row['detectleft']= dleft
row['detectconfidence'] = (dconfidence        *100)
#row['top1pct'] =  (confidence * 100)
#row['top1'] =  class_desc 
row['cputemp'] =  cputemp 
row['gputemp'] =  gputemp 
row['gputempf'] =  gputempf
row['cputempf'] =  cputempf
row['runtime'] = str(round(end - start)) 
row['host'] = os.uname()[1]
row['filename'] = filename2
row['host_name'] = host_name
row['macaddress'] = psutil_iface('wlan0')
row['end'] = '{0}'.format( str(end ))
row['te'] = '{0}'.format(str(end-start))
row['systemtime'] = datetime.datetime.now().strftime('%m/%d/%Y %H:%M:%S')
row['cpu'] = psutil.cpu_percent(interval=1)
usage = psutil.disk_usage("/")
row['diskusage'] = "{:.1f} MB".format(float(usage.free) / 1024 / 1024)
row['memory'] = psutil.virtual_memory().percent
row['id'] = str(uuid)
json_string = json.dumps(row)
fa=open("/opt/demo/logs/detect.log", "a+")
fa.write(json_string + "\n")
fa.close()
