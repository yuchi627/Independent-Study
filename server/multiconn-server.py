import selectors
import socket
import types
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import cv2
import client_struct

host = '192.168.68.106'
port = 6666

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)
    cv2.namedWindow(str(addr))
    client_dict[str(addr)] = client_struct.client()

def recvall(sock,count):
    buf = b''
    while count:
        try:
            newbuf = sock.recv(count)
            print("len",len(newbuf),newbuf)
        except:
            print("recv nothing")
            #if not newbuf: 
            return None
        buf += newbuf
        count -= len(newbuf)
        print("count",count)
    return buf

def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        if(client_dict[str(data.addr)].package_value() == -1):
            recv_data = sock.recv(16)
            package_num = int(recv_data.decode())
            client_dict[str(data.addr)].package_set(package_num)
        else:
            recv_data = sock.recv(1024)
            #recv package and concatenate recv msg to img
            client_dict[str(data.addr)].img_combine(recv_data)
            client_dict[str(data.addr)].package_decrease()
            if(client_dict[str(data.addr)].package_value() == 0):
                img = client_dict[str(data.addr)].img_read()
                client_dict[str(data.addr)].package_set(-1)
                cv2.imwrite("img.jpg",img)
                cv2.imshow(str(data.addr),img)
        '''
        length = sock.recv(16)
        print(length)
        print("decode",length.decode())
        l = int(length.decode())
        stringData = sock.recv(1024)
        print(len(stringData),"stringData: ")
        for i in range(1,l):
            stringData += sock.recv(1024)
            print("stringData",len(stringData))
        #stringData = recvall(sock,int(length.decode()))
        data = np.fromstring(stringData, dtype = 'uint8')
        print("data: ",data)
        #data = np.reshape(data,(640,480))
        cv2.imwrite("data.jpg",data)
        decimg = cv2.imdecode(data,1)
        cv2.imwrite("recv.jpg",decimg)
        print("img:  ",decimg)
        cv2.imshow('client',decimg)
        '''
        #recv_data = sock.recv(1024)  # Should be ready to read
        #if decimg.any:
        #    data.outb = decimg
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            pass
            #print('echoing', data.outb, 'to', data.addr)
            #print(len(data.outb))
            #print('echoing', data.outb.decode(), 'to', data.addr)
            #sent = sock.send(data.outb)  # Should be ready to write
            #data.outb = data.outb[sent:]

try:
    client_dict = {"client":client_struct.client()}
    client_dict["client"].p()
    sel = selectors.DefaultSelector()

    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    lsock.bind((host, port))
    lsock.listen()
    print('listening on', (host, port))
    lsock.setblocking(False)
    sel.register(lsock, selectors.EVENT_READ, data=None)
    cv2.namedWindow('client')
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_wrapper(key.fileobj)
            else:
                service_connection(key, mask)
        cv2.waitKey(1)
finally:
    lsock.close()
    print("close socket")
