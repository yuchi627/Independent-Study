import cv2
import numpy as np
import picamera

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton(device) as l:
    a,_ = l.capture()
  if flip_v:
    cv2.flip(a,0,a)
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a)


flir_img2 = capture()
camera = picamera.PiCamera()
camera.resolution = (640,480)
camera.framerate = 80
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
camera.capture("ir.jpg",use_video_port = True)











"""
ir_img = cv2.imread("ir.jpg")
flir_img = cv2.imread("flir.jpg")
flir_img = cv2.resize(flir_img,(640,480))
flir_img = cv2.applyColorMap(flir_img,cv2.COLORMAP_JET)

ir_gray = cv2.cvtColor(ir_img,cv2.COLOR_BGR2GRAY)
ir_gray = cv2.GaussianBlur(ir_gray,(3,3),0)

lowRate = 0.1
ret,binary = cv2.threshold(ir_gray,0,255,cv2.THRESH_OTSU)
empty_img = np.zeros((480,640,3))
image, contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(empty_img, contours, -1, (1,1,1), 1)
ir_edge = cv2.Canny(ir_gray, ret*lowRate, ret)

cv2.imwrite("ir_edge.jpg",ir_edge)
cv2.imwrite("ir_contour.jpg", empty_img)
cv2.imwrite("binary.jpg",binary)

flir_img[:,:,0] = np.multiply(flir_img[:,:,0],binary)
flir_img[:,:,1] = np.multiply(flir_img[:,:,1],binary)
flir_img[:,:,2] = np.multiply(flir_img[:,:,2],binary)
cv2.imwrite("combine.jpg",flir_img)
"""
