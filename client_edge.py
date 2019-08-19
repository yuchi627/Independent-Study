import time 
import picamera
import cv2
import numpy as np
import socket
import math
from pylepton import Lepton
import select
#HOST = '172.20.10.3'
HOST = '192.168.43.118'
#HOST = '192.168.43.84'
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




s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send(("Firefighter1").ljust(16).encode())

count = 100
reconnect_count = 0
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
window_name = "IMAGE"
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
ir_img = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
matrix = np.loadtxt('matrix6.txt',delimiter = ',')
M = cv2.getRotationMatrix2D((ir_weight/2,ir_height/2), 180, 1)
save_flag = False
danger_flag = False
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]

try:
	cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
	#cv2.namedWindow("combine",cv2.WINDOW_NORMAL)
	th_70 = 7700
	th_100 = 7800
	count_img = 0
	while True:
		count_img += 1
		if(count_img == 81):
			count_img = 1
		ir_img = cv2.imread("ir/img"+str(count_img)+".jpg")
		flir_val = np.loadtxt("flir/flir"+str(count_img)+".txt")
		flir_val = np.reshape(flir_val,(60,80,1))
		flir_val = flir_val.astype(np.uint16)
		try:	
			red_flag, combine = img_processing(ir_img, flir_val)
			######## encode & send image #############
			_, encode_img = cv2.imencode('.jpg', combine, encode_param)
			data_img = np.array(encode_img)
			stringData_img = data_img.tostring()

			try:
				if(red_flag):
					s.send(("RIMG" + str(len(stringData_img))).ljust(16).encode())
				else:
					s.send(("IMG" + str(len(stringData_img))).ljust(16).encode())
				s.send(stringData_img)

				try: 
					ready = select.select([s], [], [],0.001)
					if(ready[0]):
						data = (s.recv(16)).decode()
						print("recv: ",data)
						if("save" in data):
							save_flag = True
						elif("close" in data):
							danger_flag = True
				except:
					print("recv msg error")
			except:
				if(reconnect_count == 0):
					try:
						print("trying to connect server")
						s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
						#print("1")
						s.connect((HOST, PORT))
						#print("2")
						s.send(("Firefighter1").ljust(16).encode())
						#print("3")
						#s.send(("TH70"+str(th_70)).ljust(16).encode())
						#s.send(("TH100"+str(th_100)).ljust(16).encode())
					except:
						print("re")
						reconnect_count = count
				else:
					print("-=1")
					reconnect_count -= 1
			if(save_flag):
				cv2.putText(combine, "You will be saved", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
				if(danger_flag):
					danger_flag = False
					cv2.putText(combine, "Close to danger area", (20,60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)    
			if(danger_flag):
				danger_flag = False
				cv2.putText(combine, "Close to danger area", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)

			cv2.imshow(window_name,combine)
			cv2.waitKey(1)
		except Exception as e:
			print(e.args)
finally:
        #camera.close()
        s.close()






