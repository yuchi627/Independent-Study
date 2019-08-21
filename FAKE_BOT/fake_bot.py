import socket
import time
import random
import cv2
import numpy as np
import select

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
		s.send((("1.4").encode()).ljust(16))
		#send_image()
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			not_help()

	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	while count < 6:
		s.send((("1.5").encode()).ljust(16))
		#send_image()
		time.sleep(0.5)
		count += 1

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()
	
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	count = 0
	loop = 0
	s.send((("1.5").encode()).ljust(16))
	#send_image()
	time.sleep(0.5)
	s.send((("1.5").encode()).ljust(16))
	#send_image()
	time.sleep(0.5)
	while loop < 4:
		while count < 4:
			s.send((("1.5").encode()).ljust(16))
			#send_image()
			count += 1
			time.sleep(0.5)

			#random help
			ran = random.randint(1,20)
			if ran == 10:
				not_help()
			elif ran == 20:
				help_me()

		s.send((("Right").encode()).ljust(16))
		time.sleep(0.5)
		count = 0
		loop += 1
	
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("Left").encode()).ljust(16))
	time.sleep(0.5)
	s.send((("1.5").encode()).ljust(16))
	send_image()
	time.sleep(0.5)
	s.send((("1.5").encode()).ljust(16))
	send_image()
	time.sleep(0.5)
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	
	count = 0
	while count < 6:
		s.send((("1.5").encode()).ljust(16))
		#send_image()
		count += 1
		time.sleep(0.5)

		#random help
		ran = random.randint(1,10)
		if ran == 10:
			help_me()

	count = 0
	s.send((("Right").encode()).ljust(16))
	time.sleep(0.5)
	while count < 5:
		s.send((("1.4").encode()).ljust(16))
		#send_image()
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

def help_me():
	count = 0
	print("enter help_condition")
	while count < 10:
		s.send((("HELP").encode()).ljust(16))
		s.send('HOT'.ljust(16).encode())
		print('HELP')
		#send_image()
		time.sleep(0.5)
		count += 1
	count = 0
	while count < 10:
		s.send((("HELP2").encode()).ljust(16))
		s.send('HOT'.ljust(16).encode())
		print('HELP2')
		#send_image()
		time.sleep(0.5)
		count += 1

def not_help():
	count = 0
	print("enter not_really_need_help")
	while count < 7:
		s.send((("HELP").encode()).ljust(16))
		s.send('HOT'.ljust(16).encode())
		print('HELP')
		
		#send_image()
		time.sleep(0.5)
		count += 1

def send_image():
	global num
	img = cv2.imread('test_image/'+str(num)+'.jpg')
	#cv2.imshow('img',img)
	#cv2.waitKey(8000)
	#img = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
	#print(img)
	#t0 = time.time()
	#hot_area = len(np.where( (img>=(230,0,0)) & (img<=(255,110,110)) )[0])
	#cv2.imshow('hot_area', hot_area)
	#cv2.waitKey(1000)
	#print(hot_area)
	#hot_area = len(np.where( (img>=(156,43,46)) & (img<=(180,255,255)) )[0])
	#t1 = time.time()
	#print(hot_area)
	#print(t1-t0)
	#hot_percent = hot_area/total_area
	#print(hot_percent)
	encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
	result, imgencode = cv2.imencode('.jpg',img,encode_param)
	data = np.array(imgencode)
	stringData = data.tostring()
	s.send(('SIZE'+str(len(stringData))).ljust(16).encode())
	s.send(stringData)
	recv_msg()
	if(num%3==0):
		print('HOT')
		s.send('HOT'.ljust(16).encode())
	num += 1
	if(num > 20):
		num = 1
def recv_msg():
	ready = select.select([s],[],[],0.05)
	if(ready[0]):
		recv_data = s.recv(20)
		if('I will save you' in recv_data.decode()):
			print('recv')
	
s.send((("Tony").encode()).ljust(16))
print("Tony")
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
