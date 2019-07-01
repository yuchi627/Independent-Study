import cv2
import numpy as np
from pylepton import Lepton

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton(device) as l:
    a,_ = l.capture()
    b = np.copy(a)
  if flip_v:
    cv2.flip(a,0,a)
  cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  np.right_shift(a, 8, a)
  #return np.uint8(a)
  return np.uint8(a), np.uint16(b)

def fill_color(img, color):
    img = img.astype(np.float32)
    img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    img = img * color
    return img

th_70 = 7680        #8900
th_100 = 7700       #9650
flir_img, flir_val = capture()
flir_val = cv2.resize(flir_val,(640,480))
flir_img = cv2.resize(flir_img,(640,480))
flir_img = cv2.applyColorMap(flir_img,cv2.COLORMAP_JET)
print(np.max(flir_val))
print(np.min(flir_val))
first = np.where(flir_val < th_70, 1, 0)
second_1 = np.where(flir_val >= th_70, 1, 0)
second_2 = np.where(flir_val >= th_100, 0, 1)
second = np.bitwise_and(second_1,second_2)
third = np.where(flir_val >= th_100, 1, 0)

first = fill_color(first,(255,0,0))
second = fill_color(second,(0,255,0))
third = fill_color(third,(0,0,255))
#cv2.imshow("first", first)
#cv2.imshow("second", second)
#cv2.imshow("third", third)
fusion = first + second + third
cv2.imshow("fusion",fusion)
cv2.imshow("flir",flir_img)
cv2.waitKey()
