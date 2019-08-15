import selectors
import socket
import types
import numpy as np
import cv2
from client_struct import client
import threading
import time
from structure_connect import StructureConnection
import keyboard
import os

##### use "ifconfig" to find your ip
#host = '192.168.208.126'
host = '127.0.0.1'
#host = '192.168.208.140'
port = 8888

window_name = 'Firefighter'
##### Default four element array
client_list = [client(),client(),client(),client()]
resize_height = 480+200
resize_weight = 640+600
name_space_height = 50
height = 480
weight = 640
refresh_img = False ##### refresh window
refresh_map = False ##### refresh map
click_to_cancel = False ##### cancel the sos signal
click_client = 0    ##### the client you click in window
x_bound = 620   ##### window x axis bound
y_bound = 340   ##### window y axis bound
#---------------------------------------------------------#
inti_flag = -1
connection_arr = list()
connection_num = np.zeros(4)

image = []
keep = []
middle_x = 1170 
middle_y = 700
init_time = 0


def emergency_cancel(event, x, y, flags, param):
    global click_to_cancel,click_client
    if event == cv2.EVENT_LBUTTONUP:  
        ##### Left Button Click
        #print("click:x= ",x,"  y= ",y)
        click_to_cancel = True
        if((x<=x_bound) and (y<= y_bound)):
            ##### client[0]
            click_client = 0
        elif((x>=x_bound) and (y<= y_bound)):
            ##### client[1]
            click_client = 1
        elif((x<=x_bound) and (y>= y_bound)):
            ##### client[2]
            click_client = 2
        elif((x>=x_bound) and (y>= y_bound)):
            ##### client[3]
            click_client = 3
        else:
            click_to_cancel = False


            

def accept_wrapper(sock):
    global connection_arr, connection_num, inti_flag
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
#--------------------------------------------------------------------#
    i = 0
    while(i<4):
        if(connection_num[i] == 0):
            connection_arr[i] = StructureConnection(i,str(addr[0]))
            connection_num[i] = 1
            inti_flag = i
            break
        i = i + 1
    # add new connection
    # 創造一個新的Object給Device
#--------------------------------------------------------------------#
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    ##### create an client object an put into dictionary with it's address
    min_num = min(subplot_count)
    ##### create an white img with client name
    client_list[min_num]=client()
    client_dict[str(addr[1])] = min_num
    ##### number remove from list subplot_count
    subplot_count.remove(min_num)
    

def set_namespace_color(client_index,background_color,font_color):
    namespace_whiteimg = np.zeros((name_space_height,weight,3), np.uint8)
    namespace_whiteimg[:,:] = background_color
    name = client_list[client_index].get_name()
    cv2.putText(namespace_whiteimg, name, (200, 42), cv2.FONT_HERSHEY_SIMPLEX, 2, font_color, 3, cv2.LINE_AA)
    client_list[client_index].namespace_imgset(namespace_whiteimg)

