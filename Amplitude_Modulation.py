import pyaudio
import struct
import wave
import math

class AmplitudeModulation: #Calling the class AmplitudeModulation
    def __init__(self, channels, rate, f0): #Initializationg
        self.channels=channels
        self.rate=rate
        self.f0=f0

    def AM(self,input_frame): #Definition of Filter
        output_array=input_frame.copy() #Output_array to which we will be writing our new array (modulated)
        for x in range(0, len(input_frame)):  # Loop for frame
            input_sample = input_frame[x]  # Giving Frame into input_sample that will be modulated
            modulation = input_sample * math.cos(2 * math.pi * self.f0 * x / self.rate)  #Modulating input sample
            output_array[x]=modulation #Saving Modulation
        return output_array #Returining modulated frame