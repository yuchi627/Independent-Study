import socket
import select
import cv2
import numpy as np
import struct

HOST = '192.168.68.57'
PORT = 8888

def decode_img():
	global img_combine, img_binary, img_ir, ir_flag, flir_flag
	print('flir_flag',flir_flag)
	if ir_flag:
		ir_flag = False
		data = np.fromstring(img_binary, dtype = 'uint8')
		data = cv2.imdecode(data, 1)
		img_binary = b''
		img_ir = np.reshape(data, (height, width, 3))
		return False
	elif flir_flag:
		flir_flag = False
		data = struct.unpack('4800I', img_binary)
		self.img_binary = b''
		data = (np.asarray(data)).astype(np.float32)
		data = np.reshape(data, (60,80,1))
		dst = cv2.resize(data, (width, height), interpolation = cv2.INTER_CUBIC)
		dst = np.dstack([dst]*3)
		tmp = img_ir.copy()
		dst = cv2.warpPerspective(dst, matrix, (width,height))

		np.place(tmp, (dst > th_100), (0,0,255))
		np.place(tmp, ((dst > th_70) & (dst <= th_100)), (163,255,197))
		before_rotate = cv2.addWeighted(img_ir, 0.5, tmp, 0.5, 0)
		
		img_combine = cv2.warpAffine(before_rotate, M, (width, height))
		
		return True
	
	return False	


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)
s.setblocking(0)
print('Waiting for connections')
epoll = select.epoll()
epoll.register(s.fileno(), select.EPOLLIN)
response = b'Hello'
package_size = 0
th_70 = 0
th_100 = 0
ir_flag = False
flir_flag = False
height = 480
width = 640
img_combine = np.zeros((height,width,3), np.uint8)
img_ir = img_combine.copy()
img_binary = b''
matrix = np.loadtxt('matrix6.txt', delimiter=',')
M = cv2.getRotationMatrix2D((width/2,height/2), 180, 1)
send_flag = False
refresh_img = False
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
try:
	connections = {}
	recv_data = {}
	send_data = {}
	while True:
		events = epoll.poll()
		for fileno, event in events:
			if fileno == s.fileno():
				conn, address = s.accept()
				print('accept connection')
				conn.setblocking(0)
				epoll.register(conn.fileno(), select.EPOLLIN)
				#print(conn.fileno())
				connections[conn.fileno()] = conn
				recv_data[conn.fileno()] = b''
				#print(type(recv_data[conn.fileno()]))
				send_data[conn.fileno()] = response
			elif event & select.EPOLLIN:
				print('in')
				recv_data[fileno] = None
				if package_size <= 0:
					#print(fileno)
					recv_data[fileno] = connections[fileno].recv(16)
					recv_data_msg = recv_data[fileno].decode().strip()
					print(recv_data_msg)
					if 'FLIR' in recv_data_msg:
						package_size = int(recv_data_msg[4:])
						flir_flag = True
					elif 'IR' in recv_data_msg:
						package_size = int(recv_data_msg[2:])
						ir_flag = True
					elif 'TH70' in recv_data_msg:
						th_70 = recv_data_msg[4:]
					elif 'TH100' in recv_data_msg:
						th_100 = recv_data_msg[5:]
				else:
					#recv_temp = connections[fileno].recv(package_size)
					#print(recv_temp)
					#print(type(recv_data[fileno]))
					#print(type(recv_temp))
					#index = len(recv_data[fileno])
					#recv_data[fileno][index:] = connections[fileno].recv(package_size)
					recv_data[fileno] = connections[fileno].recv(package_size)
					img_binary = recv_data[fileno]
					#package_size -= (len(recv_data[fileno]) - index)
					if True:
					#if package_size <= 0:
						send_flag = decode_img()
						print('send_flag',send_flag)
						if(send_flag):
							refresh_img = True
							send_flag = False
							ir_flag = False
							flir_flag = False
							_, encode = cv2.imencode('.jpg', img_combine, encode_param)
							data_combine = np.array(encode)
							stringData = data_combine.tostring()
							send_data[fileno] = stringData
							epoll.modify(fileno, select.EPOLLOUT)		
							#s.send(str(len(stringData)).ljust(16).encode())
							#s.send(stringData)
			elif event & select.EPOLLOUT:
				print('out')
				bytesWritten = connections[fileno].send(send_data[fileno])
				send_data = send_data[fileno][bytesWritten:]
				if(len(send_data[fileno])==0):
					epoll.modify(fileno, 0)
				connections[fileno].shutdown(s.SHUT_RDWR)
			elif event & select.EPOLLHUP:
				epoll.unregister(fileno)
				connections[fileno].close()
				del connections[fileno]
	
		cv2.imshow('server', img_combine)
		cv2.waitKey(1)


finally:
	epoll.unregister(s.fileno())
	epoll.close()
	s.close()
				
