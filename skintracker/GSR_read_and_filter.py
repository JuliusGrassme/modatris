#!/usr/bin/python
import sys, struct, serial

import math

nnn=200-1
nnnn = nnn+1
import matplotlib.pyplot as plt
from scipy.ndimage.filters import uniform_filter1d
import numpy

from numpy  import array



num_array =  [0] * nnn
num_array
print(num_array)
numrange = range(0,nnn)
numrange2 = range(0,42)

num_to_add = 0


def wait_for_ack():
	ddata = ""
	ack = struct.pack('B', 0xff)
	while ddata != ack:
		ddata = ser.read(1)
		#print( "0x%02x" % ord(ddata[0])  )
	  
	return

if len(sys.argv) < 2:
	print( "no device specified" )
	print( "You need to specify the serial port of the device you wish to connect to" )
	print( "example:" )
	print( "	aAccel5Hz.py Com12" )
	print( "or")
	print( " aAccel5Hz.py /dev/rfcomm0" )
else:
	ser = serial.Serial(sys.argv[1], 115200)
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

	'''
	 sampling_freq = 32768 / clock_wait = X Hz
	'''
	sampling_freq = 5
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
	numbytes = 0
	framesize = 8 # 1byte packet type + 3byte timestamp + 2 byte GSR + 2 byte PPG(Int A13)

	print( "Packet Type\tTimestamp\tGSR\tPPG" )
	try:
		while True:
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

			#print( "0x%02x\t\t%5d,\t%4d,\t%4d" % (packettype[0], timestamp, GSR_ohm, PPG_mv) )
		 
		 
			
			
			
			#print ( "prev", num_array[num_to_add-2] ) 
			
			"""
			if num_to_add > 1 and GSR_ohm/5 > num_array[num_to_add-1]:
				num_array.pop(0)
				num_array.insert(len(num_array), )
			else:

			"""
			
			
			num_array.pop(0)
			
			print("O: ", GSR_ohm)
			print("L: ", num_array[ len(num_array)-2 ])
			
			xxx =  GSR_ohm  
			yyy =   num_array[ len(num_array)-2 ]
			
			if abs ( xxx - yyy )  > 1000 :
				print("big")
				GSR_ohm = num_array[ len(num_array)-2 ]
				num_array.insert(len(num_array), GSR_ohm)

				
			else:
				num_array.insert(len(num_array), GSR_ohm)
			
			
			

			
			

			
			#
			
			#num_array.insert(len(num_array), num_array[ len(num_array)-2 ])
			

			
			if num_to_add > nnn:

				num_to_add = 0
			
				#mylist = num_array
				#N = 100
				#cumsum, moving_aves = [0], []

				#for i, x in enumerate(mylist, 1):
				#	cumsum.append(cumsum[i-1] + x)
				#	if i>=N:
				#		moving_ave = (cumsum[i] - cumsum[i-N])/N
				#		#can do stuff with moving_ave here
				#		moving_aves.append(moving_ave)
				#		print(moving_ave)

				
				
				
				plt.plot(numrange, num_array )
				plt.ylabel('some numbers')
				plt.show()
				
				anp = array( num_array )
				
				
				
				N = 10
				
				moving_ave = uniform_filter1d(anp, size=N)
			
				plt.plot(numrange, moving_ave )
				plt.ylabel('some numbers')
				plt.show()
		 
		 
		 
			num_to_add = num_to_add +1
			#if Range == 0:
			#	print(Range, GSR_raw , GSR_ohm)

	except KeyboardInterrupt:
#send stop streaming command
		ser.write(struct.pack('B', 0x20))
		print( )
		print( "stop command sent, waiting for ACK_COMMAND" )
		wait_for_ack()
		print( "ACK_COMMAND received." )
#close serial port
		ser.close()
		print( "All done" )