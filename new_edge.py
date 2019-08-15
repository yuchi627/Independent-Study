import struct
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
import time
#import serial
HOST = '172.20.10.2'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
flir_height = 380   #flir_tmp.shape[0]
flir_weight = 520   #flir_tmp.shape[1]
refresh = False
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
img_combine2 = np.zeros((ir_height,ir_weight,3),np.uint8)
ir_img = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
matrix = np.loadtxt('./matrix4.txt',delimiter = ',')
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
try:
	count_img = 0
	cv2.namedWindow("combine",cv2.WND_PROP_FULLSCREEN)
	#cv2.setWindowProperty("combine",cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	camera = picamera.PiCamera()
	camera.resolution = (640,480)
	camera.framerate = 40
	s.send(("Nadine").ljust(16).encode())
	#s.send(("0.0").ljust(16).encode())
	#s.send(("0.0").ljust(16).encode())
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
		s.send(("TH70"+str(th_70)).ljust(16).encode())
		s.send(("TH100"+str(th_100)).ljust(16).encode())
		while (count_img<5):
			count_img += 1
		#while True:
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
			#img_processing()
			######## encode message ############
			_, imgencode_ir = cv2.imencode('.jpg', ir_img, encode_param)
			data_ir = np.array(imgencode_ir)
			stringData_ir = data_ir.tostring()
			flir_val = flir_val.ravel()
			flir_val = struct.pack("I"*len(flir_val),*flir_val)
			try:
				######## send ir image ###############
				s.send(("IR_S"+str(len(stringData_ir))).ljust(16).encode())
				s.send(stringData_ir)
				####### send flir image to server #########
				s.send(("flir"+str(len(flir_val))).ljust(16).encode())
				s.send(flir_val)
				ready = select.select([s],[],[],0.05)
				if(ready[0]):
					print("recv")
					data = s.recv(16).strip('\x00')
					size = int(data.decode().strip())
					data = s.recv(size)
					data = np.fromstring(data,dtype = 'uint8')
					data = cv2.imdecode(data,1)
					img_combine = np.reshape(data,(ir_height,ir_weight,3))

			except:
				print("reconnecting server")
				try:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect((HOST,PORT))
					#encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
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






