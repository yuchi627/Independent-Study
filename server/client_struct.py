import numpy as np
import cv2
class client:
    def __init__(self):
        self.package = -1
        self.img = b''
    def p(self):
        print("client!!!!!!")
    def package_value(self):
        return self.package
    def package_set(self,package_num):
        self.package = package_num
    def package_decrease(self):
        self.package -= 1
    def img_combine(self,recv_str):
        self.img += recv_str
    def img_read(self):
        data = np.fromstring(self.img, dtype = 'uint8')
        data = cv2.imdecode(data,1)
        return np.reshape(data,(480,640,3))
