from typing import List, Dict, Any, Optional, Union

from openai.types.chat import ChatCompletion, ChatCompletionMessage, ChatCompletionChunk
from openai.types import ChatModel, CompletionUsage

from ..ai import constant


class OpenAIRequestBuilder:
    def __init__(self, model: ChatModel = constant.GPTModel.GPT_4O_MINI) -> None:
        self.model = model
        self.messages: List[Dict[str, str]] = []
        self.temperature: float = 1.0
        self.max_tokens: Optional[int] = None
        self.top_p: float = 1.0
        self.frequency_penalty: float = 0.0
        self.presence_penalty: float = 0.0
        self.stream: bool = False

    def add_system_message(self, content: str) -> "OpenAIRequestBuilder":
        self.messages.append({"role": "system", "content": content})
        return self

    def add_user_message(self, content: str) -> "OpenAIRequestBuilder":
        self.messages.append({"role": "user", "content": content})
        return self

    def add_assistant_message(self, content: str) -> "OpenAIRequestBuilder":
        self.messages.append({"role": "assistant", "content": content})
        return self

    def set_temperature(self, temperature: float) -> "OpenAIRequestBuilder":
        self.temperature = temperature
        return self

    def set_max_tokens(self, max_tokens: int) -> "OpenAIRequestBuilder":
        self.max_tokens = max_tokens
        return self

    def set_top_p(self, top_p: float) -> "OpenAIRequestBuilder":
        self.top_p = top_p
        return self

    def set_frequency_penalty(self, frequency_penalty: float) -> "OpenAIRequestBuilder":
        self.frequency_penalty = frequency_penalty
        return self

    def set_presence_penalty(self, presence_penalty: float) -> "OpenAIRequestBuilder":
        self.presence_penalty = presence_penalty
        return self

    def set_stream(self, stream: bool) -> "OpenAIRequestBuilder":
        self.stream = stream
        return self

    def build(self) -> Dict[str, Any]:
        request = {
            "model": self.model,
            "messages": self.messages,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stream": self.stream,
        }

        if self.max_tokens is not None:
            request["max_tokens"] = self.max_tokens

        return request

    def parse_response(
        self, response: Union[ChatCompletion, ChatCompletionChunk]
    ) -> Dict[str, Any]:
        if isinstance(response, ChatCompletionChunk):
            delta = response.choices[0].delta
            return {
                "content": delta.content if hasattr(delta, "content") else None,
                "role": delta.role if hasattr(delta, "role") else None,
                "finish_reason": response.choices[0].finish_reason,
                "usage": None,
            }
        else:
            message: ChatCompletionMessage = response.choices[0].message
            usage: Optional[CompletionUsage] = response.usage

            return {
                "content": message.content,
                "role": message.role,
                "usage": (
                    {
                        "prompt_tokens": usage.prompt_tokens if usage else None,
                        "completion_tokens": usage.completion_tokens if usage else None,
                        "total_tokens": usage.total_tokens if usage else None,
                    }
                    if usage
                    else None
                ),
            }
