import cv2
import numpy as np
from pylepton import Lepton

def capture(flip_v = False, device = "/dev/spidev0.0"):
  with Lepton(device) as l:
    a,_ = l.capture()
  if flip_v:
    cv2.flip(a,0,a)
  #cv2.normalize(a, a, 0, 65535, cv2.NORM_MINMAX)
  #np.right_shift(a, 8, a)
  #return np.uint8(a)
  return np.uint16(a)

def fill_color(img, color)
th_70 = 8900
th_100 = 9650
flir_val = capture()
print(np.max(flir_val))
first = np.where(flir_val >= th_70, 0, 1)
second = (flir_val < th_70) * flir_val
secone = np.where(second > 100, 0, 1)
third = np.where(flir_val >= th_100, 1, 0)

first = first.astype(np.float32)
first = cv2.cvtColor(first, cv2.COLOR_GRAY2BGR)
first = first * (255,0,0)
first = cv2.resize(first,(640,480))
cv2.imshow("first", first)
cv2.waitKey()
#ret, first = cv2.threshold(flir_val, th_70, 1, cv2.THRESH_BINARY_INV)
#ret, second = cv2.threshold(
