import time 
import picamera
import cv2
import threading
import numpy as np
import socket
import math
from scikit import compare_ssim

HOST = '192.168.208.112'
PORT = 6667
height = 240
weight = 320
count = 0
compare_count=0
interrupt = 0
window_count = 0
window = False
prev = np.zeros((480,640,3))
prev = prev.astype(np.uint8)
cv2.namedWindow('picamera',cv2.WINDOW_AUTOSIZE)
cv2.moveWindow('picamera',30,30)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
packet_size = 10000
count = 1
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
try:
    s.send(("Sending").ljust(16).encode())
    while True:
        tmp1 = cv2.imread('ir'+str(count)+'.jpg')
        result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()
        s.send(str(len(stringData)).ljust(16).encode())
        s.send(stringData)
        count += 1
        if(count>99):
            count = 1

finally:
        s.close()
