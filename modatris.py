#--------------------------------------------------------------- gsr tracker ------------------------------------------------------------------------------------

pupil_low_mean = 1
pupil_high_mean = 10

gsr_low_mean = 1
gsr_high_mean = 10

import threading

import sys, struct, serial

import math
import numpy as np
from scipy import signal
from scipy.signal import butter, sosfilt, sosfreqz, medfilt

import matplotlib.pyplot as plt
from scipy.ndimage.filters import uniform_filter1d

from numpy  import array

from datetime import datetime
from datetime import timedelta

def wait_for_ack():
	ddata = ""
	ack = struct.pack('B', 0xff)
	while ddata != ack:
		ddata = ser.read(1)
		#print( "0x%02x" % ord(ddata[0])  )
	  
	return


ser = serial.Serial('Com6', 115200)
ser.flushInput()
print( "port opening, done." )

# send the set sensors command
ser.write(struct.pack('BBBB', 0x08 , 0x04, 0x01, 0x00))  #GSR and PPG

wait_for_ack()	
print( "sensor setting, done." )

# Enable the internal expansion board power
ser.write(struct.pack('BB', 0x5E, 0x01))
wait_for_ack()
print( "enable internal expansion board power, done." )

# send the set sampling rate command
#sampling_freq = 32768 / clock_wait = X Hz
sampling_freq = 30
clock_wait = (2 << 14) / sampling_freq





qqq = struct.pack('<BH', 0x05, int ( clock_wait) )

ser.write(qqq)


ser.write(struct.pack( 'B' , 0x20) )

wait_for_ack()

# send start streaming command
ser.write(struct.pack('B', 0x07))
wait_for_ack()
print( "start command sending, done." )

# read incoming data






ddata = bytearray()


# this is the 1 minute buffer for the gsr data
n_gsr_size    = 30*60
num_array_gsr = [0] * n_gsr_size
norm_array_gsr = [0] * n_gsr_size
num_array_ppg = [0] * n_gsr_size

fused_signal_buffer = [0] * n_gsr_size

def thread_gsr_function():
	print("start gsr")
	
	nnn=5001-1
	nnnn = nnn+1
	
	#num_array =  [0] * nnn
	#num_array2 =  [0] * nnn
	#print(num_array)
	#numrange = range(0,nnn)
	#numrange2 = range(0,nnn)

	#num_to_add = 0
	global num_array_gsr
	global num_array_ppg
	global current_gsr_values
	global ddata
	
	
	
	
	
	exetime = datetime.now()
		
	while True:
		
		dt = datetime.now() - exetime
		ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0

		exeevery = 33.3333 # ms

	
	
	
	
	
	
	
	
		numbytes = 0
		framesize = 8 # 1byte packet type + 3byte timestamp + 2 byte GSR + 2 byte PPG(Int A13)
		#print( "Packet Type\tTimestamp\tGSR\tPPG" )
	
		while numbytes < framesize:
			ddata += ser.read(framesize)
			numbytes = len(ddata)
			
		
		data = ddata[0:framesize]
		ddata = ddata[framesize:]
		numbytes = len(ddata)

		# read basic packet information
		(packettype) = struct.unpack('B', data[0:1])
		(timestamp0, timestamp1, timestamp2) = struct.unpack('BBB', data[1:4])

		# read packet payload
		(PPG_raw, GSR_raw) = struct.unpack('HH', data[4:framesize])

		# get current GSR range resistor value
		Range = ((GSR_raw >> 14) & 0xff)  # upper two bits
		if(Range == 0):
			Rf = 40.2	# kohm
		elif(Range == 1):
			Rf = 287.0  # kohm
		elif(Range == 2):
			Rf = 1000.0 # kohm
		elif(Range == 3):
			Rf = 3300.0 # kohm

		# convert GSR to kohm value
		gsr_to_volts = (GSR_raw & 0x3fff) * (3.0/4095.0)
		GSR_ohm = Rf/( (gsr_to_volts /0.5) - 1.0)

		# convert PPG to milliVolt value
		PPG_mv = PPG_raw * (3000.0/4095.0)

		timestamp = timestamp0 + timestamp1*256 + timestamp2*65536

		#num_array.pop(0)
		#num_array2.pop(0)
		
		#print("O: ", GSR_ohm)
		#print("L: ", num_array[ len(num_array)-2 ])
		
		#xxx =  GSR_ohm  
		#yyy =  num_array[ len(num_array)-2 ]
		
		#num_array2.insert(len(num_array2), GSR_ohm)
		
		#if abs ( xxx - yyy )  > 500 :
		#	#print("big")
		#	#GSR_ohm = num_array[ len(num_array)-2 ]
		#	num_array.insert(len(num_array), GSR_ohm)
		#else:
		#	num_array.insert(len(num_array), GSR_ohm)
		
		# if it is time to save data save data to array
		if ms > exeevery:
			#print(ms)
			exetime = datetime.now()
			
			num_array_gsr.pop(0)
			num_array_gsr.insert(len(num_array_gsr), GSR_ohm)
			
			num_array_ppg.pop(0)
			num_array_ppg.insert(len(num_array_ppg), PPG_mv)
			
			gsr_arrayt = np.array(num_array_gsr[1500:1799])
			gsr_qqqt = np.median(gsr_arrayt)
			gsr_normt = (gsr_qqqt - gsr_low_mean)/(gsr_high_mean - gsr_low_mean)
			
			norm_array_gsr.pop(0)
			norm_array_gsr.insert(len(norm_array_gsr), gsr_normt)	

			
			
		#N = 5000
		#anp = array( num_array )
		#moving_ave = uniform_filter1d(anp, size=N)
		#moving_ave_v = moving_ave / np.sqrt(np.sum(moving_ave**2))
		
		#print(np.mean(moving_ave), "  :  " ,moving_ave[len(num_array)-1])
	

		current_gsr_values[0] = 0#np.mean(moving_ave)
		current_gsr_values[1] = 0#moving_ave[len(num_array)-1]
		current_gsr_values[2] = 0
		current_gsr_values[3] = 0






current_gsr_values = [1, 2, 3, 4]
thread_gsr_tracker = threading.Thread(target=thread_gsr_function, args=(), daemon=True) # 

thread_gsr_tracker.start()









#------------------------------------------------------ eye tracker start --------------------------------------------------------------------------


#imports for the eye tracker 
import tobii_research as tr
from pygaze.display import Display
from pygaze.eyetracker import EyeTracker
from pygaze import settings; settings.TRACKERSERIALNUMBER = 'X230C-030127221071'
from pygaze import settings; settings.FULLSCREEN = False
from pygaze import settings; settings.DISPSIZE = (1920,1080)
#from pygaze import settings; settings.DISPTYPE = 'pygame' # this did not work in my case but it might be easier for the pygame application
#from pygaze import settings; settings.DISPTYPE = 'pygame'

import numpy as np
import pandas as pd
import logging
import time


def getPupilSize(self):
    
    # check to see if the eyetracker is connected and turned on
    if self.eyetracker is None:
        raise ValueError("There is no eyetracker.")
    if self.tracking is False:
        raise ValueError("The eyetracker is not turned on.")
        
    # while tracking
    while True:
        lPup = self.gazeData['left_pupil_diameter']
        rPup = self.gazeData['right_pupil_diameter']
        pupSizes = (lPup, rPup)
        
        # if pupils were found
        if lPup != -1 and rPup != -1:
            avgPupSize = np.nanmean(pupSizes)
        else: # otherwise return zero
            avgPupSize = (0.0)
            
        # return pupil size
        return avgPupSize



def calibrateEyeTrackerPyGaze():
    """
        Runs the callibration process using PyGaze and tobii eye trackers.
    """

    disp = Display()
    tracker = EyeTracker(disp,resolution=(1920,1080),  trackertype='tobii')
	
    #print(tracker.BINOCULAR)
    #tracker.set_eye_used(2) #both eyes
    # we hotfixed the lib to use both eyes as above does not work 
	
    tracker.calibrate()
    
    #tracker.close() 
    disp.close()
    return tracker

def avaliableEyeTrackers():
    """
        Checks for the available eye trackers connected using tobii SDK
    """
    # <BeginExample>
    eyetrackers = tr.find_all_eyetrackers()

    for eyetracker in eyetrackers:
        print("Address: " + eyetracker.address)
        print("Model: " + eyetracker.model)
        print("Name (It's OK if this is empty): " + eyetracker.device_name)
        print("Serial number: " + eyetracker.serial_number)
        #TRACKERSERIALNUMBER = eyetracker.serial_number
    # <EndExample>
    return eyetrackers
	
def shift1(arr,num = 1):
    """
    Shifts the array by 1 converting array to panda, shifting and converting to list. 
    """
    data = pd.Series(arr)
    data = data.shift(num)
    return data.tolist()

def updateRollingArray(arr,new_value):
    """
    Shifts the array and puts the new value in the first index's place
    """
    shifted_arr = shift1(arr)
    shifted_arr[0] = new_value
    return shifted_arr

from scipy.spatial import distance
#print(avaliableEyeTrackers())

eyetracker = calibrateEyeTrackerPyGaze()
eyetracker.start_recording()    
gaze_array = range(1,30)
current_tracker_sample = eyetracker.sample()


#current_gaze_mean = np.mean(gaze_array,axis=0)
#eyetracker.stop_recording()
#eyetracker.close()





# this is the 1 minute buffer for the pupil data
n_pupil_size    = 30*60
num_array_pupil = [0] * n_pupil_size
norm_array_pupil = [0] * n_pupil_size
num_array_x =  [0] * n_pupil_size
num_array_y =  [0] * n_pupil_size



