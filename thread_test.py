import time 
import picamera
import cv2
import threading
import numpy as np
import socket
import math
import subprocess
from scikit import compare_ssim
from pylepton import Lepton
import select

HOST = '192.168.68.196'
PORT = 6667

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton(device) as l:
    a,_ = l.capture()
    b = np.copy(a)
  if flip_v:
    cv2.flip(a,0,a)
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a), np.uint16(b)

def fill_color(img, color):
    img = img.astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img * color
    return img

def classfy(flir_val):
    th_70 = 7680        #8900
    th_100 = 7700       #9650
    flir_val = cv2.resize(flir_val,(640,480))
    print(np.max(flir_val))
    print(np.min(flir_val))
    first = np.where(flir_val < th_70, 1, 0)
    second_1 = np.where(flir_val >= th_70, 1, 0)
    second_2 = np.where(flir_val >= th_100, 0, 1)
    second = np.bitwise_and(second_1,second_2)
    third = np.where(flir_val >= th_100, 1, 0)
    first = fill_color(first,(255,0,0))
    second = fill_color(second,(0,255,0))
    third = fill_color(third,(0,0,255))
    fusion = first + second + third
    return fusion

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
request_flag = 0

try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 40
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
    s.send(("Nadine").ljust(16).encode())
    save_msg_count = 0
    #pic_count = 0
    while True:
    #while(pic_count<100):
        #pic_count+=1
        
        flir_img2, flir_val = capture()
        t1 = time.time()
        camera.capture("ir1.jpg",use_video_port = True)
        t2 = time.time()
        print("time = ",t2-t1)
        tmp1 = cv2.imread('ir1.jpg')
        flir_img2 = cv2.applyColorMap(flir_img2, cv2.COLORMAP_JET)
        cv2.imwrite('flir1.jpg',flir_img2)
        #print(flir_img.shape[0],flir_img.shape[1])
        flir_img = cv2.resize(flir_img2,(640,480))
        #flir_img = flir_img2
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()
        s.send(str(len(stringData)).ljust(16).encode())
        s.send(stringData)
        sendframe_count = 0
        compare_count = compare_count + 1
        if(compare_count > 8):#8 time approximately 1 sec
            thread1 = threading.Thread(target = detect_move, args=(tmp1,prev,))
            thread1.start()
            compare_count = 0
            prev = tmp1.copy()
        tmp1 = cv2.resize(tmp1,(640,480))
        tmp1 = cv2.cvtColor(tmp1,cv2.COLOR_BGR2GRAY)
        tmp1 = np.dstack([tmp1]*3)
        ir_height = tmp1.shape[0]
        ir_weight = tmp1.shape[1]
        white = tmp1.copy()
        classfy_color = classfy(flir_val)
        flir_tmp = cv2.resize(classfy_color,(ir_weight-120,ir_height-100),interpolation = cv2.INTER_CUBIC)
        #flir_tmp = cv2.resize(flir_img,(ir_weight-120,ir_height-100),interpolation = cv2.INTER_CUBIC)
        flir_height = flir_tmp.shape[0]
        flir_weight = flir_tmp.shape[1]
        move_y = 24
        move_x = 50
        white[move_y:move_y+flir_height,move_x:move_x+flir_weight] = flir_tmp
        img_combine = cv2.addWeighted(tmp1,0.8,white,0.2,0)
        cv2.imshow("combine",img_combine)
        tmp2 = tmp1.copy()

        if(window):
            cv2.putText(tmp2,"Move!",(20,250),cv2.FONT_HERSHEY_COMPLEX,6,(255,255,255),25)
            window_count += 1
            if(window_count > 25):
                msg = 'SOS'
                s.sendto(msg.ljust(16).encode(),(HOST,PORT))
                request_flag = 1
                #s.recv(1024)
                window_count = 0
            t1 = time.time()
            if(request_flag == 1):
                ready = select.select([s],[],[],0.05)
                if(ready[0]):
                    recv_data = s.recv(20)
                    if("I will save you" in recv_data.decode()):
                        save_msg_count = 10
                        request_flag = 0
            if(save_msg_count):
                save_msg_count -= 1
                cv2.putText(tmp2,"Got it!",(20,250),cv2.FONT_HERSHEY_COMPLEX,4,(255,255,255),25)
            t2 = time.time()
            cv2.imshow('flir',flir_img)
            cv2.imshow('picamera',tmp2)
            cv2.waitKey(1)
        else:
            window_count = 0
            #print(window)
            cv2.imshow('flir',flir_img)
            cv2.imshow('picamera',tmp1)
            cv2.waitKey(1)
finally:
        camera.close()
        s.close()






