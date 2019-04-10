import sys
from PIL import Image
import imagehash
import time
import cv2
import numpy as np
import ssim.ssimlib as pyssim
'''
a1 = time.time()
ahash1 = imagehash.average_hash(Image.open(file1))
ahash2 = imagehash.average_hash(Image.open(file2))
a2 = time.time()
p1 = time.time()
phash1 = imagehash.phash(Image.open(file1))
phash2 = imagehash.phash(Image.open(file2))
p2 = time.time()
d1 = time.time()
dhash1 = imagehash.dhash(Image.open(file1))
dhash2 = imagehash.dhash(Image.open(file2))
d2 = time.time()
w1 = time.time()
whash1 = imagehash.whash(Image.open(file1))
whash2 = imagehash.whash(Image.open(file2))
w2 = time.time()
'''
file1 = sys.argv[1]
file2 = sys.argv[2]
# cutoff = sys.argv[3]

'''
if ahash1 - ahash2 < cutoff:
    print('images are similar')
else:
    print('images are different')

if phash1 - phash2 < cutoff:
    print('images are similar')
else:
    print('images are different')

if dhash1 - dhash2 < cutoff:
    print('images are similar')
else:
    print('images are different')

if whash1 - whash2 < cutoff:
    print('images are similar')
else:
    print('images are different')
'''

##### My aHash #####

t2 = time.time()

img1 = cv2.imread(file1)
img2 = cv2.imread(file2)

n = int(sys.argv[3])
cutoff = 0.078*n*n

img1 = cv2.resize(img1,(n,n))
img2 = cv2.resize(img2,(n,n))

img1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

avg1 = np.sum(img1) / (n*n)
avg2 = np.sum(img2) / (n*n)

for j in range(0,n,1):
    for k in range(0,n,1):
        if img1[j][k] >= avg1:
            img1[j][k] = 1
        else:
            img1[j][k] = 0

for j in range(0,n,1):
    for k in range(0,n,1):
        if img2[j][k] >= avg2:
            img2[j][k] = 1
        else:
            img2[j][k] = 0

myHash1 = img1.reshape(-1)
myHash2 = img2.reshape(-1)

print(myHash1)
print(myHash2)

HamDist = 0
for i in range(0,n*n,1):
    if myHash1[i] != myHash2[i]:
       HamDist += 1
if(HamDist < cutoff):
    print('images are similar')
else:
    print('images are different')
t3 = time.time()
print(HamDist)
print(cutoff)
print('t = ', t3-t2)


'''
print('ta = ', a2-a1)
print('tp = ', p2-p1)
print('td = ', d2-d1)
print('tw = ', w2-w1)
'''
'''
##### getMSSIM #####
C1 = 6.5025
C2 = 58.5225

img1 = cv2.imread(file1)
img2 = cv2.imread(file2)
img1 = cv2.resize(img1,(260,195))
img2 = cv2.resize(img2,(260,195))
img1 = cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)
diff = np.abs(img1-img2)
rmse = np.sqrt(diff).sum()
print(rmse)
psnr = 20*np.log10(255/rmse)
print(psnr)
'''
