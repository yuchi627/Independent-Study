import sys
import time
import socket
import numpy as np
import struct
import cv2
import select
<<<<<<< HEAD

<<<<<<< HEAD
HOST = '192.168.209.70'
=======
HOST = '192.168.209.29'
>>>>>>> e5a6bb36bdbda56bc524ba41c5deeeadf86962d8
=======
HOST = '192.168.68.196'
>>>>>>> 2902b58489479b637a2c95d44b559aa132c33f99
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



path = 'bot'+sys.argv[1]+'/'
fp = open(path+'record_dont_delete.txt')
#debug = open("debug"+str(sys.argv[1])+".txt","a")
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
ir_height = 480
ir_weight = 640
first = 10
img_combine = np.zeros((ir_height, ir_weight, 3),np.uint8)
ir_img = np.empty((ir_height, ir_weight),np.uint8)
flir_val = np.zeros((ir_height,ir_weight),np.uint16)
data = b''
recv_size_flag = True
matrix = np.loadtxt('matrix6.txt',delimiter=',')
M = cv2.getRotationMatrix2D((ir_weight/2,ir_height/2), 180,1)
read_count = 10
img_count = 1
remain_size = 16
package_size = 16
count_send = 0
flag_of_debug = False
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
	s.send( fp.readline().rstrip().ljust(16).encode())

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
				ready = select.select([s],[],[],0.1)
				if(ready[0]):
					if(recv_size_flag):
							data += s.recv(16)
							find_size = data.find(b'SIZE')
							'''
							if(flag_of_debug & (first > 0)):
								debug.write("size:"+str(data))
								debug.write("\n")
							'''
							while(find_size == -1):
								data = data[len(data)-16:]
								data += s.recv(8000)
								find_size = data.find(b'SIZE')
								'''
								if(flag_of_debug & (first>0)):
									debug.write("size:"+str(data))
									debug.write("\n")
								'''

								#remain_size = package_size - len(data)
								print("recv remain size")
							if(find_size != -1):
								size_data = data[find_size:find_size+16]
								
								while(len(size_data) < 16):
									print("recv 16 size","find_size = ",find_size,",data len=",len(data))
									data += s.recv(16)
										
									find_size = data.find(b'SIZE')
									size_data = data[find_size:find_size+16]
									print(data[find_size:find_size+16])
								try:
										package_size = int((size_data[4:].decode()).strip())
										if(len(data) == len(size_data)):
											data = b''
										else:
											data = data[find_size+16:]
										remain_size = package_size - len(data)
										recv_size_flag = False

										find_size = -1
								except Exception as e:
									find_size = -1
									data = data[find_size:]
									data = b''
									package_size = 0
									remain_size = 0
									recv_size_flag = True
					if not (recv_size_flag):
						if(package_size == 0):
							data = b''
							package_size = 0
							remain_size = 0
							recv_size_flag = True
						else:
							while(remain_size > 0):
								data += s.recv(remain_size)
								remain_size = package_size - len(data)
							if(package_size <= len(data)) :
								
								data_img = data[0:package_size]
								img_array = np.fromstring(data_img,dtype = 'uint8')
								try:
									img_decode = cv2.imdecode(img_array,1)

								except Exception as e:
									print("error in img decode=",e.args)
								try:
									img_combine = np.reshape(img_decode,(ir_height,ir_weight,3))
									count_send += 1
									if(count_send == 1000):
										count_send = 0
								except Exception as e:
									'''
									if(first > 0):
										flag_of_debug = True
										debug.write("img"+str(count_send)+":"+str(package_size)+"lenOFdata"+len(data_img))
										print("img"+str(count_send)+":"+str(package_size))
										debug.write(str(data_img))
										print(str(data_img))
										debug.write("\n")
										first -= 1
									if(first == 0):
										debug.close()
									count_send += 1
									if(count_send == 1000):
										count_send = 0
									'''
									print("img_array=",img_array,"len=",len(img_array))
									print("error in img reshape=",e.args)
									print("img_decode=",img_decode)
								if(len(data_img) == len(data)):
									data = b''
								else:
									data = data[len(data_img):]
								recv_size_flag = True
								package_size = 16
								remain_size = package_size - len(data)
			except Exception as e:
				print("error:",e.args)
				print("len of data_img=",len(data_img),"data=",len(data))
				print("img_array= ",img_array,"len=",len(img_array))
				print("img_decode = ",img_decode)
				img_combine = img_processing(ir_img,flir_val)
				data = b''	
				recv_size_flag = True
				remain_size = 0
				package_size = 0
			img_count += 1
		else:
			s.send(line.ljust(16).encode())
		try:
			cv2.imshow('combine',img_combine)
		except Exception as e:
			print("error in imshow= ",e.args)
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
