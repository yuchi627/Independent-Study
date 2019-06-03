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
host = '192.168.68.195'
port = 6667
window_name = 'Firefighter'
##### ten element array
client_list = [client(),client(),client(),client(),client(),client(),client(),client(),client(),client()]
resize_height = 480+200
resize_weight = 640+600
name_space_height = 50
height = 480
weight = 640

#height = 240
#weight = 320

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
    ##### subplot number remove
    subplot_count.remove(min_num)
    

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        client_host = client_dict[str(data.addr[1])]
        t1= time.time()
        if(client_list[client_host].first_time_recv()):
            recv_data = sock.recv(16)
            name = recv_data.decode()
            namespace_whiteimg = np.zeros((name_space_height,weight,3), np.uint8)
            namespace_whiteimg[:,:] = (255,255,255)
            cv2.putText(namespace_whiteimg, name, (200, 42), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 1, cv2.LINE_AA)
            client_list[client_host].namespace_imgset(namespace_whiteimg)
            t2 = time.time()
            print("time=",t2-t1)
        else:
            if(client_list[client_host].package_size() < 0):
                try:
                    ##### recv the img size
                    recv_data = sock.recv(16)
                    package_num = recv_data.decode()
                    ##### recv the SOS message
                    if("SOS" in package_num):
                        print("Save him!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    else:
                        client_list[client_host].package_set(int(package_num))
                except Exception as e:
                    print(package_num)
                    print (e.args)
            else:
                ##### recv the img
                t0=time.time()
                recv_data = sock.recv(client_list[client_host].package_size())
                ##### concatenate recv msg to img
                client_list[client_host].img_combine(recv_data)
                client_list[client_host].package_decrease(len(recv_data))
                t= time.time()
                print("recv time = ",t-t0)
                #t1 = time.time()
                if(client_list[client_host].package_size() <= 0):
                    ##### img recv complete
                    client_list[client_host].img_decode()
                    client_list[client_host].package_set(-1)
                #t2 = time.time()
                #print("showtimw= ",t2-t1)

        if not recv_data:
            print('closing connection to', data.addr)
            client_list[client_dict[str(data.addr[1])]].set_visible(False)
            subplot_count.append(client_dict[str(data.addr[1])])
            del client_dict[str(data.addr[1])]
            sel.unregister(sock)
            sock.close()

if __name__ == "__main__":
    try:
        ##### create a figure with subplot 2*5
        subplot_count = [0,1,2,3,4,5,6,7,8,9]
        width = 14
        length = 6
        cv2.namedWindow(window_name,cv2.WINDOW_NORMAL)
        cv2.moveWindow(window_name, 20,20)  # Move it to (40,30)
        #cv2.resizeWindow(window_name, 640, 480)
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
                    ##### concate and plot image
                    #t3 = time.time()
                    img_concate_Hori=np.concatenate((client_list[0].img_read(),client_list[1].img_read(),client_list[2].img_read(),client_list[3].img_read(),client_list[4].img_read()),axis=1)
                    img_concate_Verti=np.concatenate((client_list[5].img_read(),client_list[6].img_read(),client_list[7].img_read(),client_list[8].img_read(),client_list[9].img_read()),axis=1)
                    img_toshow = np.concatenate((img_concate_Hori,img_concate_Verti),axis=0)
                    img_toshow = cv2.resize(img_toshow,(resize_weight,resize_height),interpolation=cv2.INTER_CUBIC)
                    cv2.imshow(window_name,img_toshow)
                    cv2.waitKey(1)
                    #t4 = time.time()
                    #print("showtimw= ",t4-t3)
    finally:
        lsock.close()
        plt.close()
        cv2.destroyAllWindows()
        print("close socket")
