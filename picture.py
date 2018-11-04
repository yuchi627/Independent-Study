import os
import sys
import subprocess
import cv2
import numpy as np

ir_file_name = sys.argv[1]
flir_file_name = sys.argv[2]

move = os.chdir("pylepton/")

if len(sys.argv) == 4:
    int_argv = int(sys.argv[3])
    int_delay_time = (int_argv)
    delay_time = str(int_delay_time)
else:
    delay_time = "1"
    
command = "raspistill -o  " + ir_file_name + " -n -t " + delay_time

take_flir_photo = subprocess.call("./pylepton_capture " + flir_file_name, shell = True)

take_ir_photo = subprocess.call(command,shell = True)
                        #OpenCV
image_ir = cv2.imread(ir_file_name, -1)
image_flir = cv2.imread(flir_file_name, 0)

image_flir = cv2.applyColorMap(image_flir, cv2.COLORMAP_JET)

cv2.imwrite("image_flir_big2.jpg",image_flir)

# cut
x = 300
y = 400
w = 2600
h = 1950
crop_img = image_ir[y:y+h, x:x+w]
cv2.imwrite("image_cut.jpg",crop_img)

# Find edge
lowThreshold = 20
highThreshold = 105
ratio=3
crop_img = cv2.resize(crop_img,(260,195))
gray_img = cv2.cvtColor(crop_img,cv2.COLOR_BGR2GRAY)
cv2.imwrite("gray.jpg",gray_img)
blur_img = cv2.GaussianBlur(gray_img,(3,3),0)
canny = cv2.Canny(blur_img,lowThreshold,highThreshold,3)
ret, canny = cv2.threshold(canny,128,255,cv2.THRESH_BINARY_INV)
cv2.imwrite("canny.jpg",canny)


gray_flir = cv2.cvtColor(image_flir,cv2.COLOR_BGR2GRAY)
blur_flir = cv2.GaussianBlur(gray_flir,(3,3),0)
canny_flir = cv2.Canny(blur_flir,lowThreshold,highThreshold,3)
ret, canny_flir = cv2.threshold(canny_flir,128,255,cv2.THRESH_BINARY_INV)
cv2.imwrite("canny_flir.jpg",canny_flir)
# Fill color
canny_color = cv2.cvtColor(canny,cv2.COLOR_GRAY2RGB)
image_flir_big = cv2.resize(image_flir,(260,195))

for i in range(1,canny_color.shape[0]-1):
    for j in range (1,canny_color.shape[1]-1):
        if (canny_color[i-1,j-1,0] == 255):
            canny_color[i-1,j-1,0] = image_flir_big[i-1,j-1,0]
            canny_color[i-1,j-1,1] = image_flir_big[i-1,j-1,1]
            canny_color[i-1,j-1,2] = image_flir_big[i-1,j-1,2]
cv2.imwrite("canny_change.jpg",canny_color)
