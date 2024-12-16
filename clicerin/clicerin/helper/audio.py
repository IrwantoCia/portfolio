from ctypes import *
import base64
import io
import threading

import numpy as np
import pyaudio
import soundfile as sf
import wave

from pydub import AudioSegment
from pydub.playback import play


import pyaudio
import numpy as np
import threading

### DISABLE ALSA WARNING MESSAGE
# https://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time
ENABLE_WARNING = False
if not ENABLE_WARNING:
    ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

    def py_error_handler(filename, line, function, err, fmt):
        pass

    c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

    asound = cdll.LoadLibrary("libasound.so")
    # Set error handler
    asound.snd_lib_error_set_handler(c_error_handler)
### DISABLE ALSA WARNING MESSAGE


class AudioRecorder:
    def __init__(self):
        self.CHUNK = 2048
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 48000
        self.recording = False
        self.audio = pyaudio.PyAudio()
        self.audio_data = None
        self.sample_rate = None
        self._record_thread = None

    def _record_audio(self):
        frames = []
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        while self.recording:
            try:
                data = stream.read(self.CHUNK, exception_on_overflow=False)
                audio_array = np.frombuffer(data, dtype=np.float32)
                # Amplify the audio signal
                audio_array = audio_array * 5.0  # Increase amplitude by 5x
                frames.append(audio_array)
            except IOError as e:
                print(f"Warning: {e}")
                continue

        stream.stop_stream()
        stream.close()
        self.audio.terminate()

        self.audio_data = np.concatenate(frames)
        self.sample_rate = self.RATE

    def record(self):
        """
        Records audio from the default microphone and stores the audio data
        in class attributes. Recording continues until Enter key is pressed.
        The recording runs in a separate thread.
        """
        if self._record_thread is not None and self._record_thread.is_alive():
            return

        self.recording = True
        self._record_thread = threading.Thread(target=self._record_audio)
        self._record_thread.start()

    def stop_recording(self):
        """
        Stops the audio recording and waits for the recording thread to finish.
        """
        self.recording = False
        if self._record_thread is not None:
            self._record_thread.join()
            self._record_thread = None


def audio_to_base_64(audio, rate):
    # audio is numpy array 1D from pyaudio
    # OpenAI API expects 16-bit PCM WAV format

    # Convert to int16 format (required by OpenAI)
    audio = (audio * 32767).astype(np.int16)

    # Create an in-memory binary stream
    buffer = io.BytesIO()

    # Create a WAV file in the buffer
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)  # Mono audio required by OpenAI
        wav_file.setsampwidth(2)  # 2 bytes per sample (16-bit)
        wav_file.setframerate(rate)  # Sample rate must be between 8000 and 48000 Hz
        wav_file.writeframes(audio.tobytes())

    # Get the WAV data from the buffer
    buffer.seek(0)
    wav_data = buffer.getvalue()

    # Convert to base64, which is required by OpenAI's API
    base64_encoded = base64.b64encode(wav_data).decode("utf-8")
    return base64_encoded


def save(audio_data, sample_rate, output_path="./output.wav"):
    """
    Save audio data to a file.

    Args:
        audio_data (numpy.ndarray): The input audio data
        sample_rate (int): The sample rate of the audio
        output_path (str, optional): The path where the audio file will be saved. Defaults to 'output.wav'

    Returns:
        None
    """

    # Ensure audio data is in the correct format (float32)
    audio_data = audio_data.astype("float32")

    # Save the audio file
    sf.write(output_path, audio_data, sample_rate)


def play_audio(file_path=None):
    """
    Play an audio file using pydub.

    Args:
        file_path (str, optional): Path to the audio file to play.
            If None, returns without playing.
    """
    if not file_path:
        return

    try:
        audio = AudioSegment.from_file(file_path)
        play(audio)

    except Exception as e:
        print(f"Error playing audio: {str(e)}")


def play_audio_base_64(base64_data):
    """
    Play audio from a base64 encoded string using pydub.

    Args:
        base64_data (str): Base64 encoded audio data
    """

    try:
        # Decode base64 data
        decoded_data = base64.b64decode(base64_data)

        # Create a buffer with the decoded data
        audio_buffer = io.BytesIO(decoded_data)

        # Load the audio using pydub
        audio = AudioSegment.from_file(audio_buffer)

        # Play the audio
        play(audio)

    except Exception as e:
        print(f"Error playing audio: {str(e)}")
