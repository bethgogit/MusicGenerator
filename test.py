import wave
import wave_constructor as wc
import numpy as np

SAMPLE_RATE = 44100

audio, channels = wc.generate("song.sn",SAMPLE_RATE)

# Convert to (little-endian) 16 bit integers.
audio = (audio * (2 ** 15 - 1)).astype("<h")

file_name = "thesound.wav"



with wave.open(file_name, "w") as f:
    # 2 Channels.
    f.setnchannels(2)
    # 2 bytes per sample.
    f.setsampwidth(2)
    f.setframerate(SAMPLE_RATE*channels)
    f.writeframes(audio.tobytes())
