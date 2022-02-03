import os
import numpy as np
import soundfile as sf

from fir import fir
from utils import get_default_config
from utils import plot_processed_signal
from overlap_add_node import OverlapAddNode
from debug import Debug
from Compressor import Compress
from Amplitude_Modulation import AmplitudeModulation
from Vibrato import Vibrato

file_dir = os.path.dirname(os.path.realpath(__file__))

# read input wav file -> get its content, sample rate and number of channels
input_file = os.path.join(file_dir, 'input', 'speech_mono.wav')
(input_audio, sr) = sf.read(input_file, always_2d=True, dtype='float32')
channels = input_audio.shape[1] if input_audio.ndim > 1 else 1

# get processing parameters / configure overlap-add node
config = get_default_config()(channel_count=channels)
ola = OverlapAddNode(config, input_audio, overlap=0, fft_filtering=False, monitor=True)

# turn the debug mode on
#debug = Debug()

#AM('music_stereo.wav',400) #Filename and secondly frequency how it should be modified
#AM('music_stereo_compressed.wav',400) #Here's for using it together with compress when compress saved it.

f = fir(48000,3000,7,"lowpass")
a = AmplitudeModulation(channels,48000,400) # Declaring the class with AM filter, channels, frame rate, f0 that will be modulating
v = Vibrato(channels,48000,2,0.5) # Declaring Vibrato filter , frame rate, f0 that will be modulating , W that will be vibrato effect
#c = Compress(config)
#ch = chorus(config)

# read frames in a loop
frames_available = True
while frames_available:
    # get single frame
    audio_frame_in, frames_available = ola.pull_frame(window=False)
    # do some processing
    audio_frame_out = audio_frame_in
    #audio_frame_out[:,0] = f.filter(audio_frame_in[:,0])
    #audio_frame_out[:,0] = f.filter(audio_frame_in[:,0]) # Solo FIR Filter
    #audio_frame_out[:,0] = v.vibratof(audio_frame_in[:, 0]) #Solo Vibrato Filter
    #audio_frame_out[:,0] = a.AM(audio_frame_in[:,0]) #Solo AM Filter
    #audio_frame_out[:,0] = a.AM(f.filter(audio_frame_in[:,0])) #First FIR filter then AM Filter
    #audio_frame_out[:,0] = v.vibratof(f.filter(audio_frame_in[:,0])) #First FIR filter then Vibrato Filter
    #audio_frame_out[:,0] = f.filter(a.AM(audio_frame_in[:,0])) #First AM filter then FIR Filter
    #audio_frame_out[:,0] = f.filter(v.vibratof(audio_frame_in[:,0])) #First Vibrato filter then FIR Filter
    #audio_frame_out[:,0] = v.vibratof(a.AM(audio_frame_in[:,0])) #First AM filter then VIBRATO Filter
    #audio_frame_out[:,0] = a.AM(v.vibratof(audio_frame_in[:,0])) #First Vibrato filter then AM Filter

    # write the result to output buffer
    ola.write_frame(audio_frame_out)
ola.close_stream()

# save the output to a wav file
out_wav = os.path.join(file_dir, 'output', 'speech_processed.wav')
sf.write(out_wav, ola.audio_out, sr)

