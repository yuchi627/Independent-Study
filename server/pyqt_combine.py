from windows import Ui_Form
from client_struct import client
import selectors
import socket
import numpy as np
import os
import sys
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtGui import *
from PyQt5.QtCore import QTimer, Qt
import cv2
import time
#import keyboard
import types

class AppWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initVar() 
        self.timer=QTimer(self)
        self.timer.timeout.connect(self.update_image)
        self.timer.start(100)

        self.timer2 = QTimer(self)
        self.timer2.timeout.connect(self.get_socket_data)
        self.timer2.start(10)

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.ui.btn_info.clicked.connect(self.on_click_btn_info)
        self.ui.btn_map.clicked.connect(self.on_click_btn_map)
        self.ui.btn_image.clicked.connect(self.on_click_btn_image)
        self.ui.btn_choose.setEnabled(False)
        self.ui.btn_ok.setEnabled(False)     

        self.ui.label.setScaledContents(True)
        self.offset_x = self.ui.label.geometry().width()
        self.offset_y = self.ui.label.geometry().height()

        self.img_map_loading()
        self.socket_initialize()
        #self.showMaximized()
        self.show()

    def initVar(self):
        self.image_image = np.zeros((800,800,3),np.uint8)
        self.image_map = np.zeros((800,800,3),np.uint8)
        self.image_info = np.zeros((800,800,3),np.uint8)
        self.keep = np.zeros((800,800,3),np.uint8)
       # self.image = np.zeros((800,800,3),np.uint8)
        self.img_fireman = [ ]
        self.offset_x = 1
        self.offset_y = 1
        self.image_image_flag = False
        self.image_map_flag = True
        self.image_info_flag = False   
        self.middle_x = 1170
        self.middle_y = 700
        self.keep_fire = []
        self.host = '172.20.10.2'
        self.port = 8888
        self.time_press = 0
        self.info_flag = 0
        self.client_list = [client(0),client(1),client(2),client(3)]
        self.connection_num = np.zeros(4)
        self.subplot_count = [0, 1, 2, 3]
        self.client_dict = {"client":1}
        self.refresh_map = False
        self.refresh_img = False
        self.click_to_cancel = False
        self.name_space_height = 50 
        self.resize_height = 480+200
        self.resize_weight = 640+600
        self.height = 480
        self.weight = 640
        self.click_client = 0    ##### the client you click in window
        self.x_bound = 620   ##### window x axis bound
        self.y_bound = 340   ##### window y axis bound
        self.encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
        self.hot_mask = []
        self.map_width = 1174
        self.map_height = 705
        self.max_x = self.map_width*2
        self.max_y = self.map_height*2
        #---------------------------------------------------------#
        self.inti_flag = -1
        self.init_time = 0

    def on_click_btn_info(self):
        self.image_image_flag = False
        self.image_map_flag = False
        self.image_info_flag = True
        self.ui.btn_choose.setEnabled(False)
        self.ui.btn_ok.setEnabled(False)

    def on_click_btn_map(self):
        self.image_image_flag = False
        self.image_map_flag = True
        self.image_info_flag = False
        self.ui.btn_choose.setEnabled(True)
        self.ui.btn_ok.setEnabled(True)

    def on_click_btn_image(self):
        self.image_image_flag = True
        self.image_map_flag = False
        self.image_info_flag = False
        self.ui.btn_choose.setEnabled(False)
        self.ui.btn_ok.setEnabled(False)     

    def update_image(self):
        image = self.image_map.copy()
        if(self.image_image_flag):
            image = self.image_image.copy()
        elif(self.image_map_flag):
            image = self.image_map.copy()
        elif(self.image_info_flag):
            image = self.image_info.copy()
        else:
            pass
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#        cv2.imshow("Image",image)
#        cv2.waitKey(0)
        QIm = QImage(image.data, image.shape[1], image.shape[0],image.shape[1] *image.shape[2],QImage.Format_RGB888)
        self.ui.label.setPixmap(QPixmap.fromImage(QIm))

    def mousePressEvent(self,event):
        if(event.button() == Qt.LeftButton):
            pass
            #print("Left Mouse, x: ",event.pos().x())
            #print("Left Mouse, y: ",event.pos().y())

    def mouseReleaseEvent(self,event):
        press_x = int(event.pos().x()*self.offset_x)
        press_y = int(event.pos().y()*self.offset_y)
        if(event.button() == Qt.LeftButton):
            if(self.image_map_flag):
                i = 0
                while(i<4):
                    if(self.connection_num[i] == 1 and self.client_list[i].set_start == False):
                        self.client_list[i].position_x = press_x
                        self.client_list[i].position_y = press_y
                        self.client_list[i].set_start = True
                        #print("x: ",self.client_list[i].position_x)
                        #print("y: ",self.client_list[i].position_y)
                        break
                    elif(self.connection_num[i] == 1 and self.client_list[i].direction == -1):
                        if(abs(press_x - self.client_list[i].position_x) > abs(press_y- self.client_list[i].position_y)):
                            if(press_x > self.client_list[i].position_x):
                                self.client_list[i].direction = 90
                            else:
                                self.client_list[i].direction = 270
                        else:
                            if(press_y > self.client_list[i].position_y):
                                self.client_list[i].direction = 180
                            else:
                                self.client_list[i].direction = 0
                        #print("dir: ",self.client_list[i].direction)
                        break
                    else:
                        pass
                    i += 1
                #print("Left Mouse, x: ",event.pos().x())
                #print("Left Mouse, y: ",event.pos().y())
            elif(self.image_image_flag):
                self.click_to_cancel = True
                if((event.pos().x() <= self.x_bound) and (event.pos().y() <= self.y_bound)):
                    ##### client[0]
                    self.click_client = 0
                elif((event.pos().x() >= self.x_bound) and (event.pos().y() <= self.y_bound)):
                    ##### client[1]
                    self.click_client = 1
                elif((event.pos().x() <= self.x_bound) and (event.pos().y() >= self.y_bound)):
                    ##### client[2]
                    self.click_client = 2
                elif((event.pos().x() >= self.x_bound) and (event.pos().y() >= self.y_bound)):
                    ##### client[3]
                    self.click_client = 3
                else:
                    self.click_to_cancel = False     
            else:
                pass
        else:
            pass

    def img_map_loading(self):
        fireman_img_map_path = "../IMAGE/fireman.png"
        map_img_map_path = "../IMAGE/1f.png"
        if(os.path.isfile(fireman_img_map_path)):
            print("Reading FireFighter Image...")
            while(len(self.img_fireman) == 0):
                self.img_fireman = cv2.imread(fireman_img_map_path,-1)
            print(self.img_fireman.shape)
            self.img_fireman = cv2.resize(self.img_fireman,(50,50))
            #self.img_fireman = cv2.cvtColor(self.img_fireman,cv2.COLOR_RGB2BGR)
        else:
            print("There is no FireFighter Image")

        self.image_map = [] 
        print("Reading Environment Map...")
        if(os.path.isfile(map_img_map_path)):
            while(len(self.image_map) == 0):
                self.image_map = cv2.imread(map_img_map_path)
        print("Merge Map For Four FireFighters...")
        self.image_map = np.hstack((self.image_map,self.image_map))
        self.image_map = np.vstack((self.image_map,self.image_map))
 
        print("Drawing Security Line...")
        self.image_map = cv2.line(self.image_map,(5,5),(self.middle_x*2,5),(0,139,0),10,6)
        self.image_map = cv2.line(self.image_map,(5,self.middle_y),(self.middle_x*2,self.middle_y),(0,139,0),10,6)
        self.image_map = cv2.line(self.image_map,(5,self.middle_y*2),(self.middle_x*2,self.middle_y*2),(0,139,0),10,6)
        self.image_map = cv2.line(self.image_map,(5,5),(5,self.middle_y*2),(0,139,0),10,6)
        self.image_map = cv2.line(self.image_map,(self.middle_x,5),(self.middle_x,self.middle_y*2),(0,139,0),10,6)
        self.image_map = cv2.line(self.image_map,(self.middle_x*2,5),(self.middle_x*2,self.middle_y*2),(0,139,0),10,6)
 
        print("Set Initialize Map")
        self.keep = self.image_map.copy()
        #self.image_map = img_map.copy()
        #self.image = img_map.copy()
        self.hot_mask = np .zeros(self.image_map.shape,np.uint8)
        self.draw_layer(0)
        self.keep_fire = self.image_map.copy()
        self.offset_x = self.image_map.shape[1] / self.offset_x
        self.offset_y = self.image_map.shape[0] / self.offset_y

    def socket_initialize(self):    
        self.sel = selectors.DefaultSelector()
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((self.host,self.port))
        lsock.listen()
        print('listening on', (self.host, self.port))
        lsock.setblocking(False)
        self.sel.register(lsock, selectors.EVENT_READ, data=None)
        print("Waiting For Connection...")


    def get_socket_data(self):
        '''
        if(keyboard.is_pressed('1') and time.time() - self.time_press > 1):
            self.time_press = time.time()
            self.info_flag = (self.info_flag != 0)*1 - 1
            #print("pressed 1 , info_flag: ",self.info_flag)
        elif(keyboard.is_pressed('2') and time.time() - self.time_press > 1):
            self.time_press = time.time()
            self.info_flag = (self.info_flag != 1)*2 - 1
            #print("pressed 2 , info_flag: ",self.info_flag)
        elif(keyboard.is_pressed('3') and time.time() - self.time_press > 1):
            self.time_press = time.time()
            self.info_flag = (self.info_flag != 2)*3 - 1
            #print("pressed 3 , info _flag: ",self.info_flag)
        elif(keyboard.is_pressed('4') and time.time() - self.time_press > 1):
            self.time_press = time.time()
            self.info_flag = (self.info_flag != 3)*4 - 1
            #print("pressed 4 , info_flag: ",self.info_flag)
        else:  
           pass
        '''
        info_image = np.zeros((800,800,3),np.uint8)
         #---------------------------------#
        events = self.sel.select(timeout=0.01)
        for key, mask in events:
            if key.data is None:
                self.accept_wrapper(key.fileobj)
            else:
                self.service_connection(key, mask)
                
                if(self.refresh_img or self.refresh_map or self.info_flag >= 0):
                    if(self.refresh_img):
                        self.refresh_img = False
                        ###### concatenate and plot image ######
                        img_concate_Hori=np.concatenate((self.client_list[0].read_img(),self.client_list[1].read_img()),axis=1)
                        img_concate_Verti=np.concatenate((self.client_list[2].read_img(),self.client_list[3].read_img()),axis=1)
                        img_toshow = np.concatenate((img_concate_Hori,img_concate_Verti),axis=0)
                        img_toshow = cv2.resize(img_toshow,(self.resize_weight,self.resize_height),interpolation=cv2.INTER_CUBIC)
                        self.image_image = img_toshow.copy()
                        #cv2.imshow(img_window_name,img_toshow)
                        #cv2.waitKey(1)
                    if(self.refresh_map):
                            #print("refresh map")
                        #self.image_map = self.image.copy()
                        self.refresh_map = False
                            #-------------------------------------------------------------#
                            # to show image
 #                       cv2.imshow(map_window_name,image)
                            # Show 我們的圖
                            #-----------------------------------------------------------------#
                        ###
                    if(self.info_flag >= 0):
                        time_str = str(self.client_list[self.info_flag].time_pass)
                        time_str = time_str.partition('.')[0]+"."+time_str.partition('.')[2][0:1]
                        cv2.putText(info_image,"Name: "+str(self.client_list[self.info_flag].name), (10, 40), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 255, 0), 1, cv2.LINE_AA)
                        cv2.putText(info_image,"Number: "+str(self.client_list[self.info_flag].fire_num), (10, 80), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 255, 0), 1, cv2.LINE_AA)
                        cv2.putText(info_image,' '.join(["Time Pass:",time_str,"secs"]), (10, 120), cv2.FONT_HERSHEY_SIMPLEX,1, (255, 255, 0), 1, cv2.LINE_AA)
                        self.image_info = info_image.copy()
