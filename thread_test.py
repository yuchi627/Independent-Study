import time 
import picamera
import cv2
import threading
import numpy as np

def detect(img,prevImg):
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #if (np.sum(prevImg)>0):
    prevImg = cv2.cvtColor(prevImg,cv2.COLOR_BGR2GRAY)
    img = img.astype(np.int16)
    prevImg = prevImg.astype(np.int16)
    #cv2.normalize(i
    result = np.subtract(img,prevImg)
    result = abs(result)
    print('sum = ')
    result_sum = np.sum(result)
    print(result_sum)
    global count
    if(result_sum < 2500000):
        count += 1
        if(count > 10):
            print('warning')
    else:
        if(count!=0):
            count = 0


        
try:
    count = 0
    prev = np.zeros((480,640,3))
    prev = prev.astype(np.uint8)
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 80
    cv2.namedWindow('picamera',cv2.WINDOW_NORMAL)
    for num in range (0,30):
        start = time.time()
        camera.capture('image.jpg',use_video_port = True)
        end = time.time()
        tmp1 = cv2.imread('image.jpg')
        thread1 = threading.Thread(target = detect, args=(tmp1,prev,))
        thread1.start()
        prev = tmp1
        cv2.imshow('picamera',tmp1)
        cv2.waitKey(10)
        print (end-start)
finally:
        camera.close()






