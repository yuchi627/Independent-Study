import cv2
import numpy as np
import picamera

camera = picamera.PiCamera()
camera.resolution = (640,480)
camera.framerate = 40

while True:        
    camera.capture("ir1.jpg",use_video_port = True)
    img = cv2.imread('ir1.jpg',0)
    la_edge = cv2.Laplacian(img, cv2.CV_32F, ksize=3)
    la_edge = cv2.convertScaleAbs(edge)
    cv2.imshow("Laplacian", edge)
    cv2.waitKey(1)


