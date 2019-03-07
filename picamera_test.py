import time 
import picamera
import cv2
s = time.time()
try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 80
    cv2.namedWindow('picamera',cv2.WINDOW_NORMAL)
    for num in range (0,30):
        start = time.time()
        camera.capture('image.jpg',use_video_port = True)
        end = time.time()
        tmp = cv2.imread('image.jpg')
        cv2.imshow('picamera',tmp)
        cv2.waitKey(10)
        print (end-start)
finally:
    camera.close()