def service_connection(key, mask):
    global connection_arr, connection_num, image, init_time

    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        global refresh_img,refresh_map
        recv_data = None
        client_host = client_dict[str(data.addr[1])]
        if(client_list[client_host].first_time_recv()):
            recv_data = sock.recv(16)
            name = recv_data.decode()
            #name = (str)(client_list[client_host].get_num()) + "." + name
            client_list[client_host].set_name(name)
            ##### Default : white background black font
            set_namespace_color(client_host,(255,255,255),(0, 0, 0))   
            
            
        else:
            if(client_list[client_host].package_size() < 0):
                try:
                    ##### recv the img size
                    recv_data = sock.recv(16)
                    recv_data_msg = recv_data.decode().strip()
                    '''
                    ##### recv the SOS message
                    if("SOS" in recv_data_msg):
                        print("SOS msg")
                        client_list[client_host].set_sos_flag(True)
                        ##### send message back to client
                        sock.send("I will save you".encode())
                    '''
                    if("SIZE" in recv_data_msg):
                        #print("image size msg")
                        client_list[client_host].package_set(int(recv_data_msg[4:len(recv_data_msg)]))
                    else:
                        #------------------------------------------------------------------#
                        for i in connection_arr:
                            if(i.ip_addr == str(data.addr[0])):
                                i.time_pass = time.time() - init_time
                                #print(i.time_pass)
                                if(recv_data_msg == "HELP"):
                                    print("HELP1")
                                    helpConditionExec("HELP",i.id_num)
                                elif(recv_data_msg == "HELP2"):
                                    print("in help2")
                                    #print("SOS msg")
                                    client_list[client_host].set_sos_flag(True)
                                    ##### send message back to client
                                    sock.send("I will save you".encode())
                                    helpConditionExec("HELP2",i.id_num)
                                elif(recv_data_msg[0:4] == "num_"):
                                    i.fire_num = recv_data_msg[4:len(recv_data_msg)]
                                    print(i.fire_num)
                                elif(recv_data_msg[0:5] == "name_"):
                                    i.fire_name = recv_data_msg[5:len(recv_data_msg)]
                                    print(i.fire_name)
                                elif(len(recv_data_msg) == 0):
                                    pass
                                else:
                                    drawNewSpot(recv_data_msg,i.id_num,img_fireman)                    
                                break
                            # Device 傳輸資料時, call 對應function
                        #--------------------------------------------------------------------#
                except Exception as e:
                    print (e.args)
            else:
                
                ##### recv the img
                #print("image msg")
                recv_data = sock.recv(client_list[client_host].package_size())
                ##### concatenate recv msg to img
                client_list[client_host].img_combine(recv_data)
                client_list[client_host].package_decrease(len(recv_data))
                if(client_list[client_host].package_size() <= 0):
                    ##### img recv complete
                    client_list[client_host].img_decode()
                    client_list[client_host].package_set(-1)
                    refresh_img = True
                    ##### decide which background color to brush
                    brush_background_ornot = client_list[client_host].brush_background()
                    if(brush_background_ornot == 1):
                        ##### Red background white font
                        set_namespace_color(client_host,(0,0,255),(255, 255, 255))
                    elif (brush_background_ornot == 2):
                        ##### White background black font
                        set_namespace_color(client_host,(255,255,255),(0, 0, 0))
                #except Exception as e:
                #    print(e.args)

        if not recv_data:
            print('closing connection to', data.addr)
            #-------------------------------------------------------------------#
            print(str(data.addr[0]))
            print(connection_arr[0].ip_addr)
            for i in connection_arr:
                if(i.ip_addr == str(data.addr[0])):
                    connection_num[i.id_num] = 0
            refresh_map = True
            # Close Connection 的時候取消 Object
            #--------------------------------------------------------------------#
            client_list[client_dict[str(data.addr[1])]].set_visible(False)
            refresh_img = True
            subplot_count.append(client_dict[str(data.addr[1])])
            del client_dict[str(data.addr[1])]
            sel.unregister(sock)
            sock.close()

 #######    # running handling
def drawNewSpot(data,index,img_fireman):
    global connection_arr, keep, image, inti_flag, refresh_map

    image = keep.copy()
    if(data != "HELP" or data != "HELP2"):
        if(index == 0):
            cv2.line(image,(5,5),(middle_x,5),(0,139,0),10,6)
            cv2.line(image,(5,middle_y),(middle_x,middle_y),(0,139,0),10,6)
            cv2.line(image,(5,5),(5,middle_y),(0,139,0),10,6)
            cv2.line(image,(middle_x,5),(middle_x,middle_y),(0,139,0),10,6)
        elif (index == 1):
            cv2.line(image,(middle_x,5),(middle_x*2,5),(0,139,0),10,6)
            cv2.line(image,(middle_x,middle_y),(middle_x*2,middle_y),(0,139,0),10,6)
            cv2.line(image,(middle_x*2,5),(middle_x*2,middle_y),(0,139,0),10,6)
            cv2.line(image,(middle_x,5),(middle_x,middle_y),(0,139,0),10,6)
        elif(index == 2):
            cv2.line(image,(5,middle_y),(5,middle_y*2),(0,139,0),10,6)
            cv2.line(image,(middle_x,middle_y),(middle_x,middle_y*2),(0,139,0),10,6)
            cv2.line(image,(5,middle_y),(middle_x,middle_y),(0,139,0),10,6)
            cv2.line(image,(5,middle_y*2),(middle_x,middle_y*2),(0,139,0),10,6)
        elif(index == 3):
            cv2.line(image,(middle_x,middle_y),(middle_x*2,middle_y),(0,139,0),10,6)
            cv2.line(image,(middle_x,middle_y*2),(middle_x*2,middle_y*2),(0,139,0),10,6)
            cv2.line(image,(middle_x,middle_y),(middle_x,middle_y*2),(0,139,0),10,6)
            cv2.line(image,(middle_x*2,middle_y),(middle_x*2,middle_y*2),(0,139,0),10,6)
        else:
            pass
        if(data == "No Turn" or data == "Left" or data == "Right"):
            print("index:",index)
            connection_arr[index].color_set = (0,139,0)
            connection_arr[index].addNewPosition(data,0)
        else:
            connection_arr[index].color_set = (0,139,0)
            connection_arr[index].addNewPosition("No Turn",float(data))
    refresh_map = True
    #print('refresh')
    for i in range(4):
        image[connection_arr[i].position_y-25 : connection_arr[i].position_y + 25 , connection_arr[i].position_x-25 : connection_arr[i].position_x + 25] = img_fireman

