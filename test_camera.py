import cv2
import numpy as np
from pylepton import Lepton
import picamera.array

def img_processing(ir_img, flir_val):
	flag  = False
	tmp = ir_img.copy()
	if(np.sum(flir_val > th_100) >= (flir_val.size / 3)):
		flag = True
	flir_val = cv2.resize(flir_val, (ir_w,ir_h),interpolation = cv2.INTER_CUBIC)
	flir_val = np.dstack([flir_val]*3)
	dst = cv2.warpPerspective(flir_val, matrix, (ir_w,ir_h))
	np.place(tmp, (dst > th_100), (0,0,255))
	np.place(tmp,((dst > th_70) & (dst <= th_100)),(163,255,197))
	add = cv2.addWeighted(ir_img, 0.5, tmp, 0.5, 0)
	rotate = cv2.warpAffine(add, M, (ir_w,ir_h))
	if(flag):
		flag = False
		cv2.putText(rotate, "In danger area", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
	return rotate


ir_h = 480
ir_w = 640
th_70 = 0
th_100 = 0
flir_val = np.zeros((ir_h,ir_w,3), np.uint8)
ir_img = np.empty((ir_h,ir_w,3), np.uint8)
matrix = np.loadtxt('matrix6.txt',delimiter = ',')
M = cv2.getRotationMatrix2D((ir_w/2,ir_h/2), 180, 1)
try:
	camera = picamera.PiCamera()
	camera.resolution = (ir_w, ir_h)
	camera.framerate = 40

	device = "/dev/spidev0.0"
	with Lepton(device) as l:
		a, _ = l.capture()
		flir_val = np.uint16(a)
		val_min = np.min(flir_val)
		diff = np.max(flir_val) - val_min
		th_70 = diff * 0.7 + val_min
		th_100 = diff * 0.8 + val_min
		while(True):
			a,_ = l.capture()
			flir_val = np.uint16(a)
			camera.capture(ir_img, 'bgr', use_video_port = True)
			img_combine = img_processing(ir_img,flir_val)
			cv2.imshow("combine",img_combine)
			cv2.waitKey(1)
finally:
	camera.close()
	print("close camera")

