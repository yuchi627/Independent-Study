import cv2
import numpy as np
import sys
from matplotlib import pyplot as plt

file1 = sys.argv[1]
#file2 = sys.argv[2]

img1 = cv2.imread(file1)
#img2 = cv2.imread(file2)

gray1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
#gray2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

colors = ("b","g","r")
channels = cv2.split(img1)

"""
plt.figure()
plt.title("Color Histogram")
plt.xlabel("Bins")
plt.ylabel("Number of Pixels")

for (channels,color) in zip(channels,colors):
    # create a histogram for the current channel and plot it
    hist = cv2.calcHist([channels],[0],None,[256],[0,256])
    plt.plot(hist,color = color)
    plt.xlim([0,256])
"""
hist_B = cv2.calcHist(channels[0],[0],None,[256],[0,256])
hist_G = cv2.calcHist(channels[1],[0],None,[256],[0,256])
hist_R = cv2.calcHist(channels[2],[0],None,[256],[0,256])

hist_combine = hist_B + hist_G + hist_R
hist_combine.sort(axis=0)
hist_combine = hist_combine[::-1]   # in descending order