def helpConditionExec(message,num):
    global image
    if(message == "HELP"):
        connection_arr[num].color_set = (0,165,255)
        if(num == 0):
            cv2.line(image,(5,5),(middle_x,5),(0,165,255),10,6)
            cv2.line(image,(5,middle_y),(middle_x,middle_y),(0,165,255),10,6)
            cv2.line(image,(5,5),(5,middle_y),(0,165,255),10,6)
            cv2.line(image,(middle_x,5),(middle_x,middle_y),(0,165,255),10,6)
        elif (num == 1):
            cv2.line(image,(middle_x,5),(middle_x*2,5),(0,165,255),10,6) 
            cv2.line(image,(middle_x,middle_y),(middle_x*2,middle_y),(0,165,255),10,6)
            cv2.line(image,(middle_x*2,5),(middle_x*2,middle_y),(0,165,255),10,6)
            cv2.line(image,(middle_x,5),(middle_x,middle_y),(0,165,255),10,6)
        elif(num == 2):                                    
            cv2.line(image,(5,middle_y),(5,middle_y*2),(0,165,255),10,6) 
            cv2.line(image,(middle_x,middle_y),(middle_x,middle_y*2),(0,165,255),10,6)
            cv2.line(image,(5,middle_y),(middle_x,middle_y),(0,165,255),10,6)
            cv2.line(image,(5,middle_y*2),(middle_x,middle_y*2),(0,165,255),10,6)
        elif(num == 3): 
            cv2.line(image,(middle_x,middle_y),(middle_x*2,middle_y),(0,165,255),10,6)
            cv2.line(image,(middle_x,middle_y*2),(middle_x*2,middle_y*2),(0,165,255),10,6)
            cv2.line(image,(middle_x,middle_y),(middle_x,middle_y*2),(0,165,255),10,6)
            cv2.line(image,(middle_x*2,middle_y),(middle_x*2,middle_y*2),(0,165,255),10,6)
        else:    
            pass 
    elif (message == "HELP2"):
        connection_arr[num].color_set = (0,0,255)
        if(num == 0):
            cv2.line(image,(5,5),(middle_x,5),(0,0,255),10,6)
            cv2.line(image,(5,middle_y),(middle_x,middle_y),(0,0,255),10,6)
            cv2.line(image,(5,5),(5,middle_y),(0,0,255),10,6)
            cv2.line(image,(middle_x,5),(middle_x,middle_y),(0,0,255),10,6)
        elif (num == 1):
            cv2.line(image,(middle_x,5),(middle_x*2,5),(0,0,255),10,6) 
            cv2.line(image,(middle_x,middle_y),(middle_x*2,middle_y),(0,0,255),10,6)
            cv2.line(image,(middle_x*2,5),(middle_x*2,middle_y),(0,0,255),10,6)
            cv2.line(image,(middle_x,5),(middle_x,middle_y),(0,0,255),10,6)
        elif(num == 2):                                    
            cv2.line(image,(5,middle_y),(5,middle_y*2),(0,0,255),10,6) 
            cv2.line(image,(middle_x,middle_y),(middle_x,middle_y*2),(0,0,255),10,6)
            cv2.line(image,(5,middle_y),(middle_x,middle_y),(0,0,255),10,6)
            cv2.line(image,(5,middle_y*2),(middle_x,middle_y*2),(0,0,255),10,6)
        elif(num == 3): 
            cv2.line(image,(middle_x,middle_y),(middle_x*2,middle_y),(0,0,255),10,6)
            cv2.line(image,(middle_x,middle_y*2),(middle_x*2,middle_y*2),(0,0,255),10,6)
            cv2.line(image,(middle_x,middle_y),(middle_x,middle_y*2),(0,0,255),10,6)
            cv2.line(image,(middle_x*2,middle_y),(middle_x*2,middle_y*2),(0,0,255),10,6)
        else:    
            pass 
    else:
       pass
    refresh_map = True

