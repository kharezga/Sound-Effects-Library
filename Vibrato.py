
import pyaudio
import struct
import wave
import math

class Vibrato: #Class for Vibrations
    def __init__(self, channels, rate, f0,W): #F0 - Frequency for modulation with vibration W- vibrato efect
        self.channels = channels
        self.rate = rate
        self.f0 = f0
        self.W = W

    def vibratof(self,input_frame):
        #Here we creating buffer becouse we need previous frames for making effect
        buffer_MAX =  1024                          # Lenght of the buffer
        buffer = [0.0 for i in range(buffer_MAX)]   # Here we defining that we starting from 0
        #Delay for buffer
        kr = 0  #Index Buffera
        kw = int(0.5 * buffer_MAX)  #Writing index into buffer (from wich position we wanna to start)
        output_array = input_frame.copy() #Output_array to which we will be writing our new array (modulated)

        for x in range(0, len(input_frame)):       #Loop for frame to be modulated
                input_sample = input_frame[x]          # Giving Frame into input_sample that will be modulated
                kr_prev = int(math.floor(kr))       # Getting previous and next values of buffor (KR IS FRACTIONAL)
                kr_next = kr_prev + 1               #There next value of buffor
                frac = kr - kr_prev
                if kr_next >= buffer_MAX:
                        kr_next = kr_next - buffer_MAX
                modulation = (1 - frac) * buffer[kr_prev] + frac * buffer[kr_next] #Here we taking values using interpolation
                buffer[kw] = input_sample #Making simple delay
                kr = kr + 1 + self.W * math.sin(2 * math.pi * self.f0 * x / self.rate) #Calculating new kr
                if kr >= buffer_MAX:
                        kr = 0 #Ending Buffer backing to beggining
                kw = kw + 1
                if kw == buffer_MAX:
                     kw = 0 #Ending buffer backing to front
                output_array[x]=modulation #Saving Modulation
        return output_array #Returining modulated frame