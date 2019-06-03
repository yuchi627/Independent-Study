import sys
import subprocess
import os
from pylepton import Lepton
import cv2
import numpy as np
import time
flir_file_name = sys.argv[1]
move = os.chdir("pylepton")
delay_time = "1"
t1 = time.time()
#take_flir_photo = subprocess.call("./pylepton_capture " + flir_file_name, shell = True)
device = "/dev/spidev0.0"
cv2.namedWindow("flir")
with Lepton(device) as l:
    while(True):
        a,_ = l.capture()
        #print a.dtype
        print np.max(a)
        cv2.normalize(a,a,0,65535,cv2.NORM_MINMAX)
        a = np.right_shift(a,8,a)
        #print np.max(a)
        a = np.uint8(a)
        #print a
        a = cv2.applyColorMap(a,cv2.COLORMAP_JET)
        a = cv2.resize(a,(260,195))
        cv2.imshow("flir",a)
        cv2.waitKey(1)
    #cv2.imwrite(flir_file_name,a)
t2 = time.time()
#print t2-t1

