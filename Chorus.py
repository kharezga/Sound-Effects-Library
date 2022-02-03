import numpy as np
import pylab as py
import soundfile as sf
import os
import time
from scipy.signal import resample

from Compressor import get_more_param

class chorus:
    def __init__(self, config):
        self.config = config

    def chorus(self, data):
        """
        Produces chorus effect on input
        Parameters
        ----------
        :param wout: True/False, optional, default=True
            Writes the data to a 16 bit *.wav file
        :param data: input audio
        """



        sample_rate = self.config.sample_rate
        channels = self.config.channel_count
        number_of_samples = get_more_param(data, 'NUM_SAMPLE')
        data_dB = get_more_param(data, 'data_DB')

        data_1 = slow(data, p=0.1)
        data_2 = slow(data, p=-0.1)

        data_2pd = np.zeros((len(data_1), channels))
        data_2pd[0:len(data_2), :] = data_2
        data_pd = np.zeros((len(data_1), channels))
        data_pd[0:len(data), :] = data
        if channels == 2:
            print('Adding stereo chorus...')
            sf.write('./chorusw.wav', data_1 + data_2pd, 44100, 'PCM_24')
            st = stereo(data, 2)
            data_F = data_pd + 0.3 * st
        else:
            print('Adding mono chorus...')
            data_F = data_pd + 0.81 * data_1 + 0.8 * data_2pd

        print('Done!')
        print('...............................')

        return data_F


    def slow(self, data ,p=10):
        """
        Resamples the input by p%, slowing it down by p%. Uses the scipy resample
        function.

        :param p: slowing factor
        :param data: input audio
        """

        if p > 0:
            print('Slowing...')
        if p < 0:
            print('Warning: You are speeding up the audio! Use positive value'
                  + ' for p to slow.')
        f = resample(data, int(len(data) * (1 + p / 100.0)))

        return f


    def stereo(self, data, time):
        """
        Produces stereo effect. If file is mono, two channels are created and the
        R channel is delayed to simulate stereo width. Beware of phase issues.
        Parameters

        data_st: array containing the stereo waveform in normalized bits.
        :param time: scalar (ms)
            Amount of time the right channel is delayed by, in milliseconds.
        :param data:  input audio frame
        """

        s_shift = int(sr * time * 1E-3)
        R = np.zeros(n)
        L = np.zeros(n)
        if ch == 2:
            L[:] = data[:, 0]
            R[:] = data[:, 1]
        if ch == 1:
            L[:] = data[:, 0]
            R[:] = data[:, 0]
        print('Applying stereo width...')
        for i in range(n - s_shift):
            R[i] = R[i + s_shift]
        data_st = np.zeros((n, 2))
        data_st[:, 0] = L[:]
        data_st[:, 1] = R[:]
        print('Done!')
        return data_st