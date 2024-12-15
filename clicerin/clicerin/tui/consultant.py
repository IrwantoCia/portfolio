from textual.app import App, ComposeResult
from textual.widgets import (
    Button,
    Header,
    Footer,
    Rule,
    Static,
    Markdown,
    TextArea,
    Label,
)
from textual.containers import VerticalScroll, Container

import asyncio

from clicerin.helper import db
from clicerin.openai import chat


class ConsultApp(App):
    """A Textual app for AI Chat."""

    CSS_PATH = "./consultant.tcss"

    def __init__(self):
        super().__init__()
        self.stream_task = None
        self.db = db.DatabaseManager()
        self.chats = ""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with Container(id="app-grid"):
            with Container(id="chat-pane"):
                with VerticalScroll(id="markdown-content"):
                    pass

                with VerticalScroll(classes="input-container"):
                    yield Static("Input", id="input_label", classes="input_label")
                    self.chat_input = TextArea(id="chat-input")
                    self.chat_input.focus()
                    yield self.chat_input

                with Container(classes="button-container"):
                    self.send_button = Button("Send", id="send-button")
                    self.stop_button = Button("Stop", id="stop-button")
                    yield self.send_button
                    yield self.stop_button

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "send-button":
            self.on_send_button()

        elif event.button.id == "stop-button" and self.stream_task:
            self.on_stop_button()

    def on_send_button(self):
        self.char_index = 0
        self.current_chat = ""

        md = Markdown()
        chat_pane = self.query_one("#markdown-content")

        q = self.chat_input.text
        self.current_chat += "### "  # markdown header
        self.current_chat += q.strip()
        self.current_chat += "\n---\n"  # markdown horizontal rule

        chat_pane.mount(Rule(line_style="blank"))
        chat_pane.mount(md)

        async def process_chunks():
            try:
                for chunk in chat.test(q):
                    if chunk is not None:
                        self.current_chat += chunk
                        await md.update(self.current_chat)
                        chat_pane.scroll_end(force=True)

            except asyncio.CancelledError:
                pass

        self.stream_task = asyncio.create_task(process_chunks())

        # self.db.insert_chat(
        #    db.Chat(
        #        id=None,
        #        model="gpt",
        #        question=self.chat_input.text,
        #        response=self.buffer,
        #        token=0,
        #        created_at=datetime.datetime.now(),
        #    )
        # )

        self.chat_input.clear()
        self.chat_input.focus()

    def on_stop_button(self):
        if self.stream_task:
            self.stream_task.cancel()
            self.stream_task = None


app = ConsultApp()
