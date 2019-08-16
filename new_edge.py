import struct
import cv2
import numpy as np
import socket
import math
#import subprocess
from pylepton import Lepton
import select
import picamera.array
#import os
#import smbus
import time
#import serial
HOST = '172.20.10.3'
#HOST= "127.0.0.1"
PORT = 8888

def img_processing(ir_img,flir_val):
	tmp = ir_img.copy()
	flir_val = cv2.resize(flir_val,(ir_weight,ir_height),interpolation = cv2.INTER_CUBIC)
	flir_val = np.dstack([flir_val]*3)
	dst = cv2.warpPerspective(flir_val,matrix,(ir_weight,ir_height))
	np.place(tmp,(dst > th_100),(0,0,255))
	np.place(tmp,((dst > th_70)&(dst <= th_100)),(163,255,197))
	return cv2.addWeighted(ir_img,0.5,tmp,0.5,0)




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
flir_height = 380   #flir_tmp.shape[0]
flir_weight = 520   #flir_tmp.shape[1]
refresh = False
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
#img_combine2 = np.zeros((ir_height,ir_weight,3),np.uint8)
ir_img = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
data = b''
matrix = np.loadtxt('matrix4.txt',delimiter = ',')
try:
	cv2.namedWindow("combine",cv2.WND_PROP_FULLSCREEN)
	#cv2.setWindowProperty("combine",cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
	camera = picamera.PiCamera()
	camera.resolution = (640,480)
	camera.framerate = 40
	s.send(("Nadine").ljust(16).encode())
	device = "/dev/spidev0.0"
	with Lepton(device) as l:
		a,_ = l.capture()
		flir_val = np.uint16(a)
		val_min = np.min(flir_val)
		diff = np.max(flir_val)-val_min
		th_70 = diff * 0.6 + val_min
		th_100 = diff * 0.8 + val_min
		s.send(("TH70"+str(th_70)).ljust(16).encode())
		s.send(("TH100"+str(th_100)).ljust(16).encode())
		count_img = 0
		#while (count_img<20):
		#	count_img += 1
		while True:
			#count_img += 1
			#if(count_img == 30):
				#s.send(("HELP2".ljust(16)).encode())
			#	print("HELP2")
           	######## flir capture ########
			t = time.time()
			a,_ = l.capture()
			flir_val = np.uint16(a)
			tn1 = time.time()
			######## ir capture ############
			#ir_img = np.empty((480,640,3),dtype = np.uint8)
			camera.capture(ir_img,'bgr',use_video_port = True)
			t2 = time.time()
			######## encode message ############
			_, imgencode_ir = cv2.imencode('.jpg', ir_img, encode_param)
			data_ir = np.array(imgencode_ir)
			stringData_ir = data_ir.tostring()
			######### encode flir_val ###########
			flir_val_ravel = flir_val.ravel()
			#print("Max = ",np.max(flir_val))
			flir_val_pack = struct.pack("I"*len(flir_val_ravel),*flir_val_ravel)
			t3 = time.time()
			#print("ir = ",t2-tn1,"flir=",tn1-t)
			try:
				######## send ir image ###############
				s.send(("IR_S"+str(len(stringData_ir))).ljust(16).encode())
				s.send(stringData_ir)
				####### send flir image to server #########
				s.send(("FLIR"+str(len(flir_val_pack))).ljust(16).encode())
				s.send(flir_val_pack)
				t4 = time.time()
				#print("t2-t1=",t2-t,"t3-t2",t3-t2,"t4-t3",t4-t3)
				try:
					####### recv the combine image from server #############
					ready = select.select([s],[],[],0.1)
					if(ready[0]):
						#print("recv")
						data = s.recv(16)
						#print(data)
						size_data = data[0:16]
						#size_data = data
						#print("SIZEDATA= ",size_data)
						#print("len of data=" , len(data))
						if(len(data) == len(size_data)):
							data = b''
						else:
							data = data[len(size_data):len(data)]
						size = int((size_data.decode()).strip())
						#print("package size = ",size)
						while(size > len(data)):
							data += s.recv(size)
						data_img = data[0:size]
						if(len(data_img) == len(data)):
							data = b''
						else:
							data = data[len(data_img):len(data)]
						#print("real recv size = ",len(data_img))
						data_img = np.fromstring(data_img,dtype = 'uint8')
						data_img = cv2.imdecode(data_img,1)
						img_combine = np.reshape(data_img,(ir_height,ir_weight,3))
				except Exception as e:
					img_combine = img_processing(ir_img,flir_val)
					data = b''
					print(e.args)
					
			except:
				print("reconnecting server")
				img_combine = img_processing(ir_img,flir_val)
				try:
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect((HOST,PORT))
					s.send(("Nadine").ljust(16).encode())
					s.send(("TH70"+str(th_70)).ljust(16).encode()) 
					s.send(("TH100"+str(th_100)).ljust(16).encode())
				except:
					pass
			cv2.imshow("combine",img_combine)
			cv2.waitKey(1)
			t1 = time.time()
			#print("time=",t1-t)
			#print("t2-t1=",t2-t1,"t3-t2",t3-t2,"t4-t3",t4-t3,"t5-t4",t5-t4)    
finally:
		camera.close()
		s.close()






