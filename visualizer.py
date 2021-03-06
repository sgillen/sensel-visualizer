#!/usr/bin/env python

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



#sgillen: you'll need to install the sensel API to run this program (https://github.com/sensel/sensel-api)
#once you have that installed simply call "python visualizer.py" and follow the prompts
#if you want to mess around with how sensitive the visualizer is change the MAX_FORCE variable defined right after all the imports


#started with the sensel API example 3, modified it to what you see now, this program visualizes and saves the raw force data coming from the sensel device
#there is some code to save the data as a numpy array or .mat file but it is commented out right now as these files tend to be rather large

#imports
#==============================================================================

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
import scipy.io

#define some global variables
#==============================================================================

#MAX_FORCE is a constant you can tweak to change how sensitive the visualizer is.

#MAX_FORCE = 8192 #This is allegedly the maximum allowable force
#MAX_FORCE = 500 # this is the maximum force I've seen in tests, when pushing very very hard
MAX_FORCE = 12.5 # this is what I've found makes the animations look nice


# we store each array we get from the sensel here
force_image_list = []


#sensel functions, ripped from example 3
#==============================================================================
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


#scan frames is what is called during the animation, it pulls data from the sensel,
#puts it into a 2D numpy array, and then updates the animation 
#==============================================================================
def scanFrames(dummy, frame, info):

    global force_image_list
    force_image = np.zeros((info.num_cols, info.num_rows))
    
    error = sensel.readSensor(handle)
    (error, num_frames) = sensel.getNumAvailableFrames(handle)

    #get all the available frames from the device
    for n in range(num_frames):
        error = sensel.getFrame(handle, frame)

        for i in range(info.num_cols):
            for j in range(info.num_rows):
                force_image[i,j] = frame.force_array[j*info.num_cols + i]

        force_image_list.append(np.copy(force_image))
    
        
    #for the most recent frame ONLY, go through and extract the force array into a numpy array
    im.set_array(force_image)
    return [im]


#this is sort of a janky wrapper function that allows us to save our animation to an mp4  
def saveFrames(i):
    im.set_array(force_image_list[i])
    return [im]
    

#main method
#==============================================================================

if __name__ == '__main__':    
    

    #ask for a file name
    file_name = raw_input("Enter a filename to save this session under (for example typing in movie will result in movie.mp4 and movie.csv files)\nleave this blank if you don't want to save anything \n")
    
    
    #open the sensel and make sure that it worked
    handle = openSensel()

    if handle is None:
        print "error opening sensor! exiting!"
    
    (error, info) = sensel.getSensorInfo(handle)
    frame = initFrame()

    #set up the canvas on which we will plot
    fig = plt.figure()
    im = plt.imshow(np.zeros((info.num_cols, info.num_rows)), animated=True, vmin=0, vmax=MAX_FORCE)

    # Set up formatting for the movie files
    Writer = animation.writers['ffmpeg']
    writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)

    
    print "sensel is open and streaming data, x out figure one to quit and save data"

    #launch the animation, this will continue until you x out the figure
    ani = animation.FuncAnimation(fig, scanFrames , fargs = (frame,info), interval=50, blit=True)
    plt.show()

    
    if file_name:
        
        print "saving session, this may take a minute"

        #save the movie file
        ani = animation.FuncAnimation(fig, saveFrames, frames=len(force_image_list), interval=50, blit=True)
        ani.save(file_name + ".mp4" , writer=writer)


        # #this copies our list of force images into a 3d array (so we can save an load it more naturally)
        # force_image_3d = np.array(force_image_list)
        
        # #this will save the output as a numpy array
        # np.save(file_name + ".npy", force_image_3d)

        # #this will save this output as .mat file (for use with matlab)
        # scipy.io.savemat(file_name + ".mat" , mdict={'sensel_data': force_image_3d})
        
    #close up
    closeSensel(frame)
    print "all done, the sensel is closed"    
