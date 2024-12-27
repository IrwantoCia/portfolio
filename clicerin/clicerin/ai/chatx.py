from collections.abc import Iterable
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

from clicerin.memory.sqlitesaver import SqliteSaver, History

from ..helper import file
from ..ai import constant


class Chatx:
    def __init__(self, resource_id: str) -> None:
        self.client = OpenAI()
        self.memory = SqliteSaver()
        self.resource_id = resource_id
        self.history: list[ChatCompletionMessageParam] = []

    def get_history(self) -> list[History]:
        history = self.memory.get(self.resource_id)
        # convert
        for h in history:
            if h.role == "human":
                self.history.append({"role": "user", "content": h.content})
            elif h.role == "ai":
                self.history.append({"role": "assistant", "content": h.content})
        return history

    def invoke(self, query: str):
        self.get_history()
        system_message: ChatCompletionMessageParam = {
            "role": "system",
            "content": file.open_file(constant.SYSTEM_PROMPT),
        }
        user_message: ChatCompletionMessageParam = {"role": "user", "content": query}

        messages: Iterable[ChatCompletionMessageParam] = []
        messages.append(system_message)
        messages.extend(self.history)
        messages.append(user_message)

        stream = self.client.chat.completions.create(
            model=constant.GPTModel.GPT_4O_MINI,
            stream=True,
            messages=messages,
        )

        assistant_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                assistant_response += content
                yield content
            if chunk.choices[0].finish_reason == "stop":
                break

        self.memory.insert(
            [
                History(
                    resource_id=self.resource_id,
                    role="human",
                    content=query,
                ),
                History(
                    resource_id=self.resource_id,
                    role="ai",
                    content=assistant_response,
                ),
            ]
        )
