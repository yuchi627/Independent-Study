import multiprocessing as mp
import time 
import picamera
import cv2
import numpy as np
import math
from pylepton import Lepton
import picamera.array
from multiprocessing import Manager
import socket
import serial

HOST = '192.168.208.126'
PORT = 8888
#ser = serial.Serial('/dev/ttyACM0',9600)

def capture(flip_v = False, device = "/dev/spidev0.0"):
    with Lepton(device) as l:
        a,_ = l.capture()
        b = np.copy(a)
    if flip_v:
        cv2.flip(a,0,a)
    cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
    np.right_shift(a, 8, a)
    return np.uint8(a), np.uint16(b)
    #return np.uint16(a)

def ir_capture(ir_img,l2):
    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
        s.send(("Client1").ljust(16).encode())
    except:
        pass
    try:
        camera = picamera.PiCamera()
        print('set camera')
        camera.resolution = (640,480)
        camera.framerate = 40
        while True:
            tmp1 = np.empty((480,640,3),dtype = np.uint8)
            camera.capture(tmp1,'bgr',use_video_port = True)

            #l2.acquire()
            #if not ir_img.empty():
            #    ir_img.get()
            ir_img.put(tmp1,False)
            #l2.release()
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
            result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
            data = np.array(imgencode)
            stringData = data.tostring()
            
            try:
                s.send(("SIZE"+str(len(stringData))).ljust(16).encode())
                s.send(stringData)
            except:
                try:
                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    s.connect((HOST,PORT))
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
                    s.send(("Client1").ljust(16).encode())
                except:
                    pass
            
    finally:
        #s.close()
        camera.close()

def flir_capture(q_val,q_img,flip_v = False, device = "/dev/spidev0.0"):
    with Lepton(device) as l:
        set_th =  True
        while(1):
            try:
                t= time.time()
                a,_ = l.capture()
                b = np.copy(a)
                if flip_v:
                    cv2.flip(a,0,a)
                cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
                np.right_shift(a, 8, a)
                flir_img = np.uint8(a)
                flir_val = np.uint16(b)
                if  q_img.full():
                    continue
                if not set_th:
                    val_min = np.min(flir_val)
                    diff = np.max(flir_val) - val_min
                    th_70.value = diff * 0.3 + val_min
                    th_100.value = diff * 0.5 + val_min
                    set_th = True
                q_val.put(flir_val,False)
                q_img.put(flir_img,False)
                t1 = time.time()
                #print(t1-t)
                #l.release()
            except Exception as e:
                print(e) 

def img_processing(flir_val,ir):
    tmp = ir.copy()
    flir_val = cv2.resize(flir_val,(ir_weight,ir_height),interpolation = cv2.INTER_CUBIC)
    flir_val = np.dstack([flir_val]*3)
    t3 = time.time()

    dst = cv2.warpPerspective(flir_val,matrix,(ir_weight,ir_height))
    #np.place(tmp,(dst > th_100.value),(0,0,255))
    #np.place(tmp,((dst > th_70.value) & (dst <= th_100.value)),(163,255,197))
    np.place(tmp,(dst > th_70),(0,0,255))
    np.place(tmp,((dst > th_70) & (dst <= th_100)),(163,255,197))
    #img_combine = cv2.addWeighted(ir,0.5,tmp,0.5,0)
    t4 = time.time()
    return cv2.addWeighted(ir,0.5,tmp,0.5,0)


if __name__=='__main__':
    cv2.namedWindow("Image",0)
    #cv2.resizeWindow("Image",1000,1000)
    #cv2.setWindowProperty("Image",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    ir_height = 480 #tmp1.shape[0]
    ir_weight = 640 #tmp1.shape[1]
    img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
    flir_val = np.zeros((ir_height,ir_weight),np.uint16)
    flir_img = np.zeros((ir_height,ir_weight),np.uint8)
    matrix = np.loadtxt('matrix3.txt',delimiter = ',')
    tmp1 = np.empty((480,640,3),dtype = np.uint8)
    request = False
    help1 = False
    help2 = False
    danger_count = 0
    th_danger = 25
    save_msg_count = 0
    th_70 = 7400
    th_100 = 7000
    #th_70 = mp.Value("d",0)#7070
    #th_100 = mp.Value("d",0)#7090
    try:
        #l = mp.Lock()
        l2 = mp.Lock()
        q_val = Manager().Queue()
        q_img = Manager().Queue()
        ir_img = Manager().Queue()
        ir_img.put(tmp1)
        q_img.put(flir_img)

        process_flir = mp.Process(target=flir_capture,args = (q_val,q_img,), daemon = True)
        process_flir.start()
        process_ir = mp.Process(target=ir_capture,args = (ir_img,l2), daemon = True)
        process_ir.start()

        #process_img = mp.Process(target=img_processing, args = (q_val,ir_img,l,th_100,th_70), daemon = True)
        #process_img.start()
        while True:
            t1 = time.time()
            while not (q_val.empty()): #or ir_img.empty()):
                if not q_val.empty():
                    flir_val = q_val.get()
                    flir_img = q_img.get()
                if not ir_img.empty():
                    tmp1 = ir_img.get()

            img_combine = img_processing(flir_val,tmp1)
            cv2.imshow("Image",img_combine)
            cv2.imshow("flir",flir_img)
            cv2.waitKey(1)
            t2 = time.time()
            print(t2-t1)
            
    finally:
        cv2.destroyAllWindows()

        #s.close()
        #camera.close()

