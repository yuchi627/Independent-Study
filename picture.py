import time
import sys
import subprocess
import cv2
import numpy as np
import os

start = time.time()
ir_file_name = sys.argv[1]
flir_file_name = sys.argv[2]

move = os.chdir("pylepton")

if len(sys.argv) == 4:
    int_argv = int(sys.argv[3])
    int_delay_time = (int_argv)
    delay_time = str(int_delay_time)
else:
    delay_time = "1"
    
command = "raspistill -o  " + ir_file_name + " -n -t " + delay_time
camera = time.time()
take_flir_photo = subprocess.call("./pylepton_capture " + flir_file_name, shell = True)
end = time.time()
print(end-camera)
take_ir_photo = subprocess.call(command,shell = True)
mid = time.time()
print(mid-end)
                       #OpenCV
image_ir = cv2.imread(ir_file_name, -1)
image_flir = cv2.imread(flir_file_name, 0)

image_flir = cv2.applyColorMap(image_flir, cv2.COLORMAP_JET)

cv2.imwrite("image_flir_big3.jpg",image_flir)

# cut
x = 300
y = 400
w = 2600
h = 1950
crop_img = image_ir[y:y+h, x:x+w]
cv2.imwrite("image_cut.jpg",crop_img)

# Find edge

lowThreshold = 35
highThreshold = 95
ratio=3
image_ir = cv2.resize(image_ir,(260,195))
gray_img = cv2.cvtColor(image_ir,cv2.COLOR_BGR2GRAY)
cv2.imwrite("gray.jpg",gray_img)
blur_img = cv2.GaussianBlur(gray_img,(3,3),0)
#blur_img = cv2.adaptiveThreshold(blur_img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,151,6)
canny = cv2.Canny(blur_img,lowThreshold,highThreshold,3)
#cv2.imshow('canny',canny)
#cv2.waitKey(0)
ret, canny2 = cv2.threshold(canny,128,255,cv2.THRESH_BINARY_INV)
ret, canny = cv2.threshold(canny,128,1,cv2.THRESH_BINARY_INV)

'''
c=0
block = 101
canny2 = cv2.adaptiveThreshold(canny,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,block,c)
canny = cv2.adaptiveThreshold(canny,1,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY_INV,block,c)
'''
cv2.imwrite("canny3.jpg",canny)
cv2.imwrite("canny_ir3.jpg",canny2)
'''
image_ir = cv2.resize(image_ir,(260,195))
gray_img = cv2.cvtColor(image_ir,cv2.COLOR_BGR2GRAY)
ret, binary = cv2.threshold(gray_img,127,255,cv2.THRESH_BINARY)
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(mask,contours,-1,(255,255,255),1)
'''


'''
gray_flir = cv2.cvtColor(image_flir,cv2.COLOR_BGR2GRAY)
blur_flir = cv2.GaussianBlur(gray_flir,(3,3),0)
canny_flir = cv2.Canny(blur_flir,lowThreshold,highThreshold,3)
ret, canny_flir = cv2.threshold(canny_flir,128,255,cv2.THRESH_BINARY_INV)
cv2.imwrite("canny_flir.jpg",canny_flir)
'''

# Fill color
canny_color = cv2.cvtColor(canny,cv2.COLOR_GRAY2RGB)
image_flir_big = cv2.resize(image_flir,(260,195))

color0 = time.time()

image_flir_big[:,:,0] = np.multiply(image_flir_big[:,:,0],canny)
image_flir_big[:,:,1] = np.multiply(image_flir_big[:,:,1],canny)
image_flir_big[:,:,2] = np.multiply(image_flir_big[:,:,2],canny)
cv2.imwrite("test_combine6.jpg",image_flir_big)

color1 = time.time()
print("multi:")
print(color1-color0)
#canny_color = cv2.addWeighted(canny_color,0.5,image_flir_big,0.7,0)
#canny_color = cv2.add(canny_color,image_flir_big,canny_color,mask)

for i in range(1,canny_color.shape[0]-1):
    for j in range (1,canny_color.shape[1]-1):
        if (canny_color[i-1,j-1,0] == 255):
            canny_color[i-1,j-1,0] = image_flir_big[i-1,j-1,0]
            canny_color[i-1,j-1,1] = image_flir_big[i-1,j-1,1]
            canny_color[i-1,j-1,2] = image_flir_big[i-1,j-1,2]
