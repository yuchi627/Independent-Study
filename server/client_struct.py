import numpy as np
import cv2
class client:
    def __init__(self):
        self.total_package_size = -1
        self.img = b''
    def package_size(self):
        if(self.total_package_size >= 1024):
            return 1024
        else :
            return self.total_package_size
    def package_value(self):
        return self.total_package_size
    def package_set(self,package_num):
        self.total_package_size = package_num
    def package_decrease(self, decrease_num):
        self.total_package_size -= decrease_num
    def img_combine(self,recv_str):
        self.img += recv_str
    def img_read(self):
        data = np.fromstring(self.img, dtype = 'uint8')
        data = cv2.imdecode(data,1)
        self.img = b''
        return np.reshape(data,(480,640,3))
