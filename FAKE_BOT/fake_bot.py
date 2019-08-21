import struct
import socket
import time
import random
import cv2
import numpy as np
import select

#HOST = '172.20.10.2'
HOST = '192.168.43.149'
PORT = 8888
num = 1
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

def move1():
	print("enter function_1")
	count = 0
	s.send((("0.0").encode()).ljust(16))
	print("0.0")
	s.send((("Right").encode()).ljust(16))
	loop = 0
	time.sleep(0.5)
	while loop < 4:
		while count < 5:
			s.send((("1.2").encode()).ljust(16))
			count += 1
			time.sleep(0.5)

			#random help
			ran = random.randint(1,5)
			if ran == 5:
				help_me()
		count = 0
		s.send((("Left").encode()).ljust(16))
		loop += 1
		time.sleep(0.5)
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)

def move2():
	print("enter function_2")
	s.send((("0.0").encode()).ljust(16))
	loop = 0
	count = 0
	time.sleep(0.5)
	while loop < 4:
		while count < 5:
			s.send((("1.2").encode()).ljust(16))
			count += 1
			time.sleep(0.5)

			#random help
			ran = random.randint(1,5)
			if ran == 5:
				help_me()
		count = 0
		s.send((("Right").encode()).ljust(16))
		time.sleep(0.5)
		loop += 1
	time.sleep(0.5)

def move3():
	print("enter function_3")
	s.send((("0.0").encode()).ljust(16))
	count = 0
	time.sleep(0.5)
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
		
		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()
		
	count = 0
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	while count < 9:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 9:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
		
		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

def move4():
	print("enter function_4")
	s.send((("0.0").encode()).ljust(16))
	time.sleep(0.5)
	count = 0

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	count = 0
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	while count < 9:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
	
		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

	while count < 9:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()
	
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	
def move5():
	print("enter function_5")
	s.send((("0.0").encode()).ljust(16))
	time.sleep(0.5)
	count = 0

	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		time.sleep(0.5)
		count += 1

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		time.sleep(0.5)
		count += 1

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		time.sleep(0.5)
		count += 1

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		time.sleep(0.5)
		count += 1
		
		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	
	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		time.sleep(0.5)
		count += 1

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	count = 0
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		time.sleep(0.5)
		count += 1

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

