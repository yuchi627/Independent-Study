import time 
import picamera
import cv2
s = time.time()
count = 20
try:
    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 80
    cv2.namedWindow('picamera',cv2.WINDOW_NORMAL)
    #while(1):
    for num in range (0,40):
        start = time.time()
        count+=1
        pic = "img"+str(count)+".jpg"
        camera.capture(pic,use_video_port = True)
        end = time.time()
        tmp = cv2.imread(pic)
        cv2.imshow('picamera',tmp)
        cv2.waitKey(10)
        print (end-start)
finally:
    camera.close()




