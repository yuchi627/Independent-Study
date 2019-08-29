import smbus
import multiprocessing as mp
import struct
import cv2
import numpy as np
import socket
import math
from pylepton import Lepton
import select
import picamera.array
import time
import sys

HOST = '192.168.43.9'
PORT = 8888
# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

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
		try:
			temp_data = read_bes_z()
			bes_arr.append(temp_data)
			if len(bes_arr) >= 100:
				real_bes = np.std(bes_arr)
				#print('real_bes: ', real_bes)
				mutex.acquire()
				if (real_bes <= 0.3 and real_bes > 0):
					distance.value += 0.0
				elif (real_bes <= 2.0 and real_bes > 0.3):
					distance.value += 0.3
				else:
					distance.value += 0.8
				mutex.release()
				bes_arr = []
				#print(distance.value)
		except Exception as e:
			print(e.args)
		if stop_key == True:
			break

def check_turning(mutex, turn, turn_flag):
	global real_gyro
	global stop_key
	while True:
		try:
			turn.value = read_gyro()
			mutex.acquire()
			if turn.value >= -12000 and turn.value <= 12000:
				turn_flag.value = 0 #no turn
			elif turn.value < 12000:
				turn_flag.value = 1 #left
			if turn.value >= -12000 and turn.value <= 12000:
				turn_flag.value = 0 #no turn
			elif turn.value < 12000:
				turn_flag.value = 1 #left
			else:
				turn_flag.value = 2 #right
			mutex.release()
		except Exception as e:
			print(e.args)
		if stop_key == True:
			break
		    
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

