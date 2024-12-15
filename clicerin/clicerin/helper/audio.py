import base64
import io

import numpy as np
import pyaudio
import soundfile as sf
import wave

from pydub import AudioSegment
from pydub.playback import play


def record():
    """
    Records audio from the default microphone and returns the audio data.
    Recording continues until Enter key is pressed.

    Returns:
        tuple: A tuple containing (audio_data, sample_rate)
    """

    CHUNK = 2048
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    RATE = 48000

    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK
    )

    print("Recording... Press Enter to stop.")

    frames = []
    recording = True

    def check_input():
        nonlocal recording
        input()
        recording = False

    import threading

    input_thread = threading.Thread(target=check_input)
    input_thread.daemon = True
    input_thread.start()

    while recording:
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_array = np.frombuffer(data, dtype=np.float32)
            # Amplify the audio signal
            audio_array = audio_array * 5.0  # Increase amplitude by 5x
            frames.append(audio_array)
        except IOError as e:
            print(f"Warning: {e}")
            continue

    print("Done recording.")

    stream.stop_stream()
    stream.close()
    audio.terminate()

    audio_data = np.concatenate(frames)
    return audio_data, RATE


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
