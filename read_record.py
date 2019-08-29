import sys
import time
import socket
import numpy as np
import struct
import cv2
import select

<<<<<<< HEAD
HOST = '192.168.68.100'
=======
HOST = '192.168.68.196'
>>>>>>> dac3983c340742e3b5e38e25465403d04d297b04
PORT = 8888
img_limit = 0
if sys.argv[1] == 1:
	img_limit = 1795
elif sys.argv[1] == 2:
	img_limit = 320
elif sys.argv[1] == 3:
	img_limit = 205

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



path = 'bot'+sys.argv[1]+'/'
fp = open(path+'record_dont_delete.txt')
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
ir_height = 480
ir_weight = 640
img_combine = np.zeros((ir_height, ir_weight, 3),np.uint8)
ir_img = np.empty((ir_height, ir_weight),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
data = b''
size = 0
recv_size_flag = True
matrix = np.loadtxt('matrix6.txt',delimiter=',')
M = cv2.getRotationMatrix2D((ir_weight/2,ir_height/2), 180,1)
read_count = 10
img_count = 1


time.sleep(float(fp.readline()))
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
for i in range(4):
	msg = fp.readline()
	#print(msg)
	s.send( (msg).strip().ljust(16).encode())
th_70 = float(fp.readline()[4:].strip())
th_100 = float(fp.readline()[5:].strip())
s.send(('TH70'+str(th_70)).ljust(16).encode())
s.send(('TH100'+str(th_100)).ljust(16).encode())
for i in range(2):
	msg = fp.readline()
	#print(msg)
	s.send( (msg).rstrip().ljust(16).encode())

line = fp.readline()
while line:
	#print(img_count)
	#print(line)
	if(read_count % 2 == 0):
		time.sleep(float(line))
	else:
		if 'image' in line:
			ir_img = cv2.imread(path+'ir_dont_delete/'+str(img_count)+'.jpg')
			_, imgencode_ir = cv2.imencode('.jpg', ir_img, encode_param)
			data_ir = np.array(imgencode_ir)
			stringData_ir = data_ir.tostring()
			
			flir_val = np.loadtxt(path+'flir_dont_delete/'+str(img_count)+'.txt')
			flir_val = flir_val.astype(np.uint16)
			flir_val_ravel = flir_val.ravel()
			flir_val_pack = struct.pack("I"*len(flir_val_ravel), *flir_val_ravel)
			s.send(("IR"+str(len(stringData_ir))).ljust(16).encode())
			s.send(stringData_ir)
			s.send(("FLIR"+str(len(flir_val_pack))).ljust(16).encode())
			s.send(flir_val_pack)
			try:
				####### recv the combine image from server #############
				ready = select.select([s],[],[],0.01)
				if(ready[0]):
					if(recv_size_flag):
						data += s.recv(16)
						if(len(data) >= 16):
							size_data = data[0:16]
							if(len(data) == len(size_data)):
								data = b''
							else:
								data = data[len(size_data):len(data)]
							size = int((size_data.decode()).strip())
							recv_size_flag = False
					while(size > len(data)):
						data += s.recv(size)
					if( (size != 0) & (size <= len(data))):
						data_img = data[0:size]
						if(len(data_img) == len(data)):
							data = b''
						else:
							data = data[len(data_img):len(data)]
						data_img = np.fromstring(data_img,dtype = 'uint8')
						data_img = cv2.imdecode(data_img,1)
						img_combine = np.reshape(data_img,(ir_height,ir_weight,3))
						recv_size_flag = True
			except Exception as e:
				print(e.args)
				img_combine = img_processing(ir_img,flir_val)
				data = b''	
			img_count += 1
		else:
			s.send(line.ljust(16).encode())
		cv2.imshow('combine',img_combine)
		cv2.waitKey(1)
		
	read_count += 1
	line = fp.readline()
	
	if line == '':
		print('end')
		fp.seek(0)
		for i in range(7):
			fp.readline()
		for i in range(2):
			s.send( (fp.readline()).strip().ljust(16).encode())

		line = fp.readline()
		img_count = 1
		read_count = 10

'''
for line in fp:
	print(read_count)
	if(read_count % 2 == 0):
		time.sleep(float(line))
	else:
		if 'image' in line:
			ir_img = cv2.imread(path+'ir_dont_delete/'+str(img_count)+'.jpg')
			_, imgencode_ir = cv2.imencode('.jpg', ir_img, encode_param)
			data_ir = np.array(imgencode_ir)
			stringData_ir = data_ir.tostring()
			
			flir_val = np.loadtxt(path+'flir_dont_delete/'+str(img_count)+'.txt')
			flir_val = flir_val.astype(np.uint16)
			flir_val_ravel = flir_val.ravel()
			flir_val_pack = struct.pack("I"*len(flir_val_ravel), *flir_val_ravel)
			s.send(("IR"+str(len(stringData_ir))).ljust(16).encode())
			s.send(stringData_ir)
			s.send(("FLIR"+str(len(flir_val_pack))).ljust(16).encode())
			s.send(flir_val_pack)
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
			img_count += 1
		else:
			s.send(line.ljust(16).encode())
		cv2.imshow('combine',img_combine)
		cv2.waitKey(1)
		
	read_count += 1
	print(line.strip())
'''
