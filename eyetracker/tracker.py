
#install the tobi i tracker from the usb
#!pip install tobii_research
#!pip install python-pygaze
#!pip install psychopy
#!pip install pygame

import tobii_research as tr

from pygaze.display import Display
from pygaze.eyetracker import EyeTracker
from pygaze import settings; settings.TRACKERSERIALNUMBER = 'X230C-030127221071'
from pygaze import settings; settings.FULLSCREEN = False
from pygaze import settings; settings.DISPSIZE = (1920,1080)
#from pygaze import settings; settings.DISPTYPE = 'pygame' # this did not work in my case but it might be easier for the pygame application

import numpy as np
import pandas as pd


def calibrateEyeTrackerPyGaze():
    """
        Runs the callibration process using PyGaze and tobii eye trackers.
    """

    disp = Display()
    tracker = EyeTracker(disp,resolution=(1920,1080),  trackertype='tobii')
    
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


# pupil size measurements

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

print(avaliableEyeTrackers())

eyetracker = calibrateEyeTrackerPyGaze()


eyetracker.start_recording()    
gaze_array = range(1,30)
while True:

    current_sample = eyetracker.sample()
    print('current gaze is at: ',current_sample) #tuple(x,y)
    gaze_array = updateRollingArray(gaze_array,current_sample)
    #current_gaze_mean = np.mean(gaze_array,axis=0)

#eyetracker.stop_recording()
#eyetracker.close()


