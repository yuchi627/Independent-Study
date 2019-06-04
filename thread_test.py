import time 
import picamera
import cv2
import threading
import numpy as np
import socket
import math
from scikit import compare_ssim

HOST = '192.168.68.195'
PORT = 6667

def detect_nothing(img):
    meanVal = img.mean()
    dif = np.subtract(img,meanVal)

def detect_move(img,prevImg):
    # 0.02 sec/per
    t1 = time.time()
    img = cv2.resize(img,(260,195))
    prevImg = cv2.resize(prevImg,(260,195))
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    prevImg = cv2.cvtColor(prevImg,cv2.COLOR_BGR2GRAY)
    result_sum,grad,S,myssim = compare_ssim(img,prevImg,gradient=True,full=True)
    #print("-------my_mmsim: ",myssim )
    print("result: ",result_sum)
    #print("grad_std: ", np.std(grad))
    #print("S: ",S)
    global count,window,interrupt
    #warning_threshold = 2500000
    warning_threshold = 0.8
    if(result_sum > warning_threshold):
        #print("img =", img)
        detect_nothing(img)
        count += 1
        interrupt = 0
        if(count > 5):
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
packet_size = 10000

try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 80
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
    s.send(("Nadine").ljust(16).encode())

    while True:
        camera.capture("image.jpg",use_video_port = True)
        tmp1 = cv2.imread('image.jpg')
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()
        s.send(str(len(stringData)).ljust(16).encode())
        s.send(stringData)
        sendframe_count = 0
        """
        head = 0
        tail = packet_size
        packets = math.ceil( len(stringData) / packet_size )
        s.send(str(len(stringData)).ljust(16).encode())
        #for i in range(1000):
        #    continue

        for i in range(packets):
            sendbuf = stringData[head:tail]
            s.send(sendbuf)
            head += packet_size
            tail += packet_size
            #print(stringData)

        data = np.fromstring(stringData,dtype='uint8')
        decimg = cv2.imdecode(data,1)
        #cv2.imwrite("client.jpg",decimg)
        """
        compare_count = compare_count + 1
        #print("time: ",te-ts)
        if(compare_count > 8):#8 time approximately 1 sec
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
                s.sendto(msg.ljust(16).encode(),(HOST,PORT))
                #s.recv(1024)
                window_count = 0

            cv2.imshow('picamera',tmp2)
            cv2.waitKey(1)
        else:
            window_count = 0
            #print(window)
            cv2.imshow('picamera',tmp1)
            cv2.waitKey(1)
        #t2 = time.time()
        #print ('time = ' ,t2-t1)
finally:
        camera.close()
        s.close()






