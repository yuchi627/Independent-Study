import time 
import cv2
import numpy as np
import math
import sys
import picamera
from pylepton import Lepton
#from  matplotlib import pyplot as plt

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton(device) as l:
    a,_ = l.capture()
    b = np.copy(a)
  if flip_v:
    cv2.flip(a,0,a)
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  return np.uint8(a), np.uint16(b)

def get_position(event, x, y, flags, param):
    global src_points, dst_points, flir_img, ir_img, count
    if event == cv2.EVENT_LBUTTONDOWN:
        count += 1 
        if(param==1):
            src_points.append((x,y))
            np.savetxt('src6.txt',src_points,fmt = "%d,%d",delimiter = '\n')
            print('flir',len(src_points))
        elif(param==2):
            dst_points.append((x,y))
            obj_points.append([x,y,0])
            np.savetxt('dst6.txt',dst_points,fmt = "%d,%d",delimiter = '\n')
            np.savetxt('obj6.txt',obj_points,fmt = "%d,%d,%d",delimiter = '\n')
            print('ir',len(dst_points))
        if(len(src_points)>=4 and len(dst_points)>=4 and len(src_points)==len(dst_points)):
            get_matrix()
            calibrate()

def get_matrix():
    global src_points, dst_points, M_flag, Ma, Mp, Mh
    Ma = cv2.getAffineTransform(np.float32(src_points[0:3]), np.float32(dst_points[0:3]))
    Mp = cv2.getPerspectiveTransform(np.float32(src_points[0:4]), np.float32(dst_points[0:4]))
    Mh, mask = cv2.findHomography(np.float32(src_points), np.float32(dst_points))
    np.savetxt('matrix6.txt',Mh,fmt = "%f,%f,%f",delimiter = '\n')
    print("Ma = ",Ma)
    print("Mp = ",Mp)
    print("Mh = ",Mh)
    M_flag = True

def chess_board():
    for i in range(10,12):
        img = cv2.imread("flir"+str(i)+".jpg")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray,(4,6),None)
        if ret == True:
            print("Find")



def calibrate():
    global obj_points, src_points, Mc, newMc, dist, roi, rvec, tvec, R
    ret, Mc, dist, rvec, tvec = cv2.calibrateCamera([np.float32(obj_points)], [np.float32(src_points)], (640,480), None, None)
    newMc, roi = cv2.getOptimalNewCameraMatrix(Mc, dist, (640,480),1,(640,480)) 
    print('Mc = ',Mc)
    print('dist = ',dist)
    
    rvec = cv2.Rodrigues(np.float32(rvec))
    R[:3,:3] = rvec[0]
    print(R)
    print(tvec)
    R[0,3] = tvec[0][0]
    R[1,3] = tvec[0][1]
    R[2,3] = tvec[0][2]
    print(R)


def transform(flir_img, ir_img):
    global count, Ma, Mp, Mh, affine, perspect, homo, cali, Mc, newMc, dist, roi, R
    affine = cv2.warpAffine(flir_img, Ma, (640,480))
    perspect = cv2.warpPerspective(flir_img, Mp, (640,480), cv2.INTER_LINEAR)
    homo = cv2.warpPerspective(flir_img, Mh, (640,480), cv2.INTER_LINEAR)
    affine = cv2.addWeighted(ir_img, 0.8,affine, 0.2, 0)
    perspect = cv2.addWeighted(ir_img, 0.8,perspect, 0.2, 0)
    homo = cv2.addWeighted(ir_img, 0.8,homo, 0.2, 0)

    mapx, mapy = cv2.initUndistortRectifyMap(Mc, dist, None, newMc, (640,480),5)
    dst = cv2.remap(flir_img, mapx, mapy, cv2.INTER_LINEAR)
    '''
    dst = cv2.undistort(flir_img, Mc, dist, None, newMc)
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]
    '''
    cali = cv2.addWeighted(ir_img, 0.8,dst, 0.2, 0)

    #cali = cv2.warpPerspective(flir_img, R, (640,480), cv2.INTER_LINEAR)
    #cali = cv2.addWeighted(ir_img, 0.8,cali, 0.2, 0)
    
    #cv2.imwrite("transform_result/affine"+str(count)+".jpg", affine)
    #cv2.imwrite("transform_result/perspect"+str(count)+".jpg", perspect)
    #cv2.imwrite("transform_result/homo"+str(count)+".jpg", homo)
    #count += 1


