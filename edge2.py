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
HOST = '172.20.10.6'
PORT = 8888

def img_processing(ir_img, flir_val):
	red_flag = False
	if(np.sum(flir_val) >= (flir_val.size / 3)):
		red_flag = True
	tmp = ir_img.copy()
	flir_val = cv2.resize(flir_val,(ir_weight,ir_height), interpolation = cv2.INTER_CUBIC)
	flir_val = np.dstack([flir_val]*3)
	dst = cv2.warpPerspective(flir_val,matrix,(ir_weight,ir_height)) 
	np.place(tmp, (dst > th_100), (0,0,255))
	np.place(tmp, ((dst > th_70) & (dst <= th_100)),(163,255,197))
	add = cv2.addWeighted(ir_img,0.5,tmp,0.5,0)
	return red_flag, cv2.warpAffine(add, M, (ir_weight,ir_height))

count = 100
reconnect_count = 0
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s.connect((HOST,PORT))
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
window_name = "IMAGE"
#flir_height = 380   #flir_tmp.shape[0]
#flir_weight = 520   #flir_tmp.shape[1]
#th_70 = 7800        #8900
#th_100 = 7860       #9650
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
ir_img = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
matrix = np.loadtxt('matrix6.txt',delimiter = ',')
M = cv2.getRotationMatrix2D((ir_weight/2,ir_height/2), 180, 1)
try:
	cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
	#cv2.namedWindow("combine",cv2.WINDOW_NORMAL)
	camera = picamera.PiCamera()
	camera.resolution = (640,480)
	camera.framerate = 40
	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),20]
	#s.send(("Nadine").ljust(16).encode())
	device = "/dev/spidev0.0"
	with Lepton(device) as l:
		a,_ = l.capture()
		flir_val = np.uint16(a)
		val_min = np.min(flir_val)
		diff = np.max(flir_val) - val_min
		th_70 = diff * 0.6 + val_min
		th_100 = diff * 0.8 + val_min
		while True:
			a,_ = l.capture()
			flir_val = np.uint16(a)
			camera.capture(ir_img, 'bgr', use_video_port = True)
			red_flag, combine = img_processing(ir_img, flir_val)
			######## encode & send image #############
			_, encode_img = cv2.imencode('.jpg', combine, encode_param)
			data_img = np.array(encode_img)
			stringData_img = data_img.tostring()
			try:
				if(red_flag):
					s.send(("RIMG"+ str(len(stringData_img))).ljust(16),encode())
				else:
					s.send(("IMG"+ str(len(stringData_img))).ljust(16),encode())
				s.send(stringData_img)
				try: 
					ready = select.select([s], [], [],0.05)
					if(ready[0]):
						data = (s.recv(16)).decode()
						if("save" in data):
							save_flag = True
						elif("close" in data):
							danger_flag = True
				except:
					print("recv msg error")
				if(save_flag):
					cv2.putText(combine, "You will be saved", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
					if(danger_flag):
						danger_flag = False
						cv2.putText(combine, "Close to danger area", (20,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)	
				if(danger_flag):
					danger_flag = False
					cv2.putText(combine, "Close to danger area", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
			except:
				if(reconnect_count == 0):
					try:
						print("trying to connect server")
						#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						s.connect((HOST, PORT))
						s.send(("Firefighter1").ljust(16).encode())
						#s.send(("TH70"+str(th_70)).ljust(16).encode())
						#s.send(("TH100"+str(th_100)).ljust(16).encode())
					except:
						reconnect_count = count
				else:
					reconnect_count -= 1
			cv2.imshow(window_name,combine)
			cv2.waitKey(1)
		
finally:
        camera.close()
        s.close()