#                        cv2.imshow(info_window_name,info_image)                        
                        ###
                   
#                    if cv2.waitKey(1) & 0xFF == ord('q'):
#                        break
                    if(self.click_to_cancel):
                        self.set_namespace_color(self.click_client,(255,255,255),(0, 0, 0))
                        self.client_list[self.click_client].set_sos_flag(False)
                        self.click_to_cancel = False
 
    def accept_wrapper(self,sock):
        conn, addr = sock.accept()  # Should be ready to read
        print('accepted connection from', addr)
    
        conn.setblocking(False)
        data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        self.sel.register(conn, events, data=data)
        ###### create an client object an put into dictionary with it's address ######
        min_num = min(self.subplot_count)
        ###### create an white image with client name ######
        self.client_list[min_num]=client(min_num)
        self.client_dict[str(addr[1])] = min_num
        ###### number remove from list subplot_count ######
        self.subplot_count.remove(min_num)
    
        #--------------------------------------------------------------#
        i = 0                                                             
        while(i<4):
            if(self.connection_num[i] == 0):
                self.client_list[i].set_info(i,addr)
                self.connection_num[i] = 1
                inti_flag = i
                break
            i = i + 1
            # add new connection
            # 創造一個新的Object給Device
        #--------------------------------------------------------------------#
    
        print("Client: ")
        print("\tnum: ",self.client_list[i].id_num)
        print("\tip_addr: ",self.client_list[i].ip_addr)
    
 
    def set_namespace_color(self,client_index,background_color,font_color):
        namespace_whiteimg = np.zeros((self.name_space_height,self.weight,3), np.uint8)
        namespace_whiteimg[:,:] = background_color
        name = self.client_list[client_index].get_name()
        cv2.putText(namespace_whiteimg, name, (200, 42), cv2.FONT_HERSHEY_SIMPLEX, 2, font_color, 3, cv2.LINE_AA)
        self.client_list[client_index].set_namespace(namespace_whiteimg)
 
    def service_connection(self,key, mask):
        sock = key.fileobj
        data = key.data
        if mask & selectors.EVENT_READ:
            recv_data = None
            client_host = self.client_dict[str(data.addr[1])]
            if(self.client_list[client_host].first_time_recv()):
                print("Getting Name...")
                recv_data = sock.recv(16)
                name = recv_data.decode()
                #name = (str)(client_list[client_host].get_num()) + "." + name
                self.client_list[client_host].set_name(name)
                ###### Default : white background black font ######
                self.set_namespace_color(client_host,(255,255,255),(0, 0, 0))   
                print("The Name is: ",name)
                self.init_time = time.time() 
            else:
                #print("get_package_size: ",self.client_list[client_host].get_package_size() )
                if(self.client_list[client_host].get_package_size() <= 0):
                    #try:
                    ###### recv the image size ######
                    recv_data = sock.recv(16)
                    recv_data_msg = recv_data.decode().strip()
                    #print("msg = ", recv_data_msg)
                    if("FLIR" in recv_data_msg):
                        #print("flir image size msg")
                        self.client_list[client_host].set_package(int(recv_data_msg[4:len(recv_data_msg)]),2)
                    elif("IR" in recv_data_msg):
                        #print("ir image size msg")
                        self.client_list[client_host].set_package(int(recv_data_msg[2:len(recv_data_msg)]),1)
                    elif("TH70" in recv_data_msg):
                        #print("TH70 msg")
                        self.client_list[client_host].set_threshold(1, float(recv_data_msg[4:len(recv_data_msg)]))
                    elif("TH100" in recv_data_msg):
                        #print("TH100 msg")
                        self.client_list[client_host].set_threshold(2, float(recv_data_msg[5:len(recv_data_msg)]))
                    elif(len(recv_data_msg) == 0):
                        pass
                    else:
                        #------------------------------------------------------------------#
                        for i in self.client_list:
                            if(i.ip_addr == data.addr):
                                i.time_pass = time.time() - self.init_time
                                #print(i.time_pass)
                                if("HELP2" in recv_data_msg):
                                    #print("HELP2")
                                    self.helpConditionExec("HELP2",i.id_num)
                                    self.client_list[client_host].set_sos_flag(True)
                                elif("HELP" in recv_data_msg):
                                    #print("HELP")
                                    self.helpConditionExec("HELP",i.id_num)
                                elif("num" in recv_data_msg):
                                    i.fire_num = recv_data_msg[3:len(recv_data_msg)]
                                    #print(i.fire_num)
                                else:
                                    #print("id: ",i.id_num)
                                    #print(recv_data_msg)
                                    self.drawNewSpot(recv_data_msg,i.id_num)                    
                                break
                            # Device 傳輸資料時, call 對應function
                        #--------------------------------------------------------------------#
                    '''
                    except Exception as e:
                        print ("error in get msg: ",e.args)
                        #pass
                    '''    
                else:
                    ###### recv the img ######
                    #print("image msg")
                    recv_data = sock.recv(self.client_list[client_host].get_package_size())
                    ###### concatenate recv msg to image ######
                    #print(type(recv_data))
                    self.client_list[client_host].combine_recv_img(recv_data)
                    self.client_list[client_host].decrease_package_size(len(recv_data))
                    if(self.client_list[client_host].get_package_size() <= 0):
                        ###### image recv complete ######
                        send_flag = self.client_list[client_host].decode_img()
                        if(send_flag):
                            self.refresh_img = True
                            send_flag = False
                            try:
                                combine = self.client_list[client_host].read_combine_img()
                                _,encode = cv2.imencode('.jpg', combine, self.encode_param)
                                data_combine = np.array(encode)
                                stringData = data_combine.tostring()
                                sock.send(str(len(stringData)).ljust(16).encode())
                                sock.send(stringData)
                            except Exception as e:
                                print("error in send image to client : ",e.args)
                            ###### decide which background color to brush ######
                            brush_background_ornot = self.client_list[client_host].brush_namespace_background()
                            if(brush_background_ornot == 1):
                                ###### Red background with white font ######
                                self.set_namespace_color(client_host,(0,0,255),(255, 255, 255))
                            elif (brush_background_ornot == 2):
                                ###### White background with black font ######
                                self.set_namespace_color(client_host,(255,255,255),(0, 0, 0))
                        self.client_list[client_host].set_package(-1,0)
 
            if not recv_data:
                print('closing connection to', data.addr)
                #-------------------------------------------------------------------#
                print(str(data.addr[0]))
                print(self.client_list[0].ip_addr)
                for i in self.client_list:
                    if(i.ip_addr == data.addr):
                        self.connection_num[i.id_num] = 0
                        self.client_list[i.id_num] = client(i.id_num)
                self.image_map = self.keep_fire.copy()
                self.refresh_map = True
                # Close Connection 的時候取消 Object
                #--------------------------------------------------------------------#
                self.client_list[self.client_dict[str(data.addr[1])]].set_visible(False)
                self.refresh_img = True
                self.subplot_count.append(self.client_dict[str(data.addr[1])])
                del self.client_dict[str(data.addr[1])]
                self.sel.unregister(sock)
                sock.close()

    def drawNewSpot(self,data,index):
        #print("drawNewSpot")
        self.image_map = self.keep.copy()
 
        left_spot_x = 5 + (self.middle_x-5)*(index%2)
        right_spot_x = self.middle_x + self.middle_x*(index%2)
        up_spot_y = 5 + (self.middle_y-5)*(index >= 2)
        down_spot_y = self.middle_y + (self.middle_y)*(index >= 2)
 
        self.client_list[index].color_set = (0,139,0)
        cv2.line(self.image_map,(left_spot_x,up_spot_y),(right_spot_x,up_spot_y),self.client_list[index].color_set,10,6)
        cv2.line(self.image_map,(left_spot_x,down_spot_y),(right_spot_x,down_spot_y),self.client_list[index].color_set,10,6)
        cv2.line(self.image_map,(left_spot_x,up_spot_y),(left_spot_x,down_spot_y),self.client_list[index].color_set,10,6)
        cv2.line(self.image_map,(right_spot_x,up_spot_y),(right_spot_x,down_spot_y),self.client_list[index].color_set,10,6)
 
        if("No Turn" in data):
             #print("index:",index)
            self.client_list[index].addNewPosition("No Turn",0)
        elif("Left" in data):
            self.client_list[index].addNewPosition("Left",0)
        elif("Right" in data):
            self.client_list[index].addNewPosition("Right",0)
        else:
            self.client_list[index].addNewPosition("No Turn",float(data))
        self.refresh_map = True
        self.draw_layer(index)     
        
        '''for i in range(0,4):
            self.image_map[self.client_list[i].position_y - 25 : self.client_list[i].position_y + 25 , self.client_list[i].position_x - 25 : self.client_list[i].position_x + 25] = self.img_fireman
            print("position",self.client_list[i].position_x,self.client_list[i].position_y)'''
        
    def helpConditionExec(self,message,index):
        self.drawNewSpot('0.0',index)
        if("HELP2" in message):
            self.client_list[index].color_set = (0,0,255)
        elif("HELP" in message):
            self.client_list[index].color_set = (0,165,255)
        else:
            pass
 
        left_spot_x = 5 + (self.middle_x-5)*(index%2)
        right_spot_x = self.middle_x + self.middle_x*(index%2)
        up_spot_y = 5 + (self.middle_y-5)*(index >= 2)
        down_spot_y = self.middle_y + (self.middle_y)*(index >= 2)
 
        cv2.line(self.image_map,(left_spot_x,up_spot_y),(right_spot_x,up_spot_y),self.client_list[index].color_set,10,6)
        cv2.line(self.image_map,(left_spot_x,down_spot_y),(right_spot_x,down_spot_y),self.client_list[index].color_set,10,6)
        cv2.line(self.image_map,(left_spot_x,up_spot_y),(left_spot_x,down_spot_y),self.client_list[index].color_set,10,6)
        cv2.line(self.image_map,(right_spot_x,up_spot_y),(right_spot_x,down_spot_y),self.client_list[index].color_set,10,6)
    
        self.refresh_map = True

    def replace_roi(self, dst, num, y0, y1, x0, x1, roi):
        dst[y0 : y1 , x0 : x1] = roi
        if(num==0):
            next_y0 = y0 + self.map_height
            next_y1 = y1 + self.map_height
            next_x0 = x0 + self.map_width
            next_x1 = x1 + self.map_width
            dst[y0 : y1 , x0 : x1] = roi
            dst[y0 : y1 , next_x0 : next_x1] = roi
            dst[next_y0 : next_y1 , x0 : x1] = roi
            dst[next_y0 : next_y1 , next_x0 : next_x1] = roi
        elif(num==1):
            last_x0 = x0 - self.map_width
            last_x1 = x1 - self.map_width
            next_y0 = y0 + self.map_height
            next_y1 = y1 + self.map_height
            dst[y0 : y1 , x0 : x1] = roi
            dst[y0 : y1 , last_x0 : last_x1] = roi
            dst[next_y0 : next_y1 , x0 : x1] = roi
            dst[next_y0 : next_y1 , last_x0 : last_x1] = roi
        elif(num==2):
            next_x0 = x0 + self.map_width
            next_x1 = x1 + self.map_width
            last_y0 = y0 - self.map_height
            last_y1 = y1 - self.map_height
            dst[y0 : y1 , x0 : x1] = roi
            dst[y0 : y1 , next_x0 : next_x1] = roi
            dst[last_y0 : last_y1 , x0 : x1] = roi
            dst[last_y0 : last_y1 , next_x0 : next_x1] = roi
        else:
            last_y0 = y0 - self.map_height
            last_y1 = y1 - self.map_height
            last_x0 = x0 - self.map_width
            last_x1 = x1 - self.map_width
            dst[y0 : y1 , x0 : x1] = roi
            dst[y0 : y1 , last_x0 : last_x1] = roi
            dst[last_y0 : last_y1 , x0 : x1] = roi
            dst[last_y0 : last_y1 , last_x0 : last_x1] = roi

    def draw_layer(self,num):
        
        alpha_s = self.img_fireman[:,:,3] / 255.0
        alpha_l = 1.0 - alpha_s
        if(self.client_list[num].position_x > self.client_list[num].bound_right):
            x_offset = self.client_list[num].bound_right
        elif(self.client_list[num].position_x < self.client_list[num].bound_left):
            x_offset = self.client_list[num].bound_left
        else:
            x_offset = self.client_list[num].position_x-25
        if(self.client_list[num].position_y > self.client_list[num].bound_buttom):
            y_offset = self.client_list[num].bound_buttom
        elif(self.client_list[num].position_y < self.client_list[num].bound_top):
            y_offset = self.client_list[num].bound_top
        else:
            y_offset = self.client_list[num].position_y-25

        #x_offset = self.client_list[num].position_x-25
        #y_offset = self.client_list[num].position_y-25
        if(self.client_list[num].in_danger_flag):
            self.replace_roi(self.hot_mask, num, y_offset, self.img_fireman.shape[0] + y_offset, x_offset, self.img_fireman.shape[1] + x_offset, (1,1,1))
            self.client_list[num].in_danger_flag = False
        else:
            self.replace_roi(self.hot_mask, num, y_offset, self.img_fireman.shape[0] + y_offset, x_offset, self.img_fireman.shape[1] + x_offset, (0,0,0))

        index_tuple = np.where(self.hot_mask[:,:,0]==1)
        row = index_tuple[0]
        col = index_tuple[1]
        for c in range(1,3):     
            self.image_map[row,col,c] = self.image_map[row, col, c]*0.5
        self.image_map[row, col, 0] = self.image_map[row, col, 0]*0.5 + 122
        for i in range(4):
            ###### avoid out of bounds ######
            if(self.client_list[i].position_x > self.client_list[i].bound_right):
                x_offset = self.client_list[i].bound_right
            elif(self.client_list[i].position_x < self.client_list[i].bound_left):
                x_offset = self.client_list[i].bound_left
            else:
                x_offset = self.client_list[i].position_x-25
            if(self.client_list[i].position_y > self.client_list[i].bound_buttom):
                y_offset = self.client_list[i].bound_buttom
            elif(self.client_list[i].position_y < self.client_list[i].bound_top):
                y_offset = self.client_list[i].bound_top
            else:
                y_offset = self.client_list[i].position_y-25
            x2 = self.img_fireman.shape[1] + x_offset
            y2 = self.img_fireman.shape[0] + y_offset
            for c in range(3):
                self.image_map[y_offset:y2 , x_offset:x2, c] = (alpha_s * self.img_fireman[:,:,c] + alpha_l * self.image_map[y_offset:y2 , x_offset:x2, c])
            ###### detect_danger ######
            x1 = self.client_list[i].position_x-50
            y1 = self.client_list[i].position_y-50
            x2 = self.client_list[i].position_x+50
            y2 = self.client_list[i].position_y+50
            if x1 < 0:
                x1 = 0
            elif x2 > self.max_x:
                x2 = self.max_x
            if y1 < 0:
                y1 = 0
            elif y2 > self.max_y:
                y2 = self.max_y	
            if np.sum(self.hot_mask[y1:y2, x1:x2]) > 0:
                self.client_list[i].closing_danger_flag = True
            else:
                self.client_list[i].in_danger_flag = False
                self.client_list[i].closing_danger_flag = False
            #print(i,client_list[i].in_danger_flag, client_list[i].closing_danger_flag)


app = QApplication(sys.argv)
w = AppWindow()
w.show()
sys.exit(app.exec_())
