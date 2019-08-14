import socket
import time
import cv2
import numpy as np
HOST = '192.168.208.164'
PORT = 8888

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))
num = 1
total_area = 640*480

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
	count = 0
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	while count < 9:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 9:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		count += 1
		time.sleep(0.5)

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
	count = 0
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	while count < 9:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

	while count < 9:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
	
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
	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		time.sleep(0.5)
		count += 1
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		time.sleep(0.5)
		count += 1
	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		time.sleep(0.5)
		count += 1
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	
	while count < 4:
		s.send((("1.5").encode()).ljust(16))
		time.sleep(0.5)
		count += 1
	count = 0
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		time.sleep(0.5)
		count += 1
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
	
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 5:
		s.send((("1.5").encode()).ljust(16))
		count += 1
		time.sleep(0.5)
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

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

def move7():
	print("enter function_7")
	s.send((("0.0").encode()).ljust(16))
	count = 0
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		send_image()
		count += 1
		time.sleep(0.5)

	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 6:
		s.send((("1.5").encode()).ljust(16))
		send_image()
		time.sleep(0.5)
		count += 1
	
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	loop = 0
	s.send((("1.5").encode()).ljust(16))
	send_image()
	time.sleep(0.5)
	s.send((("1.5").encode()).ljust(16))
	send_image()
	time.sleep(0.5)
	while loop < 4:
		while count < 4:
			s.send((("1.5").encode()).ljust(16))
			send_image()
			count += 1
			time.sleep(0.5)
		s.send((("Right").encode()).ljust(16))
		time.sleep(0.5)
		count = 0
		loop += 1
	
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("1.5").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("1.5").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	
	count = 0
	while count < 6:
		s.send((("1.5").encode()).ljust(16))
		send_image()
		count += 1
		time.sleep(0.5)
	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		send_image()
		count += 1
		time.sleep(0.5)

	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)

def send_image():
	global num
	img = cv2.imread('test_image/'+str(num)+'.jpg')
	#cv2.imshow('img',img)
	#cv2.waitKey(8000)
	#img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
	#print(img)
	t0 = time.time()
	hot_area = len(np.where( (img>=(230,0,0)) & (img<=(255,110,110)) )[0])
	#cv2.imshow('hot_area', hot_area)
	#cv2.waitKey(1000)
	#print(hot_area)
	#hot_area = len(np.where( (img>=(156,43,46)) & (img<=(180,255,255)) )[0])
	t1 = time.time()
	#print(hot_area)
	#print(t1-t0)
	hot_percent = hot_area/total_area
	#print(hot_percent)
	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
	result, imgencode = cv2.imencode('.jpg',img,encode_param)
	data = np.array(imgencode)
	stringData = data.tostring()
	s.send(('SIZE'+str(len(stringData))).ljust(16).encode())
	s.send(stringData)
	num += 1
	if(num > 20):
		num = 1

s.send((("Tony").encode()).ljust(16))
print("Tony")
time.sleep(1)
s.send((("0.0").encode()).ljust(16))
print("0.0")
time.sleep(1)
s.send((("0.0").encode()).ljust(16))
print("0.0")
time.sleep(5)

while True:
	move7()
