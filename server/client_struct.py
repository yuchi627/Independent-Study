import numpy as np
import cv2
height = 480
weight = 640
name_space_height = 50

white_img = np.zeros((height+name_space_height,weight,3), np.uint8)
white_img[:,:] = (255,255,255)

namespace_whiteimg = np.zeros((name_space_height,weight,3), np.uint8)
namespace_whiteimg[:,:] = (255,255,255)

class client:
    remain_package_size = -1
    binary_img = b''
    subplot_number = 0
    img = white_img
    visible = False
    first = False

    def __init__(self):
        self.visible = True
        self.namespace_img = namespace_whiteimg
        self.first = True

    def namespace_imgset(self,my_namespace_img):
        self.namespace_img = my_namespace_img
        self.first = False

    def first_time_recv(self):
        return self.first

    def set_visible(self,tORf):
        self.visible = tORf

    def package_size(self):
        return self.remain_package_size

    def package_set(self,package_num):
        self.remain_package_size = package_num

    def package_decrease(self, decrease_num):
        self.remain_package_size -= decrease_num

    def img_combine(self,recv_str):
        self.binary_img += recv_str
    
    def img_read(self):
        if(self.visible):
            return_img = self.img
        else:
            return_img = white_img
        return return_img

    def img_decode(self):
        ##### decode the string and turn to 2 dimension array
        try:
            data = np.fromstring(self.binary_img, dtype = 'uint8')
            data = cv2.imdecode(data,1)
            self.binary_img = b''
            self.img = np.reshape(data,(height,weight,3))
            self.img = np.concatenate((self.namespace_img,self.img),axis=0)
        except:
            self.img = white_img

