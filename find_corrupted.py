import cv2
import sys
import numpy as np

path = 'bot'+sys.argv[1]+'/ir_dont_delete/'
limit = 0
if sys.argv[1] == '1':
	limit = 1795
elif sys.argv[1] == '2':
	limit = 320
elif sys.argv[1] == '3':
	limit = 205

for i in range(1,limit+1):
	#print(i)
	try:
		img = cv2.imread(path+str(i)+'.jpg')
		_,img_encode = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY),90])
		data_encode = np.array(img_encode)
		str_encode = data_encode.tostring()
		print(b'\xff\xd8' in str_encode[:2] ,b'\xff\xd9' in str_encode[len(str_encode)-3:])
		#print(type(data_encode))
		#with open('encoded/'+str(i)+'.txt', 'w') as f:
		#	f.write(str_encode)
		#	f.flush
		#with open('img_encode.txt','r') as f:
		#	str_encode = f.read()

		nparr = np.fromstring(str_encode, np.uint8)
		img_decode = cv2.imdecode(nparr, 1)
		cv2.imshow('img',img_decode)
		cv2.waitKey(1)
	except Exception as e:
		print(e.args)

