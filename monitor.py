import cv2
import numpy as np
import tkinter as tk
import time
import threading

def display_multi(winName, src, row, col):

    root = tk.Tk()
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    disp_img = np.zeros((screen_h,screen_w,3))
    disp_img = disp_img.astype(np.uint8)
    w_offset = int(screen_w / col)
    h_offset = int(screen_h / row)
    w = w_offset
    h = h_offset

    num = len(src)
    t1 = time.time()
    for i in range(num):
        x = int(i%col) * w_offset
        y = int(i/col) * h_offset
        w = src[i].shape[1]
        h = src[i].shape[0]
        if(w_offset > h_offset):
            w = int(h_offset*(w/h))
            h = h_offset
        elif(h_offset > w_offset):
            h = int(w_offset*(h/w))
            w = w_offset

        ROI = cv2.resize(src[i],(w,h))
        disp_img[y:(y+h), x:(x+w),:] = ROI  
    cv2.imshow(winName, disp_img)
    t2 = time.time()
    print(t2-t1)
    cv2.waitKey(1)

    cv2.namedWindow("FullScreen",cv2.WINDOW_NORMAL)
    #cv2.setWindowProperty("FullScreen", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


first = 1
last = 10
while(1):
    src = []
    for i in range(first,last+1):
        img_num = str(i)
        img = cv2.imread("img"+img_num+".jpg")
        src.append(img)
    first+=1
    last+=1
    if(last>60):
        assert threading.current_thread().__class__.__name__ == '_MainThread'
        first = 1
        last = 10
    display_multi("FullScreen",src,2,5)
#cv2.imshow("FullScreen",src)
#cv2.waitKey()
