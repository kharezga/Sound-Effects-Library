import pyaudio
import numpy as np
import soundfile as sf
import matplotlib.pyplot as plt


class OverlapAddNode(object):
    def __init__(self, config, audio_in, overlap=0.5, fft_filtering=True, monitor=False):
        """
        Instantiates offline OverlapAddNode with given configuration.

        :param config:
        :param audio_in:
        :param overlap:
        :param fft_filtering:
        :param monitor:
        """
        self.hop_size = int(config.buffer_size // (1/(1-overlap)))  # 50% overlap
        self.hann_window = np.hanning(config.buffer_size+1)[:-1].reshape((-1, 1))
        next_power_of_two = 2 ** int(np.ceil(np.log2(config.buffer_size)))
        self.fft_size = next_power_of_two * 2  # zero-pad factor

        # not totally proper but working; to be tighten up
        if fft_filtering:
            self.normalization = 2 * self.hop_size / config.buffer_size
            self.output_buffer_size = 2 * config.buffer_size
        else:
            self.normalization = (self.hop_size / np.sum(self.hann_window)) if overlap != 0 else 1
            self.output_buffer_size = config.buffer_size

        self.audio_in = audio_in
        self._preprocess_input()
        # n = self.audio_in.shape[0] // config.buffer_size * config.buffer_size
        # self.audio_in = self.audio_in[:n, :]  # truncate to int number of blocks

        pad_last_frame = config.buffer_size - (self.audio_in.shape[0] % config.buffer_size)
        self.audio_out = np.zeros((self.audio_in.shape[0]+pad_last_frame, config.channel_count), dtype=np.float32)
        self.output_buffer = np.zeros((self.output_buffer_size, config.channel_count), dtype=np.float32)

        self.frm_in_ptr = self.frm_out_ptr = 0
        self.fft_filtering = fft_filtering
        self.config = config

        if monitor:
            self.pa = pyaudio.PyAudio()
            self.stream = self.pa.open(rate=self.config.sample_rate, channels=self.config.channel_count,
                                       format=pyaudio.paInt16, frames_per_buffer=self.hop_size, output=True)

    def pull_frame(self, window=True):
        """
        Pulls one frame from input PCM stream.

        :param window:
        """
        audio_frame = self.audio_in[self.frm_in_ptr:(self.frm_in_ptr+self.config.buffer_size), :].copy()
        audio_frame = np.pad(audio_frame, ((0, self.config.buffer_size-audio_frame.shape[0]), (0, 0)))
        if window:
            audio_frame *= self.hann_window
        self.frm_in_ptr += self.hop_size
        frames_available = True if (self.frm_in_ptr < self.audio_in.shape[0]) else False

        return audio_frame, frames_available

    def write_frame(self, audio_frame=None):
        """
        Writes processed frame to output buffer.

        :param audio_frame:
        """
        self.output_buffer[:self.hop_size, :] = 0
        self.output_buffer = np.roll(self.output_buffer, -self.hop_size, axis=0)

        if audio_frame is not None:
            self.output_buffer += audio_frame * self.normalization
            audio_out_hop = self.output_buffer[:self.hop_size, :].copy()
        else:
            audio_out_hop = self.audio_in[self.frm_out_ptr:(self.frm_out_ptr + self.hop_size), :].copy()
            audio_out_hop = np.pad(audio_out_hop, ((0, self.hop_size - audio_out_hop.shape[0]), (0, 0)))

        if self.fft_filtering:  # if anything goes wrong blame this and ***below
            if self.frm_in_ptr > self.hop_size:  # skip zero samples at the beginning
                self.audio_out[self.frm_out_ptr:(self.frm_out_ptr+self.hop_size), :] = audio_out_hop
                self.frm_out_ptr += self.hop_size
        else:
            self.audio_out[self.frm_out_ptr:(self.frm_out_ptr + self.hop_size), :] = audio_out_hop
            self.frm_out_ptr += self.hop_size

        # static buffer
        # self.audio_out[self.frm_out_ptr:(self.frm_out_ptr+self.output_buffer_size), :] += \
        #     audio_frame * self.normalization
        # self.frm_out_ptr += self.hop_size

        if hasattr(self, 'stream'):  # plays 16bit/48kHz stream to default audio device
            audio_scaled = audio_out_hop * 2 ** 16 - 1
            audio_int16 = audio_scaled.astype(np.int16)
            raw_samples = audio_int16.tobytes()
            self.stream.write(raw_samples)

        # ***pull the remaining samples
        if self.fft_filtering and self.frm_out_ptr == (self.audio_out.shape[0] - 2 * self.hop_size):
            self.write_frame(np.zeros((self.output_buffer_size, self.config.channel_count)))

    def close_stream(self):
        """
        Closes and trims output stream.
        """
        self.audio_out = self.audio_out[:self.audio_in.shape[0], :]

    def reset(self):
        """
        Resets overlap-add node.
        """
        self.frm_in_ptr = self.frm_out_ptr = 0

    def _read_wav_file(self, wav_file):
        """
        Reads PCM stream from WAV file.

        :param wav_file:
        """
        self.audio_in, self.sample_rate = sf.read(wav_file, always_2d=True, dtype='float32')
        self.config = self.config._replace(channel_count=self.audio_in.shape[1], sample_rate=self.sample_rate)
        self._preprocess_input()

    def _preprocess_input(self):
        """
        Pre-processes input audio to fit the signal chain.
        """
        if len(self.audio_in.shape) == 1:
            self.audio_in = self.audio_in.reshape((-1, 1))
        elif np.argmax(self.audio_in.shape) != 0:
            self.audio_in = self.audio_in.transpose()
