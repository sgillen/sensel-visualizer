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
#from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import matplotlib.animation as animation


#define some global variables

#MAX_FORCE is a constant you can tweak to change how sensitive the visualizer is.

#MAX_FORCE = 8192 #This is allegedly the maximum allowable force
#MAX_FORCE = 500 # this is the maximum force I've seen in tests, when pushing very very hard
MAX_FORCE = 12.5 # this is what I've found makes the animations look nice


force_image_list = []




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

    
def closeSensel(frame):
    error = sensel.freeFrameData(handle, frame)
    error = sensel.stopScanning(handle)
    error = sensel.close(handle)


def scanFrames(dummy, frame, info):

    global force_image_list
    
    error = sensel.readSensor(handle)
    (error, num_frames) = sensel.getNumAvailableFrames(handle)

    #get all the available frames from the device
    for i in range(num_frames):
        error = sensel.getFrame(handle, frame)


    #for the most recent frame ONLY, go through and extract the force array into a numpy array
    for i in range(info.num_cols):
        for j in range(info.num_rows):
            force_image[i,j] = frame.force_array[j*info.num_cols + i]


    force_image_list.append(np.copy(force_image))
    
#    print np.amax(force_image)
    
    im.set_array(force_image)
 
    return [im]


def saveFrames(i):
    im.set_array(force_image_list[i])
    return [im]
    
    


if __name__ == '__main__':    
    
    
    handle = openSensel()

    if handle is None:
        print "error opening sensor! exiting!"
    
    (error, info) = sensel.getSensorInfo(handle)
        
    frame = initFrame()

    fig = plt.figure()
    im = plt.imshow(np.zeros((info.num_cols, info.num_rows)), animated=True, vmin=0, vmax=MAX_FORCE)

    # Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

    
    ani = animation.FuncAnimation(fig, scanFrames , fargs = (frame,info), interval=50, blit=True)

    plt.show()

    ani = animation.FuncAnimation(fig, saveFrames, frames=len(force_image_list), interval=50, blit=True)
    ani.save('im.mp4', writer=writer)
        
    closeSensel(frame)