t1 = time.time()
img_count = 1
size = 0# Variable
start = 0  #for time interval
start_warning_time = 0
help_flag = False
real_bes = 0
real_gyro = 0
stop_key = False
turning_flag = False
recv_size_flag = True
##############################
ir_height = 480 #tmp1.shape[0]
ir_weight = 640 #tmp1.shape[1]
img_combine = np.zeros((ir_height,ir_weight,3),np.uint8)
ir_img = np.empty((ir_height,ir_weight,3),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
data = b''
matrix = np.loadtxt('matrix6.txt',delimiter = ',')
M = cv2.getRotationMatrix2D((ir_weight/2,ir_height/2), 180, 1)
###############################################
t1 = time.time()

#main
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
turn_wait_time = 0
help_wait_time = 0
count = 0
last_flag = False
this_flag = False
try:	
	delay_times = 0
	cv2.namedWindow("combine",cv2.WND_PROP_FULLSCREEN)
	cv2.setWindowProperty("combine",cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
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
		th_70 = diff * 0.5 + val_min
		th_100 = diff * 0.6 + val_min
		
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((HOST,PORT))
		s.send(("Nadine").ljust(16).encode())
		s.send(("num"+str(sys.argv[1])).ljust(16).encode())
		s.send((("0.0").encode()).ljust(16))
		s.send((("0.0").encode()).ljust(16))
		s.send(("TH70"+str(th_70)).ljust(16).encode()) 
		s.send(("TH100"+str(th_100)).ljust(16).encode())
				
		t1 = time.time()
		time_sett = 0
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
			cv2.imwrite( (path+'ir/'+str(img_count)+'.jpg'), ir_img)
			np.savetxt(path+'flir/'+str(img_count)+'.txt',flir_val.reshape(flir_val.shape[0],flir_val.shape[1]))

			#print(time.time()-t1)
			######## encode message ############
			_, imgencode_ir = cv2.imencode('.jpg', ir_img, encode_param)
			data_ir = np.array(imgencode_ir)
			stringData_ir = data_ir.tostring()
			######### encode flir_val ###########
			flir_val_ravel = flir_val.ravel()
			flir_val_pack = struct.pack("I"*len(flir_val_ravel),*flir_val_ravel)
			img_count += 1

			######## encode message ############
			try:
				######## send ir image ###############
				count += 1
				if(count == 100):
					count = 0
				print("send",count)
				s.send(("IR"+str(len(stringData_ir))).ljust(16).encode())
				s.send(stringData_ir)
				####### send flir image to server #########
				s.send(("FLIR"+str(len(flir_val_pack))).ljust(16).encode())
				s.send(flir_val_pack)
				try:
					####### recv the combine image from server #############
					ready = select.select([s],[],[],0.1)
					if(ready[0]):
						#print("ready",recv_size_flag)
						if(recv_size_flag):
							data += s.recv(16)
							print("recv")
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
							print("recv")
						if((size !=0 ) & (size <= len(data))):
							#print(recv_size_flag)
							data_img = data[0:size]
							if(len(data_img) == len(data)):
								data = b''
							else:
								data = data[len(data_img):len(data)]
							data_img = np.fromstring(data_img,dtype = 'uint8')

							data_img = cv2.imdecode(data_img,1)
							img_combine = np.reshape(data_img,(ir_height,ir_weight,3))	
							cv2.imwrite("debug.jpg",img_combine)
							recv_size_flag = True
				except Exception as e:
					img_combine = img_processing(ir_img,flir_val)
					print(e.args)
					print("reshape = ",data_img)
					size =  0
					data = b''
					recv_size_flag = True
				t1 = time.time()

				try:
					#check if falling
					bes_xout = read_bes_x()
					#print("help: ", bes_xout)
					if bes_xout > -3.0:
						help_wait_time = time.time()
						if start_warning_time == 0:
							start_warning_time = time.time()
							print("START HELP")
							#time.sleep(1)
						else:
							if time.time() - start_warning_time >= 5 and time.time() - start_warning_time < 10:
								this_flag = True
								print(time.time()-t1)
								s.send((("HELP").encode()).ljust(16))
								t1 = time.time()
								print("HELP")
								help_flag = True
							elif time.time() - start_warning_time >= 10:
								this_flag = True
								s.send((("HELP2").encode()).ljust(16))
								t1 = time.time()
								print("HELP2")
					else:
						start_warning_time = 0
						help_flag = False
						this_flag = False

					if(this_flag == False and last_flag == True):
						turn.value = 0
						distance.value = 0
						turn_flag.value = 0
						time.sleep(1)
					#send turning
					last_flag = this_flag

					if help_flag == False:
						if turn_flag.value == 0:
							#print("No Turn")
							turning_flag = False
				
						elif turn_flag.value == 1 and time.time() - help_wait_time > 2.0 and time.time() - turn_wait_time > 2.0:
							turning_flag = True
							print(time.time()-t1)
							s.send((("DRAWLeft").encode()).ljust(16))
							t1 = time.time()
							print("Left")
							#time.sleep(1)
							turn_wait_time = time.time()
							help_wait_time = 0
						elif time.time() - help_wait_time > 2 and time.time() - turn_wait_time > 2.0:
							turning_flag = True
							print(time.time()-t1)
							s.send((("DRAWRight").encode()).ljust(16))
							t1 = time.time()
							print("Right")
							#time.sleep(1)
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
						print(time.time()-t1)
						s.send(('DRAW'+temp_dis).ljust(16).encode())
						t1 = time.time()
						print(temp_dis)
						distance.value = 0
						#time.sleep(0.15)
						turn_wait_time = 0
						help_wait_time = 0
					else:
						distance.value = 0
				except Exception as e:
					print(e.args)
							
			except:
				print("reconnecting server")
				img_combine = img_processing(ir_img,flir_val)
				'''
				try:
					####### reconnect server #########
					fp.write(str(time.time()-t1)+'\n')
					print(time.time()-t1)
					
					s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					s.connect((HOST,PORT))
					s.send(("Nadine").ljust(16).encode())
					s.send(("num"+str(sys.argv[1])).ljust(16).encode())
					s.send((("0.0").encode()).ljust(16))
					s.send((("0.0").encode()).ljust(16))
					s.send(("TH70"+str(th_70)).ljust(16).encode()) 
					s.send(("TH100"+str(th_100)).ljust(16).encode())
					
					t1 = time.time()
					fp.write("Nadine\n")
					fp.write("num"+str(sys.argv[1])+'\n')
					fp.write("0.0\n")
					fp.write("0.0\n")
					fp.write("TH70"+str(th_70)+"\n")
					fp.write("TH100"+str(th_100)+"\n")
				except:
					pass
				'''
			cv2.imshow("combine",img_combine)
			cv2.waitKey(1)
			
finally:
		camera.close()
		s.close()
		print('close')
		stop_key = True

