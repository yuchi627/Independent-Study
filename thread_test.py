import time 
import picamera
import cv2
import threading
import numpy as np
import socket

HOST = '192.168.68.193'
PORT = 6666

def detect(img,prevImg):
    # 0.02 sec/per
    t1 = time.time()
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    prevImg = cv2.cvtColor(prevImg,cv2.COLOR_BGR2GRAY)
    img = img.astype(np.int16)
    prevImg = prevImg.astype(np.int16)
    result = np.subtract(img,prevImg)
    result = abs(result)
    print('sum = ')
    result_sum = np.sum(result)
    print(result_sum)
    global count,window
    if(result_sum < 2500000):
        count += 1
        if(count > 50):
            window = True
            print('warning')
    else:
        if(count!=0):
            count = 0
            if(window):
                window = False
    t2 = time.time()
    print('time = ' ,t2-t1)

count = 0
window_count = 0
window = False
prev = np.zeros((480,640,3))
prev = prev.astype(np.uint8)
cv2.namedWindow('picamera',cv2.WINDOW_AUTOSIZE)
cv2.moveWindow('picamera',30,30)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 80
    #for num in range (0,30):
    while True:
        #t1 = time.time()
        camera.capture('image.jpg',use_video_port = True)
        tmp1 = cv2.imread('image.jpg')
        thread1 = threading.Thread(target = detect, args=(tmp1,prev,))
        thread1.start()
        prev = tmp1.copy()
        if(window):
            cv2.putText(tmp1,"Move!",(20,250),cv2.FONT_HERSHEY_COMPLEX,6,(255,255,255),25)
            window_count += 1
            if(window_count > 25):
                s.send('SOS')
                s.recv(1024)
                window_count = 0
        else:
            window_count = 0
        print(window)
        cv2.imshow('picamera',tmp1)
        cv2.waitKey(10)
        #t2 = time.time()
        #print ('time = ' ,t2-t1)
finally:
        camera.close()
        s.close()






