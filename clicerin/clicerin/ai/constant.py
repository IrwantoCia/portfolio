from pathlib import Path
from openai.types import ChatModel

SYSTEM_PROMPT = str(Path(__file__).parent / "SYSTEM_PROMPT")


class GPTModel:
    GPT_4O_MINI: ChatModel = "gpt-4o-mini"
    GPT_4O_AUDIO_PREVIEW: ChatModel = "gpt-4o-audio-preview"
