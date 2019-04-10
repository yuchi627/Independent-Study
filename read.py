import cv2
k=cv2.imread("img21.jpg")
cv2.namedWindow("s")
k=cv2.cvtColor(k,cv2.COLOR_BGR2RGB)
cv2.imshow("s",k)
cv2.waitKey(0)
