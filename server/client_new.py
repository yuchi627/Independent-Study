import numpy as np
import cv2
import struct

height = 480
weight = 640
name_space_height = 50

white_img = np.zeros((height+name_space_height,weight,3), np.uint8)
white_img[:,:] = (255,255,255)

namespace_whiteimg = np.zeros((name_space_height,weight,3), np.uint8)
namespace_whiteimg[:,:] = (255,255,255)

matrix = np.loadtxt("matrix6.txt", delimiter=',')
M = cv2.getRotationMatrix2D((weight/2,height/2), 180, 1)
class client:
    th_70 = 0   ###### threshold for 70 degree flir value
    th_100 = 0  ###### threshold for 100 degree flir value
    remain_package_size = 0
    binary_img = b''
    ir_img = white_img
    combine_img = white_img
    show_img = white_img    
    name = "name"
    recv_ir_flag = False
    recv_flir_flag = False
    visible_flag = False
    first_flag = False  ###### first time recv msg
    sos_flag = False
    twinkling_flag = False
    closing_danger_flag = False     ###### close to the danger area
    in_danger_flag = False      ###### the red area more one third of pic
# ---------------------------------------------#
    color_set = (0,0,0) # 紅綠燈的燈號
    fire_num = ""
    fire_name = ""
    time_pass = 0
    id_num = 0 # 顯示在Map的數字
    ip_addr = "" # 裝置ip
    position_x = 25 # 裝置在Map的位置(x)
    position_y = 25 # 裝置在Map的位置(y)
    direction = -1 # 裝置方向
    dist_save = 0 # 距離暫存
    bes_data_list = []
    gyro_list = []
#------------------------------------------------#
    def __init__(self):
        self.visible_flag = True
        self.first_flag = True
        self.namespace_img = namespace_whiteimg

    def set_info(self,num,ip_position):
        self.id_num = num
        self.ip_addr = ip_position
        self.color_set = (0,255,0)

    def set_th70(self,th70):
        ###### set the 70 degree threshold of flir value ######
        self.th_70 = th70

    def set_th100(self,th100):
        ###### set the 100 degree threshold of flir value ######
        self.th_100 = th100

    def set_close_danger(self,flag):
        self.closing_danger_flag = flag

    def set_namespace(self,my_namespace_img):
        ###### set the image with name ######
        self.first_flag = False
        self.namespace_img = my_namespace_img

    def set_sos_flag(self,flag):
        self.sos_flag = flag

    def brush_namespace_background(self):
        if(self.sos_flag):
            if(self.twinkling_flag):
                self.twinkling_flag = False
                return 1    ###### red background
            else:
                self.twinkling_flag = True
                return 2    ###### white background
        return 0    ###### do not need to brush background

    def first_time_recv(self):
        return self.first_flag

    def set_visible(self,flag):
        self.visible_flag = flag

    def set_name(self,myname):
        self.name = myname

    def get_name(self):
        return self.name
        
    def get_package_size(self):
        return self.remain_package_size

    def set_package(self,package_num,ir_or_flir):
        self.remain_package_size = package_num
        if(ir_or_flir == 1):
            self.recv_ir_flag = True
        elif(ir_or_flir == 2):
            self.recv_flir_flag = True
        else:
            self.recv_ir_flag = False
            self.recv_flir_flag = False

    def decrease_package_size(self, num):
        self.remain_package_size -= num

    def combine_img(self,recv_str):
        self.binary_img += recv_str
    
    def read_img(self):
        if(self.visible_flag):
            return_img = self.show_img
        else:
            return_img = white_img
        return return_img

    def read_combine_img(self):
        return self.combine_img

    def decode_img(self):
        try:
            if(self.recv_ir_flag):
                ###### decode ir image ######
                self.recv_ir_flag = False
                data = np.fromstring(self.binary_img, dtype = 'uint8')
                data = cv2.imdecode(data,1)
                self.binary_img = b''
                self.ir_img = np.reshape(data,(height,weight,3))
                return False
            elif(self.recv_flir_flag):
                ###### decode flir value ######
                self.recv_flir_flag = False
                data = struct.unpack("4800I",self.binary_img)
                self.binary_img = b''
                data = (np.asarray(data)).astype(np.float32)
                data = np.reshape(data,(60,80,1))
                ###### if over threshold, replace part of ir image with red or green color ######
                dst = cv2.resize(data,(weight,height),interpolation= cv2.INTER_CUBIC)
                dst = np.dstack([dst]*3)
                tmp = self.ir_img.copy()
                dst = cv2.warpPerspective(dst,matrix,(weight,height))
                np.place(tmp,(dst > self.th_100),(0,0,255))
                np.place(tmp,((dst > self.th_70)&(dst <= self.th_100)),(163,255,197))
                before_rotate_img = cv2.addWeighted(self.ir_img,0.5,tmp,0.5,0)
                ###### rotate image ######
                rotate_img = cv2.warpAffine(before_rotate_img, M, (weight,height))
                self.combine_img = rotate_img
                ###### put the warning message on pic ######
                if(np.sum(data) >= (data.size / 3)):
                    ###### if the red area more one third of pic, rise the in_danger_flag ######
                    self.in_danger_flag = True
                    cv2.putText(self.combine,"In danger area !",(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),3)
                elif(self.closing_danger_flag):
                    cv2.putText(self.combine,"Close to danger area",(20,40),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,255),3)
                    self.closing_danger_flag = False
                ###### concatenate the combine_img and namespace ######
                self.show_img = np.concatenate((self.namespace_img,self.combine_img),axis=0)
                return True
            return False

        except Exception as e:
            print(e.args)
            ###### if decode image fail, show the white image ######
            self.show_img = white_img
            return False
        return False

    def addNewPosition(self,direct,dist): # 我們的function
        if self.direction != -1:
# change direction        
            if direct == "Right":
                self.dist_save = 0
                self.direction += 90
                if self.direction >= 360:
                    self.direction -= 360
            elif direct == "Left":
                self.dist_save = 0
                self.direction -= 90
                if self.direction < 0:
                    self.direction += 360
            elif direct == "No Turn" or direct == "":
                pass #no direction changes
            else:
                pass
                #print(direct)
#change distance
            #print(self.direction)
            dist = dist + self.dist_save # avoid error
            dist_cm = dist*100 # change meter to centimeter
            if dist_cm < 70:
                self.dist_save = self.dist_save + dist
            else:
                self.dist_save = 0
                map_cm = dist_cm/228.69 # change the billy ruler
                pixel_num = int(map_cm*100/1.5) # change to pixel
                #print("pixel_num: "+str(pixel_num))
                if self.direction == 0:
                    self.position_y -= pixel_num
                elif self.direction == 90:
                    self.position_x += pixel_num
                elif self.direction == 180:
                    self.position_y += pixel_num
                elif self.direction == 270:
                    self.position_x -= pixel_num
                else:
                    pass

