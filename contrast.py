import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt

file1 = sys.argv[1]
file2 = sys.argv[2]

img1 = cv2.imread(file1)
img2 = cv2.imread(file2)

gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

colors = ("b","g","r")
channels = cv2.split(img1)