def thread_tracker_function():
	
	#global current_tracker_sample
	
	global current_eye_values
	global num_array_pupil
	global num_array_x
	global num_array_y

	exetime_tracker = datetime.now()
	
	
		
	while True:
		
		dt = datetime.now() - exetime_tracker
		ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
		
		
		exeevery = 33.3333 # ms
		
		#while True:
		#print ( time.sleep( exeevery - ((time.time() - starttime) % exeevery)) ) 
		
		if ms > exeevery:
			#print(ms)
			exetime_tracker = datetime.now()
			
			#print("Eye" + str( datetime.now() ) )
			

			
			
			
			# get the current pupil value



			
			
			current_eyetracker_pupilval = eyetracker.pupil_size()
			
			# save the pupil value in num_array_pupil
			num_array_pupil.pop(0)
			num_array_pupil.insert(len( num_array_pupil ), current_eyetracker_pupilval )
			
			pupil_arrayt = np.array(num_array_pupil[1769:1799])
			pupil_qqqt = np.median(pupil_arrayt)
			#print("median pupil: " + str(pupil_qqqt))
			pupil_normt = (pupil_qqqt - pupil_low_mean)/(pupil_high_mean - pupil_low_mean)
			norm_array_pupil.pop(0)
			norm_array_pupil.insert(len( norm_array_pupil ), pupil_normt )			
			
			
			
			
			# get the current x and y 
			current_tracker_sample = eyetracker.sample()
			#current_tracker_sample[0] x
			#current_tracker_sample[1] y

			num_array_x.pop(0)
			num_array_x.insert(len( num_array_x ), current_tracker_sample[0])
			
			num_array_y.pop(0)
			num_array_y.insert(len( num_array_y ), current_tracker_sample[1])
			
			
			"""

			
			anp1 = array( num_array_x )
			
			anp2 = array( num_array_y )
			
			moving_ave1 = uniform_filter1d(anp1, size=N)
			moving_ave2 = uniform_filter1d(anp2, size=N) 

			num_array_x_new.insert(len( num_array_x_new ), current_tracker_sample[0])
			num_array_y_new.insert(len( num_array_y_new ), current_tracker_sample[1])
			anp1_new = array( num_array_x_new )
			anp2_new = array( num_array_y_new )
			moving_ave1_new = uniform_filter1d(anp1_new, size=50)
			moving_ave2_new = uniform_filter1d(anp2_new, size=50)

			distx = np.linalg.norm(np.mean(moving_ave1)-np.mean(moving_ave1_new))
			disty = np.linalg.norm(np.mean(moving_ave2)-np.mean(moving_ave2_new))		
			

			
			p1 = (np.mean(moving_ave1), np.mean(moving_ave2))
			p2 = (np.mean(moving_ave1_new), np.mean(moving_ave2_new))
			ddddd = distance.euclidean(p1, p2)
			"""
		
			
			#print('current gaze is at: ',current_tracker_sample) #tuple(x,y)
			#print('current gaze is at: ',current_tracker_sample) #tuple(x,y)
			
			
			
			
			
			
			current_eye_values[0] = current_tracker_sample[0] #np.mean(moving_ave1)
			current_eye_values[1] = current_tracker_sample[1] #np.mean(moving_ave2)
			current_eye_values[2] = 0 #ddddd
			current_eye_values[3] = current_eyetracker_pupilval # this is the current value used
			
			#print(current_eye_values[3])
			#Sleep(100)
			
			#print('xxx: ',current_eye_values[0]) #tuple(x,y)
			#print('yyy: ',current_eye_values[1]) #tuple(x,y)
			
			#gaze_array = updateRollingArray(gaze_array,current_tracker_sample)
		
			
			#





current_eye_values = [1, 2, 3, 4]
thread_eyetracker = threading.Thread(target=thread_tracker_function, args=()) # , daemon=True

thread_eyetracker.start()



measurement = 9


#thread_eyetracker.




#while True:
	#print("var1: ", current_eye_values[0]," var2: ", current_eye_values[1])
	#Sleep(1000)
	#pass




















# ---------------------------------------------------- Tetris start ---------------------------------------------------------------
# Control keys:
# Down - Drop stone faster
# Left/Right - Move stone
# Up - Rotate Stone clockwise
# Escape - Quit game
# P - Pause game

from random import randrange as rand
import pygame, sys



# The configuration
config = {
	'cell_size': 20,
	'cols':		 10,
	'rows':		20,
	'delay':	50,
	'maxfps':	30
}

colors = [
	(142, 214, 159),
	(15, 91, 130),
	(142, 159, 214),
	(0,   0,   255),
	(255, 120, 0  ),
	(255, 255, 0  ),
	(180, 0,   255),
	(0,   220, 220)
	]

# Define the shapes of the single parts

advanced = [
	[[2, 0, 0],
	 [2, 2, 0],
	 [2, 2, 2]],

	[[0, 0, 2],
	 [0, 2, 0],
	 [2, 0, 0]],

	[[2, 0, 2],
	 [0, 2, 0]],

	[[0, 2, 0],
	 [2, 2, 2],
	 [0, 2, 0]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

normal = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],
 
	[[1, 1],
	 [1, 1]],
 
	[[1, 1, 0],
	 [1, 1, 1]]
	 ]