def addNewPoint(event,x,y,flags,param):
    global inti_flag
    global connection_arr

    if inti_flag != -1 and event == cv2.EVENT_LBUTTONDOWN:
        if connection_arr[inti_flag].position_x ==25 and connection_arr[inti_flag].position_y == 25:
            connection_arr[inti_flag].position_x = x
            connection_arr[inti_flag].position_y = y 
        else:
            temp_x = x
            temp_y = y
            if abs(temp_x-connection_arr[inti_flag].position_x) > abs(temp_y - connection_arr[inti_flag].position_y):
                if temp_x < connection_arr[inti_flag].position_x:
                    connection_arr[inti_flag].direction = 270
                else:
                    connection_arr[inti_flag].direction = 90
            else:
                if temp_y > connection_arr[inti_flag].position_y:
                    connection_arr[inti_flag].direction = 180
                else:
                    connection_arr[inti_flag].direction = 0
            print ("dir: ",connection_arr[inti_flag].direction)
            inti_flag = -1

def show_info():
    os.system("sudo python3 show_info.py")    

if __name__ == "__main__":
    i = 0
    while(i<10):
        connection_arr.append(StructureConnection(0,"0"))
        i = i + 1
    
    img_fireman = cv2.imread("IMAGE/fireman.png")
    img_fireman = cv2.resize(img_fireman,(50,50))

    image = cv2.imread("IMAGE/1f.png")
    '''
    image1 = cv2.imread("IMAGE/1f.png")
    image2 = cv2.imread("IMAGE/1f.png")
    image3 = cv2.imread("IMAGE/1f.png")
    image = np.hstack((image,image1))
    image1 = np.hstack((image2,image3))
    image = np.vstack((image,image1))
    '''
    image = np.hstack((image,image))
    image = np.vstack((image,image))
    
    cv2.namedWindow("Image",0)
    cv2.setWindowProperty("Image",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN )
    
    image = cv2.line(image,(5,5),(middle_x*2,5),(0,139,0),10,6)
    image = cv2.line(image,(5,middle_y),(middle_x*2,middle_y),(0,139,0),10,6)
    image = cv2.line(image,(5,middle_y*2),(middle_x*2,middle_y*2),(0,139,0),10,6)
    image = cv2.line(image,(5,5),(5,middle_y*2),(0,139,0),10,6)
    image = cv2.line(image,(middle_x,5),(middle_x,middle_y*2),(0,139,0),10,6)
    image = cv2.line(image,(middle_x*2,5),(middle_x*2,middle_y*2),(0,139,0),10,6)

    cv2.setMouseCallback("Image",addNewPoint)
    keep = image.copy()

    #cv2.imshow("Image",image)
    
    ##### create a figure with subplot 2*5
    subplot_count = [0,1,2,3]
    cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(window_name, emergency_cancel)
    cv2.moveWindow(window_name, 20,20)  # Move it to (40,30)
    ##### create a dictionary
    client_dict = {"client":1}

    try:
        
        sel = selectors.DefaultSelector()
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, port))
        lsock.listen()
        print('listening on', (host, port))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)
        while True:
            #---------------------------------#
            #if(keyboard.is_pressed('i')):
            #    show_info()
            #---------------------------------#
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
                    if(refresh_img or refresh_map):
                        if(refresh_img):
                            refresh_img = False
                            ##### concate and plot image
                            img_concate_Hori=np.concatenate((client_list[0].img_read(),client_list[1].img_read()),axis=1)
                            img_concate_Verti=np.concatenate((client_list[2].img_read(),client_list[3].img_read()),axis=1)
                            img_toshow = np.concatenate((img_concate_Hori,img_concate_Verti),axis=0)
                            img_toshow = cv2.resize(img_toshow,(resize_weight,resize_height),interpolation=cv2.INTER_CUBIC)
                            cv2.imshow(window_name,img_toshow)
                            #cv2.waitKey(1)
                        if(refresh_map):
                            #print("show")
                            refresh_map = False
                            #-------------------------------------------------------------#
                            # to show image
                            cv2.imshow("Image",image)
                            '''
                            if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                            '''
                            # Show 我們的圖
                            #-----------------------------------------------------------------#
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    if(click_to_cancel):
                        set_namespace_color(click_client,(255,255,255),(0, 0, 0))
                        client_list[click_client].set_sos_flag(False)
                        click_to_cancel = False
            
                    
    finally:
        lsock.close()
        cv2.destroyAllWindows()
        print("close socket")
