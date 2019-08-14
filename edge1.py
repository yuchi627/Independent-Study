import time 
import picamera
import cv2
import numpy as np
import socket
import math
import subprocess
from pylepton import Lepton
import select
import picamera.array
import os
import smbus
import multiprocessing as mp
#import serial
HOST = '172.20.10.2'
PORT = 8888

'''
# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

# Variable
start = 0  #for time interval
start_warning_time = 0
help_flag = False
real_bes = 0
real_gyro = 0
stop_key = False
turning_flag = False

def read_byte(reg):
    return bus.read_byte_data(address, reg)

def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg+1)
    value = (h << 8) + l
    return value

def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def read_gyro():
    xout = read_word_2c(0x43)
    yout = read_word_2c(0x45)
    zout = read_word_2c(0x47)
    return xout

def read_bes_x():
    bes_x = read_word_2c(0x3b)
    bes_y = read_word_2c(0x3d)
    bes_z = read_word_2c(0x3f)

    bes_x_ska = bes_x / 16384.0 * 9.8
    return bes_x_ska

def read_bes_z():
    bes_x = read_word_2c(0x3b)
    bes_y = read_word_2c(0x3d)
    bes_z = read_word_2c(0x3f)

    bes_z_ska = bes_z / 16384.0 * 9.8
    return bes_z_ska

def get_bes(mutex, distance, dis_flag):
    global real_bes
    global stop_key
    global help_flag
    bes_arr = []

    while True:
        temp_data = read_bes_z()
        bes_arr.append(temp_data)
        if len(bes_arr) >= 500:
            real_bes = np.std(bes_arr)
            #print('real_bes: ', real_bes)
            mutex.acquire()
            if (real_bes <= 0.3 and real_bes > 0):
                distance.value += 0.0
            else:
                distance.value = distance.value + 1.3
            mutex.release()
            bes_arr = []
            #print(distance.value)
        if stop_key == True:
            break

def check_turning(mutex, turn, turn_flag):
    global real_gyro
    global stop_key
    while True:
        turn.value = read_gyro()
        mutex.acquire()
        if turn.value >= -12000 and turn.value <= 12000:
            turn_flag.value = 0 #no turn
        elif turn.value < 12000:
            turn_flag.value = 1 #left
        else:
            turn_flag.value = 2 #right
        mutex.release()
        
        if stop_key == True:
            break
       
'''
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
'''
bus = smbus.SMBus(1) 
address = 0x68       # via i2cdetect
bus.write_byte_data(address, power_mgmt_1, 0)

mutex = mp.Lock()

distance = mp.Value("d", 0)
turn = mp.Value("d", 0)

turn_flag = mp.Value("i", 0)
dis_flag = mp.Value("i", 0)

p = mp.Process(target=get_bes, args=(mutex, distance, dis_flag))
p1 = mp.Process(target=check_turning, args=(mutex, turn, turn_flag))
p.start()
p1.start()
'''
turn_wait_time = 0
help_wait_time = 0
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
if(os.path.isfile('./matrix4.txt')):
    print('exist')
else:
    print('not found')
matrix = np.loadtxt('./matrix4.txt',delimiter = ',')
request_flag = 0

try:
    delay_times = 0
    #cv2.namedWindow("combine2",cv2.WINDOW_NORMAL)
    cv2.namedWindow("combine",cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("combine",cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 40
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
    s.send(("Nadine").ljust(16).encode())
    s.send(("0.0").ljust(16).encode())
    s.send(("0.0").ljust(16).encode())
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
            '''
            ######## position ############
            #check if falling
            bes_xout = read_bes_x()
            #print("help: ", bes_xout)
            if bes_xout > -4.0:
                help_wait_time = time.time()
                if start_warning_time == 0:
                    start_warning_time = time.time()
                    print("START HELP")
                    time.sleep(1)
                else:
                    if time.time() - start_warning_time >= 5 and time.time() - start_warning_time < 10:
                        s.send((("HELP").encode()).ljust(16))
                        print("HELP")
                        help_flag = True
                    elif time.time() - start_warning_time >= 10:
                        s.send((("HELP2").encode()).ljust(16))
                        print("HELP2")
            else:
                start_warning_time = 0
                help_flag = False

            #send turning
            if help_flag == False:
                if turn_flag.value == 0:
                    #print("No Turn")
                    turning_flag = False
                
                elif turn_flag.value == 1 and time.time() - help_wait_time > 2:
                    turning_flag = True
                    s.send((("Left").encode()).ljust(16))
                    print("Left")
                    time.sleep(1)
                    turn_wait_time = time.time()
                    help_wait_time = 0
                elif time.time() - help_wait_time > 2:
                    turning_flag = True
                    s.send((("Right").encode()).ljust(16))
                    print("Right")
                    time.sleep(1)
                    turn_wait_time = time.time()
                    help_wait_time = 0
                else:
                    pass
                turning_flag = False
                turn.value = 0
                turn_flag.value = 0
            else:
                turn.value = 0
                turn_flag.value = 0

            if help_flag == False and time.time() - turn_wait_time > 2 and time.time() - help_wait_time > 2 and distance.value != 0:
                temp_dis = str(distance.value)
                s.send(((temp_dis).encode()).ljust(16))
                print(temp_dis)
                distance.value = 0
                time.sleep(0.15)
                turn_wait_time = 0
                help_wait_time = 0
            else:
                distance.value = 0
            '''
            ######## flir capture ########
            a,_ = l.capture()
            b = np.copy(a)
            cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
            np.right_shift(a, 8, a)
            flir_img = np.uint8(a)
            flir_val = np.uint16(b)
            ######## ir capture ############
            ir_img = np.empty((480,640,3),dtype = np.uint8)
            camera.capture(ir_img,'bgr',use_video_port = True)

            img_processing()
            '''
            ####### recv message from arduino ###########
            response = ser.read(16)
            decode_response = bytes.decode(response)
            if(decode_response.strip() == 'HELP'): ########5s
                print('HELP1')
                cv2.putText(img_combine, "Move", (20,250), cv2.FONT_HERSHEY_COMPLEX, 6, (255,255,255), 25)
            elif(decode_response.strip() == 'HELP2'):  #######10s
                print('HELP2')
                if(request_flag == -1):
                    cv2.putText(img_combine, "Got it", (20,250), cv2.FONT_HERSHEY_COMPLEX, 4, (255,255,255), 25)
                else:
                    request_flag = 1
            else:
                request_flag = 0
            '''
            ######## encode message ############
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
            result, imgencode = cv2.imencode('.jpg',ir_img,encode_param)
            data = np.array(imgencode)
            stringData = data.tostring()
            try:
                '''
                if(request_flag == 1):
                    ready = select.select([s], [], [], 0.05)
                    if(ready[0]):
                        recv_data = s.recv(20)
                        if("I will save you" in recv_data.decode()):
                            print("I will save you")
                            cv2.putText(img_combine, "Got it", (20,250), cv2.FONT_HERSHEY_COMPLEX, 4, (255,255,255), 25)
                            request_flag = -1
                if(len(response) == 16):
                    s.send(response)
                '''
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

            cv2.imshow("combine",img_combine)
            cv2.waitKey(1)
            t1 = time.time()
            #print(t1-t0)
                
finally:
        camera.close()
        s.close()






