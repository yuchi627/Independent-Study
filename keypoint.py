import cv2
import numpy as np

original = cv2.imread("ir.jpg")
new = cv2.imread("ir2.jpg")

original = cv2.resize(original,(260,195))
new = cv2.resize(new,(260,195))

gray1 = cv2.cvtColor(original,cv2.COLOR_BGR2GRAY)
gray2 = cv2.cvtColor(new,cv2.COLOR_BGR2GRAY)

gray1 = cv2.GaussianBlur(gray1,(3,3),0)
gray2 = cv2.GaussianBlur(gray2,(3,3),0)

lowRate = 0.1
ret, _ = cv2.threshold(gray1,0,255,cv2.THRESH_OTSU)
print('ret = ',ret)
edge1 = cv2.Canny(gray1,ret*lowRate,ret)
ret, _ = cv2.threshold(gray2,0,255,cv2.THRESH_OTSU)
edge2 = cv2.Canny(gray2,ret*lowRate,ret)


#edge1 = cv2.resize(edge1,(260,195))
#edge2 = cv2.resize(edge2,(260,195))

cv2.imwrite("edge1.jpg",edge1)
cv2.imwrite("edge2.jpg",edge2)


sift = cv2.xfeatures2d.SIFT_create()
kp_1, desc_1 = sift.detectAndCompute(original,None)
kp_2, desc_2 = sift.detectAndCompute(new, None)

index_params = dict(algorithm=1, trees=5)
search_params = dict()
flann = cv2.FlannBasedMatcher(index_params, search_params)

matches = flann.knnMatch(desc_1,desc_2,k=2)

good_points = []
for m,n in matches:
    if m.distance < 0.7*n.distance:
        good_points.append(m)
number_keypoints = 0
if len(kp_1) <= len(kp_2):
    number_keypoints = len(kp_1)
else:
    number_keypoints = len(kp_2)

print("good match rate : ",len(good_points)/number_keypoints)
result = cv2.drawMatches(original,kp_1,new,kp_2,good_points,None)

cv2.imwrite("result.jpg",result)


