import pyaudio
import struct
import wave
import math
import scipy.signal as signal
import numpy as np

class fir():
    def __init__(self, rate, freq, order, mode):
        '''
        filename - file to be read and processed
        freq - filter cutoff freq
        order - order of the filter
        mode - "highpass" or "lowpass"
        only supports 2 byte long samples
        '''
        RATE=rate
        # checks if mode of the filter is valid
        valid = {"lowpass", "highpass"}
        if mode not in valid:
            raise ValueError("Filter mode must be one of %r." % valid)

        # checks if highpass filter has odd order, scipy dosent like even order with highpass
        if mode == "highpass":
            if order % 2 == 0:
                raise ValueError("Highpass filter must have odd order")

        # order of the filter must be positive, performance issues start with orders >12
        if (order < 1 or order > 32):
            raise ValueError("Filter order must be between 1 and 32")

        # open the file and read the wav file properties

        # checks if the filter cutoff freq is below niquist freq, scipy dosent like it
        if (freq > RATE / 2 or freq < 1):
            raise ValueError("Filter freq must be between 1 and half of the file sample rate")

        # starts pyaudio stream with the same parameters as input stream

        # design a filter array with given values, scale the coeff to float format
        self.filter_coeff = signal.firwin(order, freq, window="boxcar", fs=RATE, pass_zero=mode, scale=True)
        # prepare the buffer for input samples
        self.input_sample_buffer = [0] * order


    def filter(self, input_audio):
        # for each sample in the frame
        output_audio = np.zeros(len(input_audio))
        for n in range(0, len(input_audio)):
            #read one frame
            input_frame = input_audio[n]

            #shift the buffer to give space for new sample
            for x in range(len(self.input_sample_buffer) - 1, -1, -1):
                if (x > 0):
                    self.input_sample_buffer[x] = self.input_sample_buffer[x - 1]
                else:
                    #push the new sample into the buffer, convert it to float so the calculations are more predictable
                    #because filter array is in floats too
                    #self.input_sample_buffer[0] = self.short_to_float(input_frame)
                    self.input_sample_buffer[0] = input_frame
            #calculate the value of a sample using FIR filter algorithm (FIR filter uses as many samples as it's order)
            temp = 0
            for y in range(len(self.filter_coeff)):
                temp += self.filter_coeff[y] * self.input_sample_buffer[y]
            output_sample = temp
            #output_audio[n] = self.float_to_short(output_sample)
            output_audio[n] = output_sample
        #output_audio=input_audio
        return output_audio
