import cv2
import numpy as np

p9 = cv2.imread("otsu9.jpg",0)
p10 = cv2.imread("otsu10.jpg",0)
#p9 = cv2.cvtColor(p9,cv2.COLOR_BGR2GRAY)
#p10 = cv2.cvtColor(p10,cv2.COLOR_BGR2GRAY)
sub = abs(np.subtract(p9,p10))
#cv2.imshow("p9",p9)
#cv2.imshow("p10",p10)
cv2.imwrite("sub.jpg",sub)

np.savetxt("p9.txt",p9,fmt = "%d")
np.savetxt("p10.txt",p10,fmt = "%d")
np.savetxt("sub.txt",sub,fmt = "%d")
#cv2.waitKey(0)
