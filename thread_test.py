import time 
import picamera
import cv2
import threading
import numpy as np

def detect(img,prevImg):
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
        if(count > 10):
            window = True
            print('warning')
    else:
        if(count!=0):
            count = 0
            if(window):
                window = False

def jumpWindow():
    cv2.namedWindow('Warning',cv2.WINDOW_NORMAL)
    background = np.zeros((600,600,3))
    cv2.putText(background,"Move !",(200,200),cv2.FONT_HERSHEY_COMPLEX,10,(255,255,255),25)
    cv2.waitKey(0)
    global count
    while(count > 10):
        pass
    print("close the window")
    cv2.destroyWindow('Warning')
        
try:
    count = 0
    window = False
    prev = np.zeros((480,640,3))
    prev = prev.astype(np.uint8)
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 80
    cv2.namedWindow('picamera',cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow('picamera',30,30)
    for num in range (0,30):
        start = time.time()
        camera.capture('image.jpg',use_video_port = True)
        end = time.time()
        tmp1 = cv2.imread('image.jpg')
        thread1 = threading.Thread(target = detect, args=(tmp1,prev,))
        thread1.start()
        prev = tmp1.copy()
        if(window):
            cv2.putText(tmp1,"Move!",(20,250),cv2.FONT_HERSHEY_COMPLEX,6,(255,255,255),25)
        print(window)
        cv2.imshow('picamera',tmp1)
        cv2.waitKey(10)
        print (end-start)
finally:
        camera.close()






