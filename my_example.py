#!/usr/bin/env python


#sgillen@20174216-12:42
# my modifications of sensels example 3


##########################################################################
# MIT License
#
# Copyright (c) 2013-2017 Sensel, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons
# to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or
# substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
# PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
# FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
##########################################################################

#Sensel imports
import sys
sys.path.append('../sensel-api/sensel-lib-wrappers/sensel-lib-python')
import sensel
import binascii
import threading
import time

#matplotlib/numpy imports
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

#openCV imports
import cv2


enter_pressed = False

MAX_FORCE = 8192


def waitForEnter():
    global enter_pressed
    raw_input("Press Enter to exit...")
    enter_pressed = True
    return

def openSensel():
    handle = None
    (error, device_list) = sensel.getDeviceList()
    if device_list.num_devices != 0:
        (error, handle) = sensel.openDeviceByID(device_list.devices[0].idx)
    return handle

def initFrame():
    error = sensel.setFrameContent(handle, sensel.FRAME_CONTENT_PRESSURE_MASK)
    (error, frame) = sensel.allocateFrameData(handle)
    error = sensel.startScanning(handle)
    return frame

def scanFrames(frame, info):
    
    error = sensel.readSensor(handle)
    (error, num_frames) = sensel.getNumAvailableFrames(handle)
    for i in range(num_frames):
        error = sensel.getFrame(handle, frame)

    drawFrame(frame,info)
        

def printFrame(frame, info):
    for i in range(info.num_rows):
        print 
        for j in range(info.num_cols):
            print frame.force_array[i*j],


def drawFrame(frame, info):

    Z = np.zeros((info.num_cols, info.num_rows))
    
    for i in range(info.num_cols):
        for j in range(info.num_rows):
            Z[i,j] = frame.force_array[j*info.num_cols + i]
            #Z[i,j] = round(frame.force_array[j*info.num_cols + i]*255/MAX_FORCE)
           
    print np.amax(Z)
    
   # im_color = cv2.applyColorMap(Z, cv2.COLORMAP_HOT)


    im_color = cv2.resize(Z, (0,0), fx=4, fy=4)
    
    cv2.imshow('force image',im_color)
    cv2.waitKey(1)
 
            
    #plt.pause(.01)

    
def closeSensel(frame):
    error = sensel.freeFrameData(handle, frame)
    error = sensel.stopScanning(handle)
    error = sensel.close(handle)

    
handle = openSensel()

if handle is None:
    print "error opening sensor! exiting!"
    
(error, info) = sensel.getSensorInfo(handle)

frame = initFrame()

enter_thread = threading.Thread(target=waitForEnter)
#sensel_thread = threading.Thread(target=scanFrames, args = (frame, info)) #this is going to cause problems

enter_thread.start()
#sensel_thread.start()

while(enter_pressed == False):
    scanFrames(frame, info)

closeSensel(frame)
        


    
