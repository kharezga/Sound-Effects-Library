import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
import scipy.signal as signal
import pyaudio
import struct
import wave
import math


class delay_echo():
    def __init__(self, sr, time, amp):
        self.sr = sr
        self.time = time
        self.amp = amp

    # sr - sampling rate
    # time - time in seconds of the delay
    # amp - the amplitude of the delayed sound

        if (amp > 1):
            raise ValueError("Amplitude values are best at the rate from 0 to 1")
        elif (amp<0):
            raise ValueError("Amplitude of delay should not be negative")

    #signalArray = signal.astype(np.float) / 2**15


    def delayEcho(self, input_audio):
        output_audio = np.zeros(len(input_audio))
        delay_audio = np.zeros(len(input_audio))
        buff = round(self.time)
        zero_sig = np.zeros(buff)
        out_len = len(output_audio) + buff
        newinput_audio = np.zeros(out_len)
        print(out_len)
        print(len(input_audio))
        print(buff)

        for i in range(0, out_len):
            if(i < len(input_audio)):
                newinput_audio[i] = input_audio[i]
            else:
                newinput_audio[i] = 0

        for m in range (0, len(newinput_audio)):
            for n in range (0, out_len-1):
                if (n<buff):
                    output_audio[n] = newinput_audio[n]
                elif (n>=buff and n<len(input_audio)):
                    output_audio[n] = newinput_audio[n] + newinput_audio[n-buff]
        #for n in range (0, len(input_audio)):
            #input_frame = np.concatenate((input_audio[n], zero_sig[n]))
            #delay_frame = np.concatenate((zero_sig[n],delay_audio[n]))
            #output_audio[n] = input_frame + delay_frame * amp

        return output_audio

        # Plotting the signal
        #plt.figure()
        #plt.plot(signal)
        #plt.plot(sumSignal)


    #Calling the function
    #delay_echo(0.1, 1)

