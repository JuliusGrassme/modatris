#--------------------------------------------------------------- gsr tracker ------------------------------------------------------------------------------------


import threading

import sys, struct, serial

import math
import numpy as np


import matplotlib.pyplot as plt
from scipy.ndimage.filters import uniform_filter1d

from numpy  import array






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
sampling_freq = 50
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

def thread_gsr_function():
	print("start gsr")
	
	nnn=5001-1
	nnnn = nnn+1
	
	num_array =  [0] * nnn
	num_array2 =  [0] * nnn
	#print(num_array)
	numrange = range(0,nnn)
	numrange2 = range(0,nnn)

	num_to_add = 0
	
	global my_var2
	global ddata
	
	while True:
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

		num_array.pop(0)
		num_array2.pop(0)
		
		#print("O: ", GSR_ohm)
		#print("L: ", num_array[ len(num_array)-2 ])
		
		xxx =  GSR_ohm  
		yyy =   num_array[ len(num_array)-2 ]
		
		num_array2.insert(len(num_array2), GSR_ohm)
		
		if abs ( xxx - yyy )  > 500 :
			#print("big")
			#GSR_ohm = num_array[ len(num_array)-2 ]
			num_array.insert(len(num_array), GSR_ohm)
		else:
			num_array.insert(len(num_array), GSR_ohm)
		
		N = 5000
		anp = array( num_array )
		moving_ave = uniform_filter1d(anp, size=N)
		#moving_ave_v = moving_ave / np.sqrt(np.sum(moving_ave**2))
		
		#print(np.mean(moving_ave), "  :  " ,moving_ave[len(num_array)-1])
	

		my_var2[0] = np.mean(moving_ave)
		my_var2[1] = moving_ave[len(num_array)-1]
		my_var2[2] = 0






my_var2 = [1, 2, 3]
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


def calibrateEyeTrackerPyGaze():
    """
        Runs the callibration process using PyGaze and tobii eye trackers.
    """

    disp = Display()
    tracker = EyeTracker(disp,resolution=(1920,1080),  trackertype='tobii')
    
    #tracker.calibrate()
    
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


def thread_tracker_function():
	
	#global current_tracker_sample
	global my_var2
	
	nnn=5001-1
	nnnn = nnn+1
	
	N = 5000
		
	num_array_x =  [0] * nnn
	num_array_y =  [0] * nnn

	num_array_x_new =  [0] * 60
	num_array_y_new =  [0] * 60
		
	while True:
		current_tracker_sample = eyetracker.sample()
	


		num_array_x.pop(0)
		num_array_y.pop(0)

		num_array_x.insert(len( num_array_x ), current_tracker_sample[0])
		num_array_y.insert(len( num_array_y ), current_tracker_sample[1])
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
			
	
		
		#print('current gaze is at: ',current_tracker_sample) #tuple(x,y)
		#print('current gaze is at: ',current_tracker_sample) #tuple(x,y)
		
		my_var[0] = np.mean(moving_ave1)
		my_var[1] = np.mean(moving_ave2)
		my_var[2] = ddddd
		my_var[3] = 0
		
		#print('xxx: ',my_var[0]) #tuple(x,y)
		#print('yyy: ',my_var[1]) #tuple(x,y)
		
		#gaze_array = updateRollingArray(gaze_array,current_tracker_sample)
	
		
		#


#
my_var = [1, 2, 3, 4]
thread_eyetracker = threading.Thread(target=thread_tracker_function, args=()) # , daemon=True

thread_eyetracker.start()


#thread_eyetracker.




#while True:
	#print("var1: ", my_var[0]," var2: ", my_var[1])
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
	'cell_size':	20,
	'cols':		16,
	'rows':		32,
	'delay':	750,
	'maxfps':	60
}

colors = [
	(0,   0,   0  ),
	(189, 119, 223),
	(119, 154, 223),
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
	 [1, 1, 1]],
 
	[[1, 1]],

	[[1]]]

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

last_diff_gsr = my_var2[1] - my_var2[0]
last_gaze_var = my_var[2]
measurement = 1 # measurements from sensor - plug in own data
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
		
		#print("gazex: ", my_var[0]," gazey: ", my_var[1],"gazex: ", my_var[0]," gazey: ", my_var[1])
		
		#print("meangsr: ", my_var2[0]," currentgsr: ", my_var2[1])
		
		#print("gaze", my_var[2])
		global measurement
		global last_diff_gsr
		global last_gaze_var
		
		curr_diff_gsr = my_var2[1] - my_var2[0]
		curr_gaze_var = my_var[2]
		
		# measurement = difficulty level 

		# if the user was more stressed on eye and gsr reduce by 1
		if curr_diff_gsr > last_diff_gsr and curr_gaze_var > last_gaze_var:
			if measurement != 1:
				measurement = measurement -1
		
		#if user was calm on eye and gsr increase by 1 
		if curr_diff_gsr < last_diff_gsr or curr_gaze_var < last_gaze_var:
			if measurement != 0 and measurement < 9:
				measurement = measurement +1
		
		print(measurement,curr_diff_gsr,last_diff_gsr,curr_gaze_var,last_gaze_var)
		
		last_diff_gsr = my_var2[1] - my_var2[0]
		last_gaze_var = my_var[2]
		
		self.stone_y = 0
		if measurement == 0:			
			self.stone = normal[rand(len(normal))]
			self.stone_y += 1
		elif measurement == 1:
			self.stone = level1[rand(len(level1))]
			self.stone_y += 2
		elif measurement == 2:
			self.stone = level2[rand(len(level2))]
			self.stone_y += 3
		elif measurement == 3:
			self.stone = level3[rand(len(level3))]
			self.stone_y += 4
		elif measurement == 4:
			self.stone = level4[rand(len(level4))]
			self.stone_y += 5
		elif measurement == 5:
			self.stone == level5[rand(len(level5))]
			self.stone_y += 6
		elif measurement == 6:
			self.stone = level6[rand(len(level6))]
			self.stone_y += 7
		elif measurement == 7:
			self.stone = level7[rand(len(level7))]
			self.stone_y += 8
		elif measurement == 8:
			self.stone = level8[rand(len(level8))]
			self.stone_y += 9
		elif measurement == 9:
			self.stone = level9[rand(len(level9))]
			self.stone_y += 10
		else:
			print ("Please make sure sensors are configured properly!")

		self.stone_x = int(config['cols'] / 2 - len(self.stone[0])/2)
		
		
		if check_collision(self.board, self.stone, (self.stone_x, self.stone_y)):
			self.gameover = True
	
	def init_game(self):
		self.board = new_board()
		self.new_stone()
	
	def center_msg(self, msg):
		for i, line in enumerate(msg.splitlines()):
			msg_image =  pygame.font.Font(pygame.font.get_default_font(), 12).render(line, False, (255,255,255), (0,0,0))
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
		
		pygame.time.set_timer(pygame.USEREVENT+1, config['delay'])
		dont_burn_my_cpu = pygame.time.Clock()
		while 1:
			self.screen.fill((0,0,0))
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
