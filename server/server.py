import selectors
import socket
import types
import matplotlib.pyplot as plt
#import matplotlib.image as mpimg
import numpy as np
import cv2
from client_struct import client
import threading
import time
##### use "ifconfig" to find your ip
host = '192.168.68.196'
port = 6667
window_name = 'Firefighter'
##### Default four element array
client_list = [client(),client(),client(),client()]
resize_height = 480+200
resize_weight = 640+600
name_space_height = 50
height = 480
weight = 640
refresh = False ##### refresh window
click_to_cancel = False ##### cancel the sos signal
click_client = 0    ##### the client you click in window
x_bound = 620   ##### window x axis bound
y_bound = 340   ##### window y axis bound


def emergency_cancel(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONUP:  
        global click_to_cancel
        ##### Left Button Click
        print("click:x= ",x,"  y= ",y)
        click_to_cancel = True
        if((x<=x_bound) and (y<= y_bound)):
            ##### client[0]
            print("client 0")
            click_client = 0
        elif((x>=x_bound) and (y<= y_bound)):
            ##### client[1]
            print("client 1")
            click_client = 1
        elif((x<=x_bound) and (y>= y_bound)):
            ##### client[2]
            print("client 2")
            click_client = 2
        elif((x>=x_bound) and (y>= y_bound)):
            ##### client[3]
            print("client 3")
            click_client = 3
        else:
            clicl_to_cancel = False


            

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
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
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        global refresh
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
                    package_num = recv_data.decode()
                    ##### recv the SOS message
                    if("SOS" in package_num):
                        print("Save him!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        client_list[client_host].set_sos_flag(True)
                        ##### send message back to client
                        sock.send("I will save you".encode())
                    else:
                        client_list[client_host].package_set(int(package_num))
                except Exception as e:
                    print (e.args)
            else:
                ##### recv the img
                recv_data = sock.recv(client_list[client_host].package_size())
                ##### concatenate recv msg to img
                client_list[client_host].img_combine(recv_data)
                client_list[client_host].package_decrease(len(recv_data))
                if(client_list[client_host].package_size() <= 0):
                    ##### img recv complete
                    client_list[client_host].img_decode()
                    client_list[client_host].package_set(-1)
                    refresh = True
                    ##### decide which background color to brush
                    brush_background_ornot = client_list[client_host].brush_background()
                    if(brush_background_ornot == 1):
                        ##### Red background white font
                        set_namespace_color(client_host,(0,0,255),(255, 255, 255))
                    elif (brush_background_ornot == 2):
                        ##### White background black font
                        set_namespace_color(click_client,(255,255,255),(0, 0, 0))
                    

        if not recv_data:
            print('closing connection to', data.addr)
            client_list[client_dict[str(data.addr[1])]].set_visible(False)
            refresh = True
            subplot_count.append(client_dict[str(data.addr[1])])
            del client_dict[str(data.addr[1])]
            sel.unregister(sock)
            sock.close()

if __name__ == "__main__":
    try:
        ##### create a figure with subplot 2*5
        subplot_count = [0,1,2,3]
        width = 14
        length = 6
        cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
        cv2.setMouseCallback(window_name, emergency_cancel)
        cv2.moveWindow(window_name, 20,20)  # Move it to (40,30)
        ##### create a dictionary
        client_dict = {"client":1}
        sel = selectors.DefaultSelector()
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lsock.bind((host, port))
        lsock.listen()
        print('listening on', (host, port))
        lsock.setblocking(False)
        sel.register(lsock, selectors.EVENT_READ, data=None)
        while True:
            events = sel.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    service_connection(key, mask)
                    if(refresh):
                        refresh = False
                        ##### concate and plot image
                        img_concate_Hori=np.concatenate((client_list[0].img_read(),client_list[1].img_read()),axis=1)
                        img_concate_Verti=np.concatenate((client_list[2].img_read(),client_list[3].img_read()),axis=1)
                        img_toshow = np.concatenate((img_concate_Hori,img_concate_Verti),axis=0)
                        img_toshow = cv2.resize(img_toshow,(resize_weight,resize_height),interpolation=cv2.INTER_CUBIC)
                        cv2.imshow(window_name,img_toshow)
                        cv2.waitKey(1)
                    if(click_to_cancel):
                        set_namespace_color(click_client,(255,255,255),(0, 0, 0))
                        client_list[click_client].set_sos_flag(False)
                        click_to_cancel = False

                    
    finally:
        lsock.close()
        plt.close()
        cv2.destroyAllWindows()
        print("close socket")
