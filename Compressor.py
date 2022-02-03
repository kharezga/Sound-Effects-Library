import numpy as np
import pylab as py
import soundfile as sf
import os
import time



class Compress():
    def __init__(self, config):
        self.config = config




    def get_more_param(self, data, param):
        """
        Determines if file is mono or stereo and converts data to dB.
        Parameters
        ----------
        filename: string Name of the input <audio> file.
        Returns
        -------
        num_of_samples: length of audio in samples
        data: array containing the signal in bits.
        data_dB: array containing the signal in dB.
        sample_rate: sample rate
        num_of_channels: number of audio channels. 1 = mono, 2 = stereo
        """

        try:
            num_of_channels = len(data[0,])
        except:
            num_of_channels = 1
        print('File contains ' + str(num_of_channels) + ' audio channel(s)...')

        # Reshape the data so other functions can interpret the array if mono.

        if num_of_channels == 1:
            data = data.reshape(-1, 1)
        num_of_samples = len(data)

        # This prevents log(data) producing nan when data is 0
        data[np.where(data == 0)] = 0.00001

        # convert to dB
        data_dB = 20 * np.log10(abs(data))

        if param == 'NUM_SAMPLE':
            return num_of_samples
        if param == 'data_DB':
            return data_dB
        else:
            return NULL


    def compress(self, data, threshold, ratio, makeup, attack, release, wout=False, plot=False):
        """
        Reduces dynamic range of input signal by reducing volume above threshold.
        The gain reduction is smoothened according to the attack and release.

        Parameters
        ----------
        filename: string
            Name of the input *.wav file.
        threshold: scalar (dB)
            value in dB of the threshold at which the compressor engages in
            gain reduction.
        ratio: scalar
            The ratio at which volume is reduced for every dB above the threshold
            (i.e. r:1)
            For compression to occur, ratio should be above 1.0. Below 1.0, you
            are expanding the signal.

        makeup: scalar (dB)
            Amount of makeup gain to apply to the compressed signal

        attack: scalar (ms)
            Characteristic time required for compressor to apply full gain
            reduction.

        release: scalar (ms)
            Characteristic time that the compressor will hold the gain reduction
            before easing off. Both attack and release basically smoothen the gain
            reduction curves.

        wout:
            Writes the data to a 16 bit *.wav file

        plot: True/False, optional, default=True
            Produces plot of waveform and gain reduction curves.

        Returns
        -------
        data_Cs: array containing the compressed waveform in dB
        data_Cs_bit: array containing the compressed waveform in bits.
        """


        # Check if ratio is valid
        if ratio < 1.0:
            print('Ratio must be > 1.0 for compression to occur!')
        if ratio == 1.0:
            print('Signal is unaffected.')




        sample_rate = self.config.sample_rate
        channels = self.config.channel_count
        number_of_samples = get_more_param(data, 'NUM_SAMPLE')
        data_dB = get_more_param(data, 'data_DB')

        # Array for the compressed data in dB
        dataC = data_dB.copy()

        # attack and release time constant
        a = np.exp(-np.log10(9) / (44100 * attack * 1.0E-3))
        re = np.exp(-np.log10(9) / (44100 * release * 1.0E-3))

        # apply compression
        print('Compressing...')
        for k in range(channels):
            for i in range(number_of_samples):
                if dataC[i, k] > threshold:
                    dataC[i, k] = threshold + (dataC[i, k] - threshold) / (ratio)

        # gain and smooth gain initialization
        gain = np.zeros(number_of_samples)
        sgain = np.zeros(number_of_samples)

        # calculate gain
        gain = np.subtract(dataC, data_dB)
        sgain = gain.copy()

        # smoothen gain
        print('Smoothing...')
        for k in range(channels):
            for i in range(1, number_of_samples):
                if sgain[i - 1, k] >= sgain[i, k]:
                    sgain[i, k] = a * sgain[i - 1, k] + (1 - a) * sgain[i, k]
                if sgain[i - 1, k] < sgain[i, k]:
                    sgain[i, k] = re * sgain[i - 1, k] + (1 - re) * sgain[i, k]

        # Array for the smooth compressed data with makeup gain applied
        dataCs = np.zeros(number_of_samples)
        dataCs = data_dB + sgain + makeup
        # Convert our dB data back to bits
        dataCs_bit = 10.0 ** ((dataCs) / 20.0)

        # sign the bits appropriately:
        for k in range(channels):

            for i in range(number_of_samples):
                if data[i, k] < 0.0:
                    dataCs_bit[i, k] = -1.0 * dataCs_bit[i, k]

        # Plot the data:
        if plot == True:
            print('Plotting...')
            t = np.linspace(0, number_of_samples / (1.0 * sample_rate), number_of_samples)
            py.close()
            fig, (ax1, ax2) = py.subplots(nrows=2)
            ax2.plot(t, gain, 'k-', linewidth=0.1, label='Gain Reduction')
            ax2.plot(t, sgain, 'r-', linewidth=1, label='Gain Reduction Smooth')
            ax1.plot(t, data, 'k-', linewidth=1, label=filename)
            ax1.plot(t, dataCs_bit, 'm-', linewidth=0.1,
                     label=filename + ' compressed')
            ax1.axhline(10 ** (threshold / 20.0), linestyle='-',
                        color='cyan', linewidth=1)
            ax1.axhline(-10 ** (threshold / 20.0), linestyle='-',
                        color='cyan', linewidth=1)
            ax1.legend()
            ax2.legend()
            ax2.set_xlabel('Time (s)')
            ax2.set_ylabel('Gain Reduction (dB)')
            ax1.set_ylabel('Amplitude (Rel. Bit)')
            ax1.set_xlabel('Time (s)')

        # write data to 16 bit file
        if wout == True:
            print('Exporting...')
            sf.write('_compressed.wav', dataCs_bit,
                     sample_rate, 'PCM_16')


        print('Done!')
        print('...............................')

        return dataCs_bit
