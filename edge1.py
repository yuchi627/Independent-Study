import time 
import picamera
import cv2
import threading
import numpy as np
import socket
import math
import subprocess
from pylepton import Lepton
import select
import picamera.array

HOST = '192.168.208.140'
PORT = 8888

def img_capture(l):
    global ir_img,flir_val,s,flir_img
    t0 = time.time()
    a,_ = l.capture()
    b = np.copy(a)

    cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(a, 8, a)
    flir_img = np.uint8(a)
    flir_val = np.uint16(b)

    
    t1 = time.time()
    ir_img = np.empty((480,640,3),dtype = np.uint8)

    try:
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        result, imgencode = cv2.imencode('.jpg',ir_img,encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()
        #print("before")
        s.send(str(len(stringData)).ljust(16).encode())
        #print("after1")
        s.send(stringData)
        #print("after2")
    except:
        print("except")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST,PORT))
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
            s.send(("Nadine").ljust(16).encode())
        except:
            pass


#def img_processing(ir_img,flir_val):
def img_processing():
    global img_combine,ir_img,flir_img,dst, flir_val
    #flir_img = cv2.applyColorMap(flir_img,cv2.COLORMAP_JET)
    #flir_img = cv2.resize(flir_img,(ir_weight,ir_height),interpolation = cv2.INTER_CUBIC)
    tmp = ir_img.copy()
    flir_val =  cv2.resize(flir_val,(ir_weight,ir_height),interpolation = cv2.INTER_CUBIC)
    flir_val = np.dstack([flir_val]*3)
    dst = cv2.warpPerspective(flir_val,matrix,(ir_weight,ir_height))
    #dst2 = cv2.warpPerspective(flir_img,matrix,(ir_weight,ir_height))
    np.place(tmp,(dst>th_100),(0,0,255))    #red
    np.place(tmp,((dst>th_70) & (dst<=th_100)), (163,255,197))  #green
    img_combine = cv2.addWeighted(ir_img,0.5,tmp,0.5,0)
    #img_combine2 = cv2.addWeighted(ir_img,0.5,dst2,0.5,0)


count = 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
packet_size = 10000
request_flag = 0
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
flir_height = 380   #flir_tmp.shape[0]
flir_weight = 520   #flir_tmp.shape[1]
move_y = 24
move_x = 50
th_70 = 0        #8900
th_100 = 0       #9650
refresh = False
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
img_combine2 = np.zeros((ir_height,ir_weight,3),np.uint8)
ir_img = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
matrix = np.loadtxt('matrix2.txt',delimiter = ',')
try:
    #cv2.namedWindow("combine2",cv2.WINDOW_NORMAL)
    cv2.namedWindow("combine",cv2.WINDOW_NORMAL)
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 40
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
    s.send(("Nadine").ljust(16).encode())
    save_msg_count = 0

    device = "/dev/spidev0.0"
    with Lepton(device) as l:
        a,_ = l.capture()
        b = np.copy(a)
        cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
        np.right_shift(a, 8, a)
        flir_img = np.uint8(a)
        flir_val = np.uint16(b)
        val_min = np.min(flir_val)
        diff = np.max(flir_val)-val_min
        th_70 = diff * 0.6 + val_min
        th_100 = diff * 0.8 + val_min

        while True:
            t0 = time.time()
            a,_ = l.capture()
            b = np.copy(a)

            cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
            np.right_shift(a, 8, a)
            flir_img = np.uint8(a)
            flir_val = np.uint16(b)
                        #print("flir",t1-t0)
            ir_img = np.empty((480,640,3),dtype = np.uint8)
            camera.capture(ir_img,'bgr',use_video_port = True)
            try:
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
                result, imgencode = cv2.imencode('.jpg',ir_img,encode_param)
                data = np.array(imgencode)
                stringData = data.tostring()
                s.send(("SIZE"+str(len(stringData))).ljust(16).encode())
                s.send(stringData)
            except:
                print("except")
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((HOST,PORT))
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
                    s.send(("Nadine").ljust(16).encode())
                except:
                    pass
            #img_capture(l)
            img_processing()
            t2 = time.time()
            #print("process: ",t2-t1)

            cv2.imshow("combine",img_combine)
            cv2.waitKey(1)
                
finally:
        camera.close()
        s.close()






