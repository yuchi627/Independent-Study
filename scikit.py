import time
t0 = time.time()
from skimage.measure import compare_ssim
t1 = time.time()
import cv2
import sys

file1 = sys.argv[1]
file2 = sys.argv[2]
original = cv2.imread(file1)
new = cv2.imread(file2)

original = cv2.resize(original,(260,195))
new = cv2.resize(new,(260,195))
original = cv2.cvtColor(original,cv2.COLOR_BGR2GRAY)
new = cv2.cvtColor(new,cv2.COLOR_BGR2GRAY)
t2 = time.time()
s = compare_ssim(original,new)
t3 = time.time()
print(t1-t0)
print(t3-t2)
print(s)
