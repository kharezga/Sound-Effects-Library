import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wavfile

#Class that provides delay/echo filter
class EchoDelay:

def echoDuration(echoTime):
    echoDurationTime = echoTime
    return echoDurationTime

#Setting the value of time of delay
def delayAmplitude(delayTime):
    delayDurationTime = delayTime
    return delayDurationTime

#Setting the value of amplitude of echo delay
def initBoth(echoTime, delayTime):
    delayDurationTime = delayTime
    echoDurationTime = echoTime

def __init__(self):
    print('Object created.')

def __del__(self):
    print('Object deleted.')

#Funciton which adds the delay
#First argument is name of file
#Second argument is time of the echo after which it
#Third argument is amplitude of the delay
def addDelayEcho(soundFileName,echo, delay):
    echoLen = echoDuration(echo)
    delayAmp = delayAmplitude(delay)


#sr - sampling rate
#signalInt - signal converted to Int
#signalArray - array made from the processed signal
    sr, signalInt = wavfile.read(soundFileName+".wav")
    signalArray = singalInt.astype(np.float) / 2**15

#Making an array with same sample rate as signal consisting only of zeros
    delay_samples = round(echoLen * sr)
    zeroSignal = np.zeros(delay_samples)

#Adding the delayed signal to the original signal to obtain echo effect
    signalDelay = np.concatenate((zeroArray, signalArray))
    signalArray = np.concatenate((signalArray, zeroSignal))

#Summing up two signals together
    sumSignal = signalArray + delayAmp * signalDelay

#Saving the signal with added delay
    wavfile.write("outSignal.wav", sr, sumSignal)


