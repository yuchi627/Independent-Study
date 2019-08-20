import struct
import cv2
import numpy as np
import socket
import math
from pylepton import Lepton
import select
import picamera.array
import time
#HOST = '172.20.10.3'
#HOST = '192.168.43.118'
#HOST = '192.168.43.84'
HOST = '192.168.43.149'
#HOST= "127.0.0.1"
PORT = 8888

def img_processing(ir_img,flir_val):
	flag = False
	tmp = ir_img.copy()
	if(np.sum((flir_val > th_100)) >= (flir_val.size / 3)):
		flag = True
	flir_val = cv2.resize(flir_val,(ir_weight,ir_height),interpolation = cv2.INTER_CUBIC)
	flir_val = np.dstack([flir_val]*3)
	######### combine ir & flir image ################
	dst = cv2.warpPerspective(flir_val,matrix,(ir_weight,ir_height))
	np.place(tmp,(dst > th_100),(0,0,255))
	np.place(tmp,((dst > th_70)&(dst <= th_100)),(163,255,197))
	add = cv2.addWeighted(ir_img,0.5,tmp,0.5,0)
	######## rotate image 180 #################
	rotate = cv2.warpAffine(add, M, (ir_weight,ir_height))
	if(flag):
		flag = False
		cv2.putText(rotate,"In danger area", (20,40), cv2.FONT_HERSHEY_SIMPLEX,1, (255,255,255), 3)
	return rotate


ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
ir_img = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
data = b''
matrix = np.loadtxt('matrix6.txt',delimiter = ',')
M = cv2.getRotationMatrix2D((ir_weight/2,ir_height/2), 180, 1)
try:
	cv2.namedWindow("combine",cv2.WND_PROP_FULLSCREEN)
	####### set ir camera ##########
	camera = picamera.PiCamera()
	camera.resolution = (640,480)
	camera.framerate = 40
	####### set flir camera ###########
	device = "/dev/spidev0.0"
	with Lepton(device) as l:
		a,_ = l.capture()
		flir_val = np.uint16(a)
		val_min = np.min(flir_val)
		diff = np.max(flir_val)-val_min
		######## 70 & 10 degree threshold ########3
		th_70 = diff * 0.6 + val_min
		th_100 = diff * 0.8 + val_min
		#count_img = 0
		#while (count_img<80):
		#	count_img += 1
		while True:
			#count_img += 1
           	######## flir capture ########
			a,_ = l.capture()
			flir_val = np.uint16(a)
			######## ir capture ############
			camera.capture(ir_img,'bgr',use_video_port = True)
				
			######## encode message ############
			_, imgencode_ir = cv2.imencode('.jpg', ir_img, encode_param)
			data_ir = np.array(imgencode_ir)
			stringData_ir = data_ir.tostring()
			######### encode flir_val ###########
			flir_val_ravel = flir_val.ravel()
			flir_val_pack = struct.pack("I"*len(flir_val_ravel),*flir_val_ravel)
			try:
				######## send ir image ###############
				s.send(("IR"+str(len(stringData_ir))).ljust(16).encode())
				s.send(stringData_ir)
				####### send flir image to server #########
				s.send(("FLIR"+str(len(flir_val_pack))).ljust(16).encode())
				s.send(flir_val_pack)
				t4 = time.time()
				try:
					####### recv the combine image from server #############
					ready = select.select([s],[],[],0.01)
					if(ready[0]):
						data = s.recv(16)
						size_data = data[0:16]
						if(len(data) == len(size_data)):
							data = b''
						else:
							data = data[len(size_data):len(data)]
						size = int((size_data.decode()).strip())
						while(size > len(data)):
							data += s.recv(size)
						data_img = data[0:size]
						if(len(data_img) == len(data)):
							data = b''
						else:
							data = data[len(data_img):len(data)]
						data_img = np.fromstring(data_img,dtype = 'uint8')
						data_img = cv2.imdecode(data_img,1)
						img_combine = np.reshape(data_img,(ir_height,ir_weight,3))
				except Exception as e:
					img_combine = img_processing(ir_img,flir_val)
					data = b''
					
			except:
				print("reconnecting server")
				img_combine = img_processing(ir_img,flir_val)
				try:
					####### reconnect server #########
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect((HOST,PORT))
					s.send(("Nadine").ljust(16).encode())
					s.send(("TH70"+str(th_70)).ljust(16).encode()) 
					s.send(("TH100"+str(th_100)).ljust(16).encode())
				except:
					pass
			cv2.imshow("combine",img_combine)
			cv2.waitKey(1)
			
finally:
		camera.close()
		s.close()






