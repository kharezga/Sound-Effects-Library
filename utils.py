import numpy as np

from warnings import warn
from collections import namedtuple as nt
from scipy.sparse import csr_matrix
import matplotlib.pyplot as plt

supported_sample_rates = (44100, 48000, 88200, 96000)


def get_default_config(fs=48000, buffer_size=2048, filter_bank='ERB'):
    """
    Creates default Dynamic EQ configuration in a form of named tuple.

    :param fs: sample rate
    :param buffer_size: audio frame size
    :param filter_bank: analysis/synthesis filter bank
    """
    if fs not in supported_sample_rates:
        warn('Sample rate {}Hz is not supported. We\'ve assumed fs=48000 and continue.'.format(fs))
        fs = 48000

    zeropad_factor = 2
    next_power_of_two = 2 ** int(np.ceil(np.log2(buffer_size)))
    fft_size = next_power_of_two * zeropad_factor
    nfreq = fft_size // 2 + 1

    ERB_spacing = 0.5
    ERB_matrix_analysis, _, center_freqs = compute_ERB_filters(nfreq, fs, 'sinus', True, 30, 18000, ERB_spacing)
    _, ERB_matrix_synthesis, _, = compute_ERB_filters(nfreq, fs, 'sinus', False, 30, 18000, ERB_spacing)

    config = nt('config',
                'sample_rate channel_count buffer_size hop_size ERB_spacing target_level fft_size n_freqs window '
                'ERB_matrix_analysis ERB_matrix_synthesis center_freqs n_bands c_attack c_release normalization '
                'compression_ratio min_dBFS max_dBFS ')

    config.__new__.__defaults__ = config(sample_rate=fs,
                                         channel_count=2,
                                         buffer_size=buffer_size if fs in supported_sample_rates[
                                                                          :2] else buffer_size * 2,
                                         hop_size=buffer_size // 2,
                                         ERB_spacing=0.5,
                                         target_level=-23,
                                         fft_size=fft_size,
                                         n_freqs=nfreq,
                                         window=np.hanning(buffer_size + 1)[:-1].reshape((-1, 1)),
                                         normalization=1,
                                         ERB_matrix_analysis=csr_matrix(ERB_matrix_analysis),
                                         ERB_matrix_synthesis=csr_matrix(ERB_matrix_synthesis),
                                         center_freqs=center_freqs,
                                         n_bands=center_freqs.size,
                                         c_attack=np.exp((-buffer_size / 2) / (50 * 10 ** -3 * fs + 1)),
                                         c_release=np.exp((-buffer_size / 2) / (1000 * 10 ** -3 * fs + 1)),
                                         compression_ratio=1,
                                         min_dBFS=-160,
                                         max_dBFS=160)

    return config


def compute_ERB_filters(K=2049, fs=48000, shape='sinus', normalized=True, fmin=30, fmax=18000, ERB_spacing=0.5):
    """
    Computes ERB based auditory filter bank.

    :param K: number of frequency coefficients
    :param fs: sample rate [Hz]
    :param shape: filter shape
    :param normalized: ensure a unity sum of each filter response
    :param fmin: smallest center frequency [Hz]
    :param fmax: highest center frequency [Hz]
    :param ERB_spacing: resolution on ERB scale
    """
    ERB_L = 24.7  # minimum ERB bandwidth (24.7)
    ERB_Q = 9.265  # Q factor of auditory filters
    ERB_O = 4  # Filter order

    fs *= fs // 44100

    c1 = 1 / (2 * K)
    c2 = 1 / fs
    nB = 0
    k0 = int(np.ceil(fmin * 2 * K / fs))
    k1 = int(np.ceil(fmin * 2 * K / fs))
    Kmax = min(K, np.floor(fmax * 2 * K / fs))

    # Compute analysis matrix based on triangular patterns:
    ERB_filter = [np.zeros((K,))]
    ERB_filter[-1][:k1] = 1
    center_freqs = []
    while k1 < Kmax:
        ERB_filter.append(np.zeros((K,)))
        nB = nB + 1
        k0 = k1
        bw = (ERB_L + (k0 * fs * c1) / ERB_Q) * ERB_spacing
        k1 = k0 + max(1, round(2 * K * bw * c2))
        k1 = min(k1, K)
        center_freqs.append(fs * np.sqrt((k0 - 1) * (k1 - 2)) / (2 * K))
        ERB_filter[-2][k0 - 1:k1] = np.linspace(1, 0, k1 + 1 - k0)
        ERB_filter[-1][k0 - 1:k1] = np.linspace(0, 1, k1 + 1 - k0)

    nB += 1
    ERB_filter[-1][k1:] = 1
    ERB_filter = np.array(ERB_filter)
    center_freqs.append(fs * k1 / (2 * K))
    center_freqs = np.array(center_freqs)

    for b in range(nB):
        if shape == 'sinus':
            ERB_filter[b, :] = 0.5 - 0.5 * np.cos(ERB_filter[b, :] * np.pi)
        if normalized:
            ERB_filter[b, :] = ERB_filter[b, :] / np.sum(np.abs(ERB_filter[b, :]))
    ERB_synth = ERB_filter.T

    return ERB_filter, ERB_synth, center_freqs


def collect_frames(audio_frame):
    signal = []
    i = 0
    signal[i] = audio_frame
    i += 1


def plot_processed_signal(audio_signal, time, amplitude):
    """
    Plot the signal (mostly for debuging purposes).

    :param audio_signal
    :param time: time domain of the signal
    :param amplitude: amplitude domain of the signal

    """

    plt.plot()
    plt.xlabel('time [s]')
    plt.ylabel('Amplitude')
    plt.show()
