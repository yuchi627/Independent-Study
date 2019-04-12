import time 
import picamera
import cv2
import threading
import numpy as np
import socket
from scikit import compare_ssim

HOST = '192.168.68.193'
PORT = 6666

def detect_nothing(img):
    meanVal = img.mean()
    dif = np.subtract(img,meanVal)
    #print("dif = " ,dif)
    print("---------------------std = ",np.std(img))

def detect_move(img,prevImg):
    # 0.02 sec/per
    t1 = time.time()
    img = cv2.resize(img,(260,195))
    prevImg = cv2.resize(prevImg,(260,195))
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    prevImg = cv2.cvtColor(prevImg,cv2.COLOR_BGR2GRAY)
    result_sum,grad,S = compare_ssim(img,prevImg,gradient=True,full=True)
    print("result: ",result_sum)
    #print("grad_std: ", np.std(grad))
    #print("S: ",S)
    global count,window,interrupt
    #warning_threshold = 2500000
    warning_threshold = 0.7
    if(result_sum > warning_threshold):
        #print("img =", img)
        detect_nothing(img)
        count += 1
        interrupt = 0
        if(count > 50):
            window = True
            print('warning')
    else:
        interrupt += 1
        if(count!=0):
            count = 0
            interrupt = 0
            if(window):
                window = False
    t2 = time.time()
    #print("compare= ",t2-t1)
    #print('time = ' ,t2-t1)    
    
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

try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 80
    #for num in range (0,30):
    while True:
        #t1 = time.time()
        camera.capture('image.jpg',use_video_port = True)
        tmp1 = cv2.imread('image.jpg')
        compare_count = compare_count + 1
        #print("time: ",te-ts)
        if(compare_count > 8):
            thread1 = threading.Thread(target = detect_move, args=(tmp1,prev,))
            thread1.start()
            compare_count = 0
        prev = tmp1.copy()
        tmp2 = tmp1.copy()

        if(window):
            cv2.putText(tmp2,"Move!",(20,250),cv2.FONT_HERSHEY_COMPLEX,6,(255,255,255),25)
            window_count += 1
            if(window_count > 25):
                msg = 'SOS'
                s.sendto(msg.encode(),(HOST,PORT))
                s.recv(1024)
                window_count = 0
            cv2.imshow('picamera',tmp2)
            cv2.waitKey(10)
        else:
            window_count = 0
            #print(window)
            cv2.imshow('picamera',tmp1)
            cv2.waitKey(10)
        #t2 = time.time()
        #print ('time = ' ,t2-t1)
finally:
        camera.close()
        s.close()






