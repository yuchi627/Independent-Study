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

HOST = '192.168.208.140'
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
            l2.acquire()
            if not ir_img.empty():
                ir_img.get()
            ir_img.put(tmp1,False)
            l2.release()
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
            result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
            data = np.array(imgencode)
            stringData = data.tostring()
            
            try:
                s.send(str(len(stringData)).ljust(16).encode())
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
                #l.acquire()
                
                #while not q_val.empty():
                #    q_val.get()
                #    q_img.get()
                
                q_val.put(flir_val,False)
                q_img.put(flir_img,False)
                t1 = time.time()
                print(t1-t)
                #l.release()
            except Exception as e:
                print(e) 
'''
def flir_capture(q_val,q_img):
    while(1):
        try:
            t = time.time()
            flir_img,flir_val = capture()
            if  q_img.full():
                continue
            #l.acquire()
            
            #while not q_val.empty():
            #    q_val.get()
            #    q_img.get()
            
            q_val.put(flir_val,False)
            q_img.put(flir_img,False)
            t1 = time.time()
            print("flir",t1-t)
            #l.release()
        except Exception as e:
            print(e)

'''
def img_processing(flir_val,ir):
    '''
    ir_height = 480
    ir_weight = 640
    ir = np.empty((480,640,3),dtype = np.uint8)
    flir_val = np.zeros((480,640),np.uint16)
    '''

    # while True:
    '''
        t1 = time.time()
        l.acquire()
        if(q_val.empty()):
            l.release()
            continue
        while not (q_val.empty()): #or ir_img.empty()):
            if not q_val.empty():
                t1 = time.time()
                flir_val = q_val.get()
                t2 = time.time()
            if not ir_img.empty():
                ir = ir_img.get()
        l.release()
        t2 = time.time()
    '''
    tmp = ir.copy()
    cv2.imshow("2",tmp)
    flir_val = cv2.resize(flir_val,(ir_weight,ir_height),interpolation = cv2.INTER_CUBIC)
    flir_val = np.dstack([flir_val]*3)
    t3 = time.time()

    dst = cv2.warpPerspective(flir_val,matrix,(ir_weight,ir_height))
    np.place(tmp,(dst > th_100),(0,0,255))
    np.place(tmp,((dst>th_70) & (dst <= th_100)),(163,255,197))
    #img_combine = cv2.addWeighted(ir,0.5,tmp,0.5,0)
    t4 = time.time()
    return cv2.addWeighted(ir,0.5,tmp,0.5,0)

if __name__=='__main__':
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

    try:
        '''
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((HOST,PORT))
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
        s.send(("Client1").ljust(16).encode())
        
        camera = picamera.PiCamera()
        camera.resolution = (640,480)
        camera.framerate = 20
        '''
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

        #_, flir_val = capture()
        val_min = np.min(flir_val)
        diff = np.max(flir_val)-val_min
        th_70 = 7070
        th_100 = 7090
        #th_70 = diff * 0.3 + val_min
        #th_100 = diff * 0.5 + val_min
        refresh = False
        #time.sleep(0.01) 

        #process_img = mp.Process(target=img_processing, args = (q_val,ir_img,l,th_100,th_70), daemon = True)
        #process_img.start()
        
        while True:
            '''
            response = ser.readline()
            response = bytes.decode(response)
            print(response)
            print("Signal: ",response)
            if(response == 'HELP\r\n'):
                print('HELP')
                help1 = True
            elif(response == 'HELP2\r\n'):
                print('HELP2')
                help2 = True
            '''
            t1 = time.time()
            #l.acquire()
            l2.acquire()
            '''
            while not (q_val.empty()): #or ir_img.empty()):
                if not q_val.empty():
                    flir_val = q_val.get()
                    flir_img = q_img.get()
                if not ir_img.empty():
                    tmp1 = ir_img.get()
            '''
            if not q_val.empty():
                flir_val = q_val.get()
                flir_img = q_img.get()
                refresh = True
                cv2.imshow("flir",flir_img)

            else:
                print('empty')
            if not ir_img.empty():
                refresh = True
                tmp1 = ir_img.get()
            l2.release()
                        #l.release()
            #t3 = time.time()
            '''
            camera.capture(tmp1,'bgr',use_video_port = True)
            ir_img.put(tmp1,False)
            '''
            img_combine = img_processing(flir_val,tmp1)
            '''
            if(help1):
                cv2.putText(img_combine, "Move!", (20,250), cv2.FONT_HERSHEY_COMPLEX, 6, (255,255,255), 25)
                if(help2):
                    msg = 'SOS'
                    print('SOS')
                    s.sendto(msg.ljust(16).encode(),(HOST,PORT))
                    requset = True
                    #danger_count = 0
                if(request):
                    ready = select.select([s],[],[],0.05)
                    if(ready[0]):
                        recv_data = s.recv(20)
                        if("I will save you" in recv_data.decode()):
                            save_msg_count = 10
                            requset = False
                    if(save_msg_count):
                        save_msg_count -= 1
                        cv2.putText(img_combine,"Got it",(20,250),cv2.FONT_HERSHEY_COMPLEX,4,(255,255,255),25)
            else:
                danger_count = 0
            '''
            cv2.imshow("combine",img_combine)
            if(refresh):
                refresh = False
                cv2.waitKey(1)
            t2 = time.time()
            #print(t2-t1)

            '''
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
            result, imgencode = cv2.imencode('.jpg',tmp1,encode_param)
            data = np.array(imgencode)
            stringData = data.tostring()
            try:
                s.send(str(len(stringData)).ljust(16).encode())
                s.send(stringData)
            except:
                try:
                    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    s.connect((HOST,PORT))
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
                    s.send(("Client1").ljust(16).encode())
                except:
                    pass
            '''
            
    finally:
        cv2.destroyAllWindows()
        #s.close()
        #camera.close()