#count = 1
ir_img = []
flir_img = []
M_flag = False
src_points = []
dst_points = []
obj_points = []
Ma = []
Mp = []
Mh = []
Mc = []
newMc = []
dist = []
roi = []
rvec = []
tvec = []
R = np.zeros((3,4), np.float32)
affine = []
perspect = []
homo = []
cali = []
count = 0

try:
    src_points = np.loadtxt('src5.txt',delimiter = ',').tolist()
    dst_points = np.loadtxt('dst5.txt',delimiter = ',').tolist()
    obj_points = np.loadtxt('obj5.txt',delimiter = ',').tolist()

    camera = picamera.PiCamera()
    camera.resolution = (640,480)
    camera.framerate = 40
    '''
    for i in range(16,17):
        print(i)
        ir = cv2.imread("ir"+str(i)+".jpg")
        flir = cv2.imread("flir"+str(i)+".jpg")
        flir = cv2.resize(flir,(640,480))
        ir = cv2.cvtColor(ir,cv2.COLOR_BGR2GRAY)
        while( count <16 ):
            cv2.imshow("__ir", ir)
            cv2.imshow("__flir", flir)
            cv2.setMouseCallback('__ir',get_position,2)
            cv2.setMouseCallback('__flir',get_position,1)
            cv2.waitKey(1)
        count = 0
    '''
    while True:
        flir_img, flir_val = capture()
        camera.capture("ir"+sys.argv[1]+".jpg",use_video_port = True)
        ir_img = cv2.imread("ir"+sys.argv[1]+".jpg")
        flir_img = cv2.applyColorMap(flir_img, cv2.COLORMAP_JET)
        #cv2.imwrite("flir"+sys.argv[1]+".jpg",flir_img)
        flir_img = cv2.resize(flir_img,(640,480))
        ir_img = cv2.cvtColor(ir_img,cv2.COLOR_BGR2GRAY)
        ir_img = np.dstack([ir_img]*3)
        if(M_flag == True):
            transform(flir_img, ir_img)
            #cv2.imshow("affine", affine)
            #cv2.imshow("perspect", perspect)
            cv2.imshow("homo", homo)
            #cv2.imshow("cali", cali)

        #plt.imshow(tmp1)
        #plt.imshow(flir_img)
        cv2.imshow("ir", ir_img)
        cv2.imshow("flir", flir_img)
        cv2.setMouseCallback('ir',get_position,2)
        cv2.setMouseCallback('flir',get_position,1)
        cv2.waitKey(1)

finally:
        camera.close()
'''
ir_height = tmp1.shape[0]
ir_weight = tmp1.shape[1]
white = tmp1.copy()
cut_rate = 0.2
cut_weight = int(ir_weight*cut_rate)
cut_height = int(ir_height*cut_rate)
flir_tmp = cv2.resize(flir_img,(ir_weight-cut_weight,ir_height-cut_weight),interpolation = cv2.INTER_CUBIC)
flir_height = flir_tmp.shape[0]
flir_weight = flir_tmp.shape[1]
move_y = 70  #90
move_x = 60
white[move_y:move_y+flir_height,move_x:move_x+flir_weight] = flir_tmp
'''
'''
img_combine = cv2.addWeighted(tmp1,0.8,white,0.2,0)
cv2.imshow("combine",img_combine)
cv2.waitKey()
'''
