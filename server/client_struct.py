import numpy as np
import cv2
import struct
import time
from queue import Queue

class client:
    ###### image setting
    height = 480
    weight = 640
    name_space_height = 50
    bound_w = 1174 
    bound_h = 705 
    right_x = 25 + bound_w
    bottom_y = 25 + bound_h
    line_W = 10
    middle_x = 1170
    middle_y = 700
    matrix = np.loadtxt("matrix6.txt", delimiter=',')
    M = cv2.getRotationMatrix2D((weight/2,height/2), 180, 1)
    ###### for namespace
    name = "name"
    first_flag = False  ###### first time recv msg
    img_white = np.zeros((height+name_space_height,weight,3), np.uint8)
    img_white[:,:] = (255,255,255)
    img_white_namespace = np.zeros((name_space_height,weight,3), np.uint8)
    img_white_namespace[:,:] = (255,255,255)
    ###### for image recv
    remain_package_size = 0     
    img_package_size = 0
    img_binary = b''
    ###### for image send
    send_package_size = 0
    sended_size = 0
    send_img_flag = False
    ###### for message recv
    msg_binary = b''
    msg_size = 16
    remain_send_size = img_package_size
    remain_msg_size = msg_size
    ###### for show image 
    img_ir = img_white.copy()
    img_combine = img_white.copy()
    img_show = img_white.copy()
    recv_ir_flag = False
    recv_flir_flag = False
    visible_flag = False
    th_70 = 0   ###### threshold for 70 degree flir value
    th_100 = 0  ###### threshold for 100 degree flir value
    ###### for sos draw namespace background
    first_recv_sos = True
    sos_flag = False
    twinkling_flag = False
    ###### put text on image
    closing_danger_flag = False     ###### close to the danger area
    in_danger_flag = False      ###### the red area more than one third of pic
    in_explosion_flag = False   ###### in the area which commander select
    send_save_msg_flag = False  
    send_over_time_flag = False
    draw_count = 0      ###### count the emergency message number
    ###### for replay image 
    disconnect_flag = True  
    back_img_count = 0
    ###### bound of drawing fireman picture on map  
    fireman_bound_top = 0   
    fireman_bound_bottom = 0
    fireman_bound_left = 0
    fireman_bound_right = 0
    ###### bound of selecting explosion area on map
    explosion_bound_top = 0     
    explosion_bound_bottom = 0
    explosion_bound_left = 0
    explosion_bound_right = 0
# ---------------------------------------------#
    color_set = (0,0,0) # 紅綠燈的燈號
    fire_num = ""
    fire_name = ""          #########################################delete
    time_in = 0
    time_pass = 0
    id_num = 0 # 顯示在Map的數字
    ip_addr = "" # 裝置ip
    position_x = 25 # 裝置在Map的位置(x)
    position_y = 25 # 裝置在Map的位置(y)
    direction = -1 # 裝置方向
    dist_save = 0 # 距離暫存
    bes_data_list = []
    gyro_list = []
    left_spot_x = 0
    right_spot_x = 0
    up_spot_y = 0
    down_spot_y = 0
    line_left_spot_x = 0
    line_right_spot_x = 0
    line_up_spot_y = 0
    line_down_spot_y = 0
    line_offset = 6
    thick = 15
    thin = 10
    left_thickness = thick
    right_thickness = thick
    up_thickness = thick
    down_thickness = thick
    yellow_flag = False
    first_recv_help2 = True
    draw_line_blinking_flag = False
    blink_count = 0
    disconnect_time = 0
    disconnect_real_time = 0
    set_start = False   
    help2_flag = False
