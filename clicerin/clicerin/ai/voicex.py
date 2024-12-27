import base64

from openai import OpenAI
from pydub import AudioSegment
from pydub.playback import play

from clicerin.memory.sqlitesaver import SqliteSaver

from ..ai import constant


class Voicex:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.memory = SqliteSaver()

    def invoke(self, encoded):
        completion = self.client.chat.completions.create(
            model=constant.GPTModel.GPT_4O_AUDIO_PREVIEW,
            modalities=["text", "audio"],
            audio={"voice": "coral", "format": "pcm16"},
            stream=True,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_audio",
                            "input_audio": {"data": encoded, "format": "wav"},
                        },
                    ],
                },
            ],
        )

        # Stream and play audio

        # Initialize an empty byte array to accumulate audio data
        audio_data = bytearray()
        current_position = 0
        CHUNK_SIZE = 32768  # 32KB buffer for smoother playback

        for chunk in completion:
            if chunk.choices[0].delta is not None:
                if hasattr(chunk.choices[0].delta, "audio"):
                    if "data" in chunk.choices[0].delta.audio:
                        decoded_data = base64.b64decode(
                            chunk.choices[0].delta.audio["data"]
                        )
                        audio_data.extend(decoded_data)

                        # Only process when we have enough data or it's the last chunk
                        if (
                            len(audio_data) - current_position >= CHUNK_SIZE
                            or chunk.choices[0].finish_reason == "stop"
                        ):
                            # Convert only the new data to an AudioSegment
                            new_segment = AudioSegment(
                                data=bytes(audio_data[current_position:]),
                                sample_width=2,  # 16-bit = 2 bytes
                                frame_rate=24000,  # Standard rate for most OpenAI audio
                                channels=1,  # Mono audio
                            )

                            # Update the position marker
                            current_position = len(audio_data)

                            # Play only the new segment
                            play(new_segment)

            if chunk.choices[0].finish_reason == "stop":
                break