def move6():
	print("enter function_6")
	s.send((("0.0").encode()).ljust(16))
	count = 0

	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)

	s.send((("1.5").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 5:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()
	
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 5:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,20)
		if ran == 10:
			help_me()
		elif ran == 20:
			not_help()

	count = 0

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("1.5").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

	count = 0
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
		
		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

def move7():
	print("enter function_7")
	s.send((("0.0").encode()).ljust(16))
	count = 0
	
	while count < 5:
		s.send((("DRAW1.4").encode()).ljust(16))
		print(1.4)
		send_image()
		count += 1
		time.sleep(0.2)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("DRAAWLeft").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	count = 0
	while count < 6:
		s.send((("DRAW1.5").encode()).ljust(16))
		print(1.5)
		send_image()
		time.sleep(0.2)
		count += 1

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()
	
	s.send((("DRAWLeft").encode()).ljust(16))
	time.sleep(0.2)
	send_image()
	count = 0
	loop = 0
	s.send((("DRAW1.5").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	s.send((("DRAW1.5").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	while loop < 4:
		while count < 4:
			s.send((("DRAW1.5").encode()).ljust(16))
			send_image()
			count += 1
			time.sleep(0.2)

			#random help
			ran = random.randint(1,20)
			if ran == 10:
				not_help()
			elif ran == 20:
				help_me()

		s.send((("DRAWRight").encode()).ljust(16))
		send_image()		
		time.sleep(0.2)
		count = 0
		loop += 1
	
	s.send((("DRAWLeft").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	s.send((("DRAWLeft").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	s.send((("DRAw1.5").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	s.send((("DRAW1.5").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	s.send((("DRAWRight").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	
	count = 0
	while count < 6:
		s.send((("DRAW1.5").encode()).ljust(16))
		send_image()
		count += 1
		time.sleep(0.2)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	count = 0
	s.send((("DRAWRight").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	while count < 5:
		s.send((("DRAW1.4").encode()).ljust(16))
		send_image()
		count += 1
		time.sleep(0.2)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("DRAWRight").encode()).ljust(16))
	send_image()
	time.sleep(0.2)
	s.send((("DRAWRight").encode()).ljust(16))
	send_image()
	time.sleep(0.2)

def help_me():
	count = 0
	print("enter help_condition")
	while count < 10:
		s.send((("HELP").encode()).ljust(16))
		#s.send('HOT'.ljust(16).encode())
		print('HELP')
		send_image()
		time.sleep(0.2)
		count += 1
	count = 0
	while count < 10:
		s.send((("HELP2").encode()).ljust(16))
		#s.send('HOT'.ljust(16).encode())
		print('HELP2')
		send_image()
		time.sleep(0.2)
		count += 1

def not_help():
	count = 0
	print("enter not_really_need_help")
	while count < 7:
		s.send((("HELP").encode()).ljust(16))
		#s.send('HOT'.ljust(16).encode())
		print('HELP')
		
		send_image()
		time.sleep(0.2)
		count += 1

def img_processing(ir_img,flir_val):
	tmp = ir_img.copy()
	flir_val = cv2.resize(flir_val,(ir_weight,ir_height),interpolation = cv2.INTER_CUBIC)
	flir_val = np.dstack([flir_val]*3)
	######### combine ir & flir image ################
	dst = cv2.warpPerspective(flir_val,matrix,(ir_weight,ir_height))
	np.place(tmp,(dst > th_100),(0,0,255))
	np.place(tmp,((dst > th_70)&(dst <= th_100)),(163,255,197))
	add = cv2.addWeighted(ir_img,0.5,tmp,0.5,0)
	######## rotate image 180 #################
	return cv2.warpAffine(add, M, (ir_weight,ir_height))
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
flir_height = 380   #flir_tmp.shape[0]
flir_weight = 520   #flir_tmp.shape[1]
refresh = False
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
ir_img = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
data = b''
matrix = np.loadtxt('matrix6.txt',delimiter = ',')
M = cv2.getRotationMatrix2D((ir_weight/2,ir_height/2), 180, 1)
th_70 = 7700
th_100 = 7800
count_img = 0

def send_image():
	global count_img
	count_img += 1
	if(count_img == 81):
		count_img = 1
	ir_img = cv2.imread("../ir/img"+str(count_img)+".jpg")
	flir_val = np.loadtxt("../flir/flir"+str(count_img)+".txt")
	flir_val = np.reshape(flir_val,(60,80,1))
	flir_val = flir_val.astype(np.uint16)
	try:
		######## encode message ############
		_, imgencode_ir = cv2.imencode('.jpg', ir_img, encode_param)
		data_ir = np.array(imgencode_ir)
		stringData_ir = data_ir.tostring()
		######### encode flir_val ###########
		flir_val_ravel = flir_val.ravel()
		flir_val_pack = struct.pack("I"*len(flir_val_ravel),*flir_val_ravel)
		'''
		s.send(("IR"+str(len(stringData_ir))).ljust(16).encode())
		s.send(stringData_ir)
		####### send flir image to server #########
		s.send(("FLIR"+str(len(flir_val_pack))).ljust(16).encode())
		s.send(flir_val_pack)
		t4 = time.time()
		try:
			####### recv the combine image from server #############
			ready = select.select([s],[],[],0.1)
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
		'''
		try:
			global s
			####### send ir image ###############
			s.send(("IR"+str(len(stringData_ir))).ljust(16).encode())
			s.send(stringData_ir)
			####### send flir image to server #########
			s.send(("FLIR"+str(len(flir_val_pack))).ljust(16).encode())
			s.send(flir_val_pack)
			t4 = time.time()
			try:
				####### recv the combine image from server #############
				ready = select.select([s],[],[],0.1)
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
				cv2.imshow('image',img_combine)
				cv2.waitKey(1)
			except Exception as e:
				img_combine = img_processing(ir_img,flir_val)
				data = b''
					
		except Exception as e:
			print(e)
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
	except Exception as e:
		print(e.args)	
def recv_msg():
	ready = select.select([s],[],[],0.05)
	if(ready[0]):
		recv_data = s.recv(20)
		if('I will save you' in recv_data.decode()):
			print('recv')
	
s.send((("Tony").encode()).ljust(16))
print("Tony")
s.send(("TH70"+str(th_70)).ljust(16).encode()) 
s.send(("TH100"+str(th_100)).ljust(16).encode())
time.sleep(1)
s.send((("0.0").encode()).ljust(16))
print("0.0")
time.sleep(1)
s.send((("0.0").encode()).ljust(16))
print("0.0")

print("click the map, hurry up!!")
time.sleep(10)

while True:
	move7()
	'''
	r = random.randint(1,7)
	if r == 1:
		move1()
	elif r == 2:
		move2()
	elif r == 3:
		move3()
	elif r == 4:
		move4()
	elif r == 5:
		move5()
	elif r == 6:
		move6()
	else:
		move7()
	'''