#------------------------------------------------#
    def __init__(self, num, queue_number):
        self.number = num
        self.first_flag = True
        #self.file = open(str(num)+".txt","w")
        self.namespace_img = self.img_white_namespace
        self.left_spot_x = 5 + (self.middle_x-5)*(num%2)
        self.right_spot_x = self.middle_x + self.middle_x*(num%2)
        self.up_spot_y = 5 + (self.middle_y-5)*(num >= 2)
        self.down_spot_y = self.middle_y + (self.middle_y)*(num >= 2)
        self.line_left_spot_x = self.left_spot_x
        self.line_right_spot_x = self.right_spot_x
        self.line_up_spot_y = self.up_spot_y
        self.line_down_spot_y = self.down_spot_y
        self.color_set = (0,139,0)
        self.max_back_img_number = queue_number
        self.back_img_num = queue_number
        self.img_q = Queue(maxsize = self.max_back_img_number)  
        if(num == 0):
            self.line_right_spot_x = self.line_right_spot_x - self.line_offset
            self.line_down_spot_y = self.line_down_spot_y - self.line_offset
            self.right_thickness = self.thin
            self.down_thickness = self.thin

            self.explosion_bound_top = self.line_W
            self.explosion_bound_bottom = self.bound_h - self.line_W
            self.explosion_bound_left = self.line_W
            self.explosion_bound_right = self.bound_w - self.line_W
            
        elif(num == 1):
            self.line_left_spot_x = self.line_left_spot_x + self.line_offset
            self.line_down_spot_y = self.line_down_spot_y - self.line_offset
            self.left_thickness = self.thin
            self.down_thickness = self.thin

            self.explosion_bound_top = self.line_W
            self.explosion_bound_bottom = self.bound_h - self.line_W
            self.explosion_bound_left = self.bound_w 
            self.explosion_bound_right = self.bound_w * 2 - int(self.line_W * 1.5)

            self.position_x = self.right_x
            
        elif(num == 2):
            self.line_right_spot_x = self.line_right_spot_x - self.line_offset
            self.line_up_spot_y = self.line_up_spot_y + self.line_offset
            self.right_thickness = self.thin
            self.up_thickness = self.thin

            self.explosion_bound_top = self.bound_h
            self.explosion_bound_bottom = self.bound_h * 2 - int(self.line_W * 1.5)
            self.explosion_bound_left = self.line_W
            self.explosion_bound_right = self.bound_w - self.line_W

            self.position_y = self.bottom_y
            
        elif(num == 3):
            self.line_left_spot_x = self.line_left_spot_x + self.line_offset
            self.line_up_spot_y = self.line_up_spot_y + self.line_offset
            self.up_thickness = self.thin
            self.left_thickness = self.thin

            self.explosion_bound_top = self.bound_h
            self.explosion_bound_bottom = self.bound_h * 2 - int(self.line_W * 1.5)
            self.explosion_bound_left = self.bound_w
            self.explosion_bound_right = self.bound_w *2 - int(self.line_W * 1.5)

            self.position_x = self.right_x
            self.position_y = self.bottom_y
            
        self.fireman_bound_top = self.line_up_spot_y + 25
        self.fireman_bound_bottom = self.line_down_spot_y - 50
        self.fireman_bound_left = self.line_left_spot_x + 25
        self.fireman_bound_right = self.line_right_spot_x - 50


    def blink_for_line(self):
        if(self.draw_line_blinking_flag):
            self.blink_count += 1
            if(self.blink_count >= 20):
                self.draw_line_blinking_flag = False
                self.blink_count = 0
            else:
                if(self.blink_count % 2 == 0):
                    return True ##### red line
                else:
                    return False ##### yellow line
        return True ##### red line

    def set_help2(self,flag):
        if(flag):
            if(self.first_recv_help2):
                self.help2_flag = True
                self.first_recv_help2 = False
                self.blink_count = 0
                self.draw_line_blinking_flag = True
        else:
            self.help2_flag = False
            self.draw_line_blinking_flag = False
            self.first_recv_help2 = True


    def except_for_img(self):
        img_binary = b''
        self.remain_package_size = 0
        self.recv_ir_flag = False
        self.recv_flir_flag = False

    def set_info(self, num, ip_position):
        self.id_num = num
        self.ip_addr = ip_position
        self.color_set = (0,139,0)

    def set_threshold(self, th70_or_100, num):
        if(th70_or_100 == 1):
            ###### set the 70 degree threshold of flir value ######
            self.th_70 = num
        else:
            ###### set the 100 degree threshold of flir value ######
            self.th_100 = num

    def set_namespace(self, my_namespace_img):
        ###### set the image with name ######
        self.first_flag = False
        self.namespace_img = my_namespace_img

    def set_sos_flag(self, flag):
        if(flag):
            if(self.first_recv_sos):
                self.sos_flag = True
                self.first_recv_sos = False
        else:
            self.sos_flag = False
            self.first_recv_sos = True

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

    def set_visible(self, flag):
        self.visible_flag = flag

    def set_name(self, myname):
        self.name = myname

    def get_name(self):
        return self.name
        
    def get_package_size(self):
        return self.remain_package_size

    def set_package(self, package_num, ir_or_flir):
        self.img_package_size = package_num
        self.remain_package_size = package_num
        if(ir_or_flir == 1):
            self.recv_ir_flag = True
        elif(ir_or_flir == 2):
            self.recv_flir_flag = True
        else:
            self.recv_ir_flag = False
            self.recv_flir_flag = False

    def set_send_package(self,num):
        self.send_package_size = num

    def decrease_remain_send_package(self):
        self.remain_send_size = self.send_package_size - self.sended_size
        if(self.remain_send_size <= 0):
            self.send_img_flag = False
            self.sended_size = 0
            self.send_package_size = 0

    def combine_recv_img(self,recv_str):
        flag = False
        self.img_binary += recv_str
        self.remain_package_size = self.img_package_size - len(self.img_binary)
        ###### image recv complete ######
        if(self.remain_package_size <= 0):
            flag = self.decode_img(self.img_binary[0:self.img_package_size])
            if(len(self.img_binary) > self.img_package_size):
                self.msg_binary = self.img_binary[self.img_package_size:len(self.img_binary)]
            self.set_package(-1,0)
            self.img_binary = b''
        return flag
    
    def combine_recv_msg(self,recv_str):
        msg = ""
        self.msg_binary += recv_str
        self.remain_msg_size -= len(recv_str)
        ###### msg recv complete ######
        if(len(self.msg_binary) >= self.msg_size):
            try:
                msg = self.msg_binary[0:self.msg_size].decode().strip()
            except Exception as e:
                print("error in decode msg",e.args)
            if(len(self.msg_binary) > self.msg_size):
                self.img_binary = self.msg_binary[self.msg_size:len(self.msg_binary)]
            self.msg_binary = b''
            self.remain_msg_size = self.msg_size
        return msg


    def set_back_img_num(self):
        self.back_img_num = self.img_q.qsize()

    def read_img(self,back_flag):
        if(self.visible_flag):
            if(self.disconnect_flag):
                if(back_flag):
                    if(self.back_img_count < self.back_img_num):   
                        return_img = self.img_q.get().copy()
                        self.img_q.put(return_img.copy())
                        self.back_img_count += 1
                        return return_img
                    else:
                        return self.img_show
                else:
                    self.back_img_count = 0
                    return self.img_show
            else:
                return self.img_show
        else:
            return self.img_white
        return self.img_white

    def read_combine_img(self):
        return self.img_combine

    def decode_img(self, binary):
        try:
            if(self.recv_ir_flag):
                ###### decode ir image ######
                self.recv_ir_flag = False
                data = np.fromstring(binary, dtype = 'uint8')
                data = cv2.imdecode(data, 1)
                self.img_ir = np.reshape(data, (self.height, self.weight, 3))
                return False
            elif(self.recv_flir_flag):
                ###### decode flir value ######
                self.recv_flir_flag = False
                data = struct.unpack("4800I",binary)
                data = (np.asarray(data)).astype(np.float32)
                if(np.sum((data> self.th_100)) >= (data.size / 3)):
                    ###### if the red area more one third of pic, rise the in_danger_flag ######
                    self.in_danger_flag = True
                data = np.reshape(data, (60,80,1))
                ###### if over threshold, replace part of ir image with red or green color ######
                dst = cv2.resize(data, (self.weight,self.height), interpolation= cv2.INTER_CUBIC)
                dst = np.dstack([dst]*3)
                tmp = self.img_ir.copy()
                dst = cv2.warpPerspective(dst,self.matrix, (self.weight,self.height))

                np.place(tmp, (dst > self.th_100), (0,0,255))
                np.place(tmp, ((dst > self.th_70)&(dst <= self.th_100)), (163,255,197))
                before_rotate_img = cv2.addWeighted(self.img_ir, 0.5, tmp, 0.5, 0)
                
                ###### rotate image ######
                rotate_img = cv2.warpAffine(before_rotate_img, self.M, (self.weight,self.height))
                self.img_combine = rotate_img
                ###### put the warning message on pic ######
                if(self.in_danger_flag | self.in_explosion_flag):
                    cv2.putText(self.img_combine, "In danger area !", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
                    self.draw_count += 1
                elif(self.closing_danger_flag):
                    cv2.putText(self.img_combine, "Close to danger area", (20,40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
                    self.draw_count += 1
                if(self.send_over_time_flag):
                    cv2.putText(self.img_combine, "You should come out !", (20,(40 + self.draw_count*30)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
                    self.draw_count += 1
                if(self.send_save_msg_flag):
                    cv2.putText(self.img_combine, "You will be saved !", (20,(40 + self.draw_count*30)), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 3)
                self.draw_count = 0
                ###### concatenate the img_combine and namespace ######
                self.img_show = np.concatenate((self.namespace_img, self.img_combine), axis=0)
                if(self.img_q.full()):
                    self.img_q.get()
                self.img_q.put(self.img_show.copy())
                self.send_img_flag = True
                return True
            return False

        except Exception as e:
            print("error in decode image",e.args)
            ###### if decode image fail, show the white image ######
            self.img_show = self.img_white
            self.img_binary = b''
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
#change distance
            dist = dist + self.dist_save # avoid error
            dist_cm = dist*100 # change meter to centimeter
            if dist_cm < 70:
                self.dist_save = self.dist_save + dist
            else:
                self.dist_save = 0
                map_cm = dist_cm/228.69 # change the billy ruler
                pixel_num = int(map_cm*100/1.5) # change to pixel
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

