import cv2
import numpy as np
import picamera
import threading
#import math
import time
def otsu_canny(i,lowrate=0.4):
    img = i.copy()
    global le,wi
    ret,_ = cv2.threshold(img,thresh=0,maxval=255,type=(cv2.THRESH_BINARY+cv2.THRESH_OTSU))
    print "threshold1= ",(ret*lowrate),"threshold2= ",ret
    edged = cv2.Canny(img,threshold1 = (ret*lowrate),threshold2 = ret)
    edged = cv2.resize(edged,(le,wi))
    return edged

def median_canny(i,sigma=0.33):
    global le,wi
    img = i.copy()
    v=np.median(img)
    lower = int(max(0,(1.0-sigma)*v))
    upper = int(min(255,(1.0+sigma)*v))
    edged = cv2.Canny(img,lower,upper)
    edged = cv2.resize(edged,(le,wi))
    return edged

def similarity(img1,img2):
    #size = 260*195
    global le,wi
    size = le*wi
    img1 = cv2.resize(img1,(le,wi))
    img2 = cv2.resize(img2,(le,wi))
    mu1 = float(np.sum(img1))/size
    mu2 = float(np.sum(img2))/size
    sub1 = np.subtract(img1,mu1)
    sub2 = np.subtract(img2,mu2)
    sd11 = np.sum(sub1*sub1)/size
    sd22 = np.sum(sub2*sub2)/size
    sd1 = np.sqrt(sd11) #standard deviation
    sd2 = np.sqrt(sd22)
    cov = (np.sum(sub1*sub2))/size #covariance
    k1=0.01
    k2=0.03
    L=255
    c1=(k1*L)
    c2=(k2*L)
    c1=c1*c1
    c2=c2*c2
    c3 = c2/2
    s = 1000
    l12 = float(int((2*mu1*mu2 + c1) / (mu1*mu1 + mu2*mu2 + c1)*s))/s
    c12 = float(int((2*sd1*sd2 + c2) / (sd11 + sd22 + c2)*s))/s
    s12 = float(int((cov + c3) / (sd1*sd2 + c3)*s))/s
    s12 = (cov+c3)/(sd1*sd2+c3)
    alpha = 1
    beta = 1
    gamma = 0.01
    #print "alpha= ",alpha,"beta= ",beta,"gamma= ",gamma
    #son = (2*mu1*mu2+c1)*(2*cov+c2)
    ##mo = (mu1*mu1+mu2*mu2+c1)*(sd1+sd2+c2)
    print "l= ",l12,"c= ",c12,"s= ",s12
    if(l12 < 0 or c12 < 0 or s12 < 0):
        print "negative "
    else:
        ssim = (l12**alpha) * (c12**beta) * (s12**gamma)
        ssim = s12
        print ssim

le = 640/1
wi = 480/1
rele = 260
rewi = 195
first = raw_input("pic1: ")
sec = raw_input("pic2: ")
tstart = time.time()
i9 = cv2.imread(first)
i10 = cv2.imread(sec)
#i10 = np.full((480,640,3),25)
#i10 = i10.astype(np.uint8)

#i9 = cv2.resize(i9,(le,wi))
#i10 = cv2.resize(i10,(le,wi))
gray9 = cv2.cvtColor(i9,cv2.COLOR_BGR2GRAY)
gray10 = cv2.cvtColor(i10,cv2.COLOR_BGR2GRAY)
count=19
#i9=edge(i9)
count=20
#i10=edge(i10)
print "original"
similarity(i9,i10)
blur9 = cv2.GaussianBlur(gray9,(3,3),0)
blur10 = cv2.GaussianBlur(gray10,(3,3),0)
print "blur"
similarity(blur9,blur10)

t9= otsu_canny(blur9)
t10 = otsu_canny(blur10)
cv2.imwrite("canny9.jpg",t9)
cv2.imwrite("canny10.jpg",t10)
print "blur otsu_canny"
similarity(t9,t10)

t9= median_canny(blur9)
t10 = median_canny(blur10)
cv2.imwrite("canny_m9.jpg",t9)
cv2.imwrite("canny_m10.jpg",t10)
print "blur median_canny"
similarity(t9,t10)

i9 = cv2.Canny(i9,46.5,155)
i10 = cv2.Canny(i10,46.5,155)
print "canny"
similarity(i9,i10)

i9 = cv2.Canny(blur9,46.5,155)
i10 = cv2.Canny(blur10,46.5,155)
print "blur canny"
similarity(i9,i10)

tend = time.time()
print "time= ",tend-tstart

#detect(i9,i10)