level1 = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],
 
	[[1, 1],
	 [1, 1]],
 
	[[1, 1, 0],
	 [1, 1, 1]],
 
	[[1, 1]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level2 = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],
 
	[[1, 1],
	 [1, 1]],
 
	[[1, 1, 0],
	 [1, 1, 1]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level3 =  [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],
 
	[[1, 1],
	 [1, 1]],

	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level4 =  [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[1, 1, 1, 1]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level5 =  [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],
 
	[[0, 0, 1],
	 [1, 1, 1]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level6 =  [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],
 
	[[1, 0, 0],
	 [1, 1, 1]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level7 = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],
 
	[[1, 1, 0],
	 [0, 1, 1]],

	[[0, 2, 0],
	 [2, 2, 2],
	 [0, 2, 0]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level8 =[
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 1, 1],
	 [1, 1, 0]],

	[[2, 0, 2],
	 [0, 2, 0]],

	[[0, 2, 0],
	 [2, 2, 2],
	 [0, 2, 0]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]

level9 = [
	[[1, 1, 1],
	 [0, 1, 0]],

	[[0, 0, 2],
	 [0, 2, 0],
	 [2, 0, 0]],

	[[2, 0, 2],
	 [0, 2, 0]],

	[[0, 2, 0],
	 [2, 2, 2],
	 [0, 2, 0]],

	[[0, 2, 2],
	 [2, 2, 0]],

	[[2, 2, 0],
	 [0, 2, 2]],

	[[2, 0, 2],
	 [0, 2, 0],
	 [2, 0, 2]],
	
	[[2, 2, 2],
	 [2, 2, 2],
	 [2, 2, 2]],

	[[2, 0, 2],
	 [0, 0, 0],
	 [2, 0, 2]],

	[[2, 0, 0, 0],
	 [2, 2, 0, 0],
	 [2, 2, 2, 0],
	 [2, 2, 2, 2]]]


last_diff_gsr = current_gsr_values[1] - current_gsr_values[0]
last_gaze_var = current_eye_values[2]
#measurement = 0 # measurements from sensor - plug in own data
#print(measurement)

def rotate_clockwise(shape):
	return [[shape[y][x] for y in range(len(shape))]
		for x in range(len(shape[0]) - 1, -1, -1)]

def check_collision(board, shape, offset):
	off_x, off_y = offset
	for cy, row in enumerate(shape):
		for cx, cell in enumerate(row):
			try:
				if cell and board[ cy + off_y ][ cx + off_x ]:
					return True
			except IndexError:
				return True
	return False

def remove_row(board, row):
	del board[row]
	return [[0 for i in range(config['cols'])]] + board
	
def join_matrixes(mat1, mat2, mat2_off):
	off_x, off_y = mat2_off
	for cy, row in enumerate(mat2):
		for cx, val in enumerate(row):
			mat1[cy+off_y-1	][cx+off_x] += val
	return mat1

def new_board():
	board = [[0 for x in range(config['cols'])] for y in range(config['rows']) ]
	board += [[ 1 for x in range(config['cols'])]]
	return board

class TetrisApp(object):




	def __init__(self):
		pygame.init()
		pygame.key.set_repeat(250,25)
		self.width = config['cell_size']*config['cols']
		self.height = config['cell_size']*config['rows']
		self.screen = pygame.display.set_mode((self.width, self.height))
		pygame.event.set_blocked(pygame.MOUSEMOTION)
		self.init_game()
	
	def new_stone(self):
		# make sure to update the if statements according to 
		# the readings from the sensors
		
		#print("gazex: ", current_eye_values[0]," gazey: ", current_eye_values[1],"gazex: ", current_eye_values[0]," gazey: ", current_eye_values[1])
		
		#print("meangsr: ", current_gsr_values[0]," currentgsr: ", current_gsr_values[1])
		
		#print("gaze", current_eye_values[2])
		global measurement
		global last_diff_gsr
		global last_gaze_var
		
		# get the current values from the 2 threads
		#curr_diff_gsr = current_gsr_values[1] - current_gsr_values[0]
		#curr_gaze_var = current_eye_values[3]
		
		# measurement = difficulty level 

		# if the user was more stressed on eye and gsr reduce by 1
		#if curr_diff_gsr > last_diff_gsr and curr_gaze_var > last_gaze_var:
		#	if measurement != 1:
		#		measurement = measurement -1
		
		#if user was calm on eye and gsr increase by 1 
		#if curr_diff_gsr < last_diff_gsr or curr_gaze_var < last_gaze_var:
		#	if measurement != 0 and measurement < 9:
		#		measurement = measurement +1
		
		#print(measurement,curr_diff_gsr,last_diff_gsr,curr_gaze_var,last_gaze_var)
		#print(config)
		
		
		
		#last_diff_gsr = current_gsr_values[1] - current_gsr_values[0]
		#last_gaze_var = current_eye_values[3]
		
		self.drop_amount = 0
		self.stone_y = 0
		
		valuezzz = 50 


		
		
		self.stone = normal[rand(len(normal))]
		
		self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
		
		
		if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.board = new_board()
		self.new_stone()
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  pygame.font.Font(pygame.font.get_default_font(), 12).render(line, False, (255,255,255), (142, 214, 159))
			msgim_center_x, msgim_center_y = msg_image.get_size()
			msgim_center_x //= 2
			msgim_center_y //= 2
			self.screen.blit(msg_image, (self.width // 2-msgim_center_x, self.height // 2-msgim_center_y+i*22))
	
	def draw_matrix(self, matrix, offset):
		off_x, off_y  = offset
		for y, row in enumerate(matrix):
			for x, val in enumerate(row):
				if val:
					pygame.draw.rect(self.screen, colors[val], pygame.Rect((off_x+x) * config['cell_size'], (off_y+y) * config['cell_size'],  config['cell_size'], config['cell_size']),0)
	
	def move(self, delta_x):
		if not self.gameover and not self.paused:
			new_x = self.stone_x + delta_x
			if new_x < 0:
				new_x = 0
			if new_x > config['cols'] - len(self.stone[0]):
				new_x = config['cols'] - len(self.stone[0])
			if not check_collision(self.board, self.stone, (new_x, self.stone_y)):
				self.stone_x = new_x
	def quit(self):
		self.center_msg("Exiting...")
		pygame.display.update()
		sys.exit()
	
	def drop(self):
		if not self.gameover and not self.paused:
			self.stone_y += 1
			if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
				self.board = join_matrixes(self.board, self.stone, (self.stone_x, self.stone_y))
				self.new_stone()
				while True:
					for i, row in enumerate(self.board[:-1]):
						if 0 not in row:
							self.board = remove_row(self.board, i)
							break
					else:
						break
	
	def rotate_stone(self):
		if not self.gameover and not self.paused:
			new_stone = rotate_clockwise(self.stone)
			if not check_collision(self.board, new_stone, (self.stone_x, self.stone_y)):
				self.stone = new_stone
	
	def toggle_pause(self):
		self.paused = not self.paused
	
	def start_game(self):
		if self.gameover:
			self.init_game()
			self.gameover = False
	
	
	

	def butter_bandpass(lowcut, highcut, fs, order=5):
			
			
			nyq = 0.5 * fs
			low = lowcut / nyq
			high = highcut / nyq
			sos = butter(order, [low, high], analog=False, btype='band', output='sos')
			y = sosfilt(sos, data)
			
			return sos

	def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
			sos = butter_bandpass(lowcut, highcut, fs, order=order)
			y = sosfilt(sos, data)
			return y	
	
	def run(self):
		key_actions = {
			'ESCAPE':	self.quit,
			'LEFT':		lambda:self.move(-1),
			'RIGHT':	lambda:self.move(+1),
			'DOWN':		self.drop,
			'UP':		self.rotate_stone,
			'p':		self.toggle_pause,
			'SPACE':	self.start_game
		}
		
		self.gameover = False
		self.paused = False
		
		config['delay'] = 50*10
		pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
		dont_burn_my_cpu = pygame.time.Clock()
		





		
		print("relax 60 sec")
		#this is the relax for 60 sec loop
		breakss = True
		exestart = datetime.now()
		while breakss:
			
			dt = datetime.now() - exestart
			ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
			#print( "breaking" + str(ms) )
			
			self.screen.fill((36, 115, 54))
			pygame.display.update()
			dont_burn_my_cpu.tick(config['maxfps'])
			
			
			exeevery = 60000
			
			if ms > exeevery:
				breakss = False
					
				dt = 0.03333333333333333333333333333333333333333333
				t = np.arange(0, 60, dt)
					
				s1_ = np.array(num_array_pupil)
				s2_ = np.array(num_array_x)
				s3_ = np.array(num_array_y)

				s4_ = np.array(num_array_gsr)
				s5_ = np.array(num_array_ppg)					
				
				#s4 = signal.filtfilt(b, a, s4)
				s4 = medfilt(s4_,301)
				s1 = medfilt(s1_,31)
				
				pupil_low_mean = np.min( s1 )
				gsr_low_mean = np.min( s4 )
				print( "pupil low  min : " + str( pupil_low_mean ) )
				print( "gsr   low  min : " + str( gsr_low_mean ) )
				
				"""
				# Plot the frequency response for a few different orders.
				plt.figure(0)
				fig, axs = plt.subplots(4, 1)
				axs[0].plot(t, s1_)
				axs[0].set_xlim(0, 60)
				axs[0].set_xlabel('time')
				axs[0].set_ylabel('s1')
				axs[0].grid(True)

				axs[1].plot( t, s2_)
				axs[1].set_xlim(0, 60)
				axs[1].set_xlabel('time')
				axs[1].set_ylabel('s2')
				axs[1].grid(True)

				axs[2].plot( t, s3_)
				axs[2].set_xlim(0, 60)
				axs[2].set_xlabel('time')
				axs[2].set_ylabel('s3')
				axs[2].grid(True)

				axs[3].plot( t, s4_)
				axs[3].set_xlim(0, 60)
				axs[3].set_xlabel('time')
				axs[3].set_ylabel('s4')
				axs[3].grid(True)

				fig.tight_layout()

				plt.figure(1)
				fig, axs = plt.subplots(4, 1)
				axs[0].plot(t, s1)
				axs[0].set_xlim(0, 60)
				axs[0].set_xlabel('time')
				axs[0].set_ylabel('s1')
				axs[0].grid(True)

				axs[1].plot( t, s2_)
				axs[1].set_xlim(0, 60)
				axs[1].set_xlabel('time')
				axs[1].set_ylabel('s2')
				axs[1].grid(True)

				axs[2].plot( t, s3_)
				axs[2].set_xlim(0, 60)
				axs[2].set_xlabel('time')
				axs[2].set_ylabel('s3')
				axs[2].grid(True)

				axs[3].plot( t, s4)
				axs[3].set_xlim(0, 60)
				axs[3].set_xlabel('time')
				axs[3].set_ylabel('s4')
				axs[3].grid(True)

				fig.tight_layout()
				
				plt.show()
				"""
		
		

		
		config['delay'] = 40*1
		pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
		dont_burn_my_cpu = pygame.time.Clock()
		
		
		print("stress 60 sec")
		#this is the fast tetris play for 10 sec loop
		wait_here = True 
		exestart = datetime.now()
		while wait_here:
			
			dt = datetime.now() - exestart
			ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
			
			
			exeevery = 60000 # 60 sec
			
			
			if ms > exeevery:
				wait_here = False
				
				dt = 0.03333333333333333333333333333333333333333333
				t = np.arange(0, 60, dt)
					
				s1_ = np.array(num_array_pupil)
				s2_ = np.array(num_array_x)
				s3_ = np.array(num_array_y)

				s4_ = np.array(num_array_gsr)
				s5_ = np.array(num_array_ppg)					
				
				#s4 = signal.filtfilt(b, a, s4)
				s4 = medfilt(s4_,301)
				s1 = medfilt(s1_,31)
				
				pupil_high_mean = np.max( s1 )
				gsr_high_mean = np.max( s4 )
				print( "pupil low  max : " + str( pupil_high_mean ) )
				print( "gsr   low  max : " + str( gsr_high_mean ) )

		
			self.screen.fill((36, 115, 54))
			if self.gameover:
				self.center_msg("""Game Over! Press space to continue""")

			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
			pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.drop()
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_" +key):
							key_actions[key]()
					
			dont_burn_my_cpu.tick(config['maxfps'])
		
		
		
		
		
		norm_array_pupil = [0] * n_pupil_size
		norm_array_gsr = [0] * n_gsr_size
		
		
		
		
		config['delay'] = 50*4
		pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
		dont_burn_my_cpu = pygame.time.Clock()		
		self.board = new_board()
		self.new_stone()
		
		
		
		print("game 60 sec")
		# this is the test loop
		plotted = 0
		exestart = datetime.now()
		while True:
			
			
			

			
			gsr_array = np.array(num_array_gsr[1500:1799])
			gsr_qqq = np.median(gsr_array)
			gsr_norm = (gsr_qqq - gsr_low_mean)/(gsr_high_mean - gsr_low_mean)
			
			if gsr_norm < 0:
				gsr_norm = 0
			if gsr_norm > 1:
				gsr_norm = 1
			
			print("gsr_low_mean: " + str(gsr_low_mean))
			print("gsr_high_mean: " + str(gsr_high_mean))
			print("gsr_qqq: " + str(gsr_qqq))
			print("gsr_norm: " + str(gsr_norm))
			
			pupil_array = np.array(num_array_pupil[1769:1799])
			pupil_qqq = np.median(pupil_array)
			pupil_norm = (pupil_qqq - pupil_low_mean)/(pupil_high_mean - pupil_low_mean)
			if pupil_norm < 0:
				pupil_norm = 0
			if pupil_norm > 1:
				pupil_norm = 1
			
			print("pupil_low_mean: " + str(pupil_low_mean))
			print("pupil_high_mean: " + str(pupil_high_mean))
			print("pupil_qqq: " + str(pupil_qqq))
			print("pupil_norm: " + str(pupil_norm))
			

			
			fused_value = gsr_norm*0.1 + pupil_norm*0.9
			
			print("fused value: " + str(fused_value))
			
			
			valuezzz = 50

			# change the speed of the game based uppon the fused value 
			if    fused_value < 0.0 :			
				print("0.0--")
				config['delay'] = valuezzz*10
			elif  fused_value > 0 and fused_value < 0.1 :			
				print("0.1")
				config['delay'] = valuezzz*10
			elif  fused_value > 0.1 and fused_value < 0.2 :
				print("0.2")
				config['delay'] = valuezzz*9
			elif  fused_value > 0.2 and fused_value < 0.3 :
				print("0.3")
				config['delay'] = valuezzz*8
			elif  fused_value > 0.3 and fused_value < 0.4 :
				print("0.4")
				config['delay'] = valuezzz*7
			elif  fused_value > 0.4 and fused_value < 0.5 :
				print("0.5")
				config['delay'] = valuezzz*6
			elif  fused_value > 0.5 and fused_value < 0.6 :
				print("0.6")
				config['delay'] = valuezzz*5
			elif  fused_value > 0.6 and fused_value < 0.7 :
				print("0.7")
				config['delay'] = valuezzz*4
			elif  fused_value > 0.7 and fused_value < 0.8 :
				print("0.8")
				config['delay'] = valuezzz*3
			elif  fused_value > 0.8 and fused_value < 0.9 :
				print("0.9")
				config['delay'] = valuezzz*2
			elif  fused_value > 0.9 and fused_value < 1.0 :
				print("1.0")
				config['delay'] = valuezzz*1
			elif  fused_value > 1.0 :
				print("1.0++")
				config['delay'] = valuezzz*1
			else:

				print ("Please")
			
			
			
			
			
			
			
			
			
			
			#measurement = 4
			
			pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
			
			dt = datetime.now() - exestart
			ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
			
			
			exeevery = 60000 # 60 sec + 5sec so the buffer is for sure not empty in nay spots
			
			
			if ms > exeevery:
		
				if plotted == 0:
				
					plotted = 1
				
					print("print all the matplotlib stuff")
				
				
					dt = 0.03333333333333333333333333333333333333333333
					t = np.arange(0, 60, dt)

					s1 = np.array(num_array_pupil)
					s2 = np.array(num_array_x)
					s3 = np.array(num_array_y)

					s4 = np.array(num_array_gsr)
					s5 = np.array(num_array_ppg)

					print("length:"  + str(len(s5)) )
					plt.figure(0)
					fig, axs = plt.subplots(4, 1)
					axs[0].plot(t, s1)
					axs[0].set_xlim(0, 60)
					axs[0].set_xlabel('time')
					axs[0].set_ylabel('s1')
					axs[0].grid(True)

					axs[1].plot( t, s2)
					axs[1].set_xlim(0, 60)
					axs[1].set_xlabel('time')
					axs[1].set_ylabel('s2')
					axs[1].grid(True)

					axs[2].plot( t, s3)
					axs[2].set_xlim(0, 60)
					axs[2].set_xlabel('time')
					axs[2].set_ylabel('s3')
					axs[2].grid(True)

					axs[3].plot( t, s4)
					axs[3].set_xlim(0, 60)
					axs[3].set_xlabel('time')
					axs[3].set_ylabel('s4')
					axs[3].grid(True)

					#axs[4].plot( t, s5)
					#axs[4].set_xlim(0, 60)
					#axs[4].set_xlabel('time')
					#axs[4].set_ylabel('s5')
					#axs[4].grid(True)
					
					fig.tight_layout()
					#plt.show()
					
					
					plt.figure(1)
					fig, axs = plt.subplots(12, 1)
					
					cxy, f = axs[0].cohere(s1, s2, 900, 15)
					axs[0].set_ylabel('s1 s2 co')
					cxy, f = axs[1].cohere(s1, s3, 900, 15)
					axs[1].set_ylabel('s1 s3 co')
					cxy, f = axs[2].cohere(s1, s4, 900, 15)
					axs[2].set_ylabel('s1 s4 co')
					#cxy, f = axs[3].cohere(s1, s5, 900, 15)
					#axs[3].set_ylabel('s1 s5 co')

					cxy, f = axs[3].cohere(s2, s1, 900, 15)
					axs[3].set_ylabel('s2 s1 co')
					cxy, f = axs[4].cohere(s2, s3, 900, 15)
					axs[4].set_ylabel('s2 s3 co')
					cxy, f = axs[5].cohere(s2, s4, 900, 15)
					axs[5].set_ylabel('s2 s4 co')
					#cxy, f = axs[7].cohere(s2, s5, 900, 15)
					#axs[7].set_ylabel('s2 s5 co')

					cxy, f = axs[6].cohere(s3, s1, 900, 15)
					axs[6].set_ylabel('s3 s1 co')
					cxy, f = axs[7].cohere(s3, s2, 900, 15)
					axs[7].set_ylabel('s3 s2 co')
					cxy, f = axs[8].cohere(s3, s4, 900, 15)
					axs[8].set_ylabel('s3 s4 co')
					#cxy, f = axs[11].cohere(s3, s5, 900, 15)
					#axs[11].set_ylabel('s3 s5 co')

					cxy, f = axs[9].cohere(s4, s1, 900, 15)
					axs[9].set_ylabel('s4 s1 co')
					cxy, f = axs[10].cohere(s4, s2, 900, 15)
					axs[10].set_ylabel('s4 s2 co')
					cxy, f = axs[11].cohere(s4, s3, 900, 15)
					axs[11].set_ylabel('s4 s3 co')
					#cxy, f = axs[15].cohere(s4, s5, 900, 15)
					#axs[15].set_ylabel('s4 s5 co')
					
					#cxy, f = axs[16].cohere(s5, s1, 900, 15)
					#axs[16].set_ylabel('s5 s1 co')
					#cxy, f = axs[17].cohere(s5, s2, 900, 15)
					#axs[17].set_ylabel('s5 s2 co')
					#cxy, f = axs[18].cohere(s5, s3, 900, 15)
					#axs[18].set_ylabel('s5 s3 co')
					#cxy, f = axs[19].cohere(s5, s3, 900, 15)
					#axs[19].set_ylabel('s5 s4 co')

					fig.tight_layout()
					
					
					


					# Sample rate and desired cutoff frequencies (in Hz).
					fs = 30.0# Sampling frequency
					lowcut = 50.0
					highcut = 110.0
					nyq = 0.5 * fs
					low = lowcut / nyq
					high = highcut / nyq
					order = 5
					
					#s1 = sosfilt(butter(order, [low, high], analog=False, btype='band', output='sos'), s1)
					#s2 = sosfilt(butter(order, [low, high], analog=False, btype='band', output='sos'), s2)
					#s3 = sosfilt(butter(order, [low, high], analog=False, btype='band', output='sos'), s3)
					#s4 = sosfilt(butter(order, [low, high], analog=False, btype='band', output='sos'), s4)
					#s5 = sosfilt(butter(order, [low, high], analog=False, btype='band', output='sos'), s5)
					
					order = 5
					fs = 30.0# Sampling frequency
					fc = 5  # Cut-off frequency of the filter
					w = fc / (fs / 2) # Normalize the frequency
					b, a = signal.butter(order, w, 'low')
					
					#s1 = signal.filtfilt(b, a, s1)
					#s2 = signal.filtfilt(b, a, s2)
					#s3 = signal.filtfilt(b, a, s3)
					
					
					s5 = signal.filtfilt(b, a, s5)
						

					order = 5
					fs = 30.0# Sampling frequency
					fc = 1  # Cut-off frequency of the filter
					w = fc / (fs / 2) # Normalize the frequency
					b, a = signal.butter(order, w, 'low')
					
					
					
					
					#s4 = signal.filtfilt(b, a, s4)
					
					

					# Plot the frequency response for a few different orders.
					plt.figure(2)
					fig, axs = plt.subplots(6, 1)
					axs[0].plot(t, s1)
					axs[0].set_xlim(0, 60)
					axs[0].set_xlabel('time')
					axs[0].set_ylabel('Raw pupil')
					axs[0].grid(True)
					
					s1_30 = medfilt(s1,31)

					axs[1].plot( t, s1_30)
					axs[1].set_xlim(0, 60)
					axs[1].set_xlabel('time')
					axs[1].set_ylabel('Filtered 30 pupil')
					axs[1].grid(True)
					
					s1_300 = medfilt(s1,301)

					axs[2].plot( t, s1_300)
					axs[2].set_xlim(0, 60)
					axs[2].set_xlabel('time')
					axs[2].set_ylabel('Filtered 300 pupil')
					axs[2].grid(True)					
					

					axs[3].plot(t, s4)
					axs[3].set_xlim(0, 60)
					axs[3].set_xlabel('time')
					axs[3].set_ylabel('Raw GSR')
					axs[3].grid(True)
					
					s4_30 = medfilt(s4,31)

					axs[4].plot( t, s4_30)
					axs[4].set_xlim(0, 60)
					axs[4].set_xlabel('time')
					axs[4].set_ylabel('Filtered 30 GSR')
					axs[4].grid(True)
					
					s4_300 = medfilt(s4,301)

					axs[5].plot( t, s4_300)
					axs[5].set_xlim(0, 60)
					axs[5].set_xlabel('time')
					axs[5].set_ylabel('Filtered 300 GSR')
					axs[5].grid(True)

					
					fig.tight_layout()
					
					
					
					
					plt.show()
		
			self.screen.fill((36, 115, 54))
			if self.gameover:
				self.center_msg("""Game Over! Press space to continue""")

			else:
				if self.paused:
					self.center_msg("Paused")
				else:
					self.draw_matrix(self.board, (0,0))
					self.draw_matrix(self.stone, (self.stone_x, self.stone_y))
			pygame.display.update()
			
			for event in pygame.event.get():
				if event.type == pygame.USEREVENT+1:
					self.drop()
				elif event.type == pygame.QUIT:
					self.quit()
				elif event.type == pygame.KEYDOWN:
					for key in key_actions:
						if event.key == eval("pygame.K_" +key):
							key_actions[key]()
					
			dont_burn_my_cpu.tick(config['maxfps'])

if __name__ == '__main__':
	App = TetrisApp()
	App.run()
