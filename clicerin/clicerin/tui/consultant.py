from textual.app import App, ComposeResult
from textual.widgets import (
    Button,
    Header,
    Footer,
    Rule,
    Static,
    Markdown,
    TextArea,
)
from textual.containers import VerticalScroll, Container

import asyncio

from ..helper import audio
from ..ai import chatx, voicex


class ConsultApp(App):
    """A Textual app for AI Chat."""

    CSS_PATH = "./consultant.tcss"

    def __init__(self):
        super().__init__()
        self.stream_task = None
        self.audioRecorder = audio.AudioRecorder()
        self.chatx = chatx.Chatx(resource_id="1")
        self.voicex = voicex.Voicex()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        with VerticalScroll(id="app-grid"):
            with Container(id="chat-pane"):
                with VerticalScroll(id="markdown-content"):
                    content = ""
                    for h in self.chatx.get_history():
                        if h.role == "ai":
                            content += h.content
                            md = Markdown(content)
                            yield md
                        elif h.role == "human":
                            content = "### "  # markdown header
                            content += h.content
                            content += "\n---\n"  # markdown horizontal rule
                            yield Rule(line_style="blank")

                with VerticalScroll(classes="input-container"):
                    yield Static("Input", id="input_label", classes="input_label")
                    self.chat_input = TextArea(id="chat-input")
                    self.chat_input.focus()
                    yield self.chat_input

                with Container(classes="button-container"):
                    self.send_button = Button("Send", id="send-button")
                    self.stop_button = Button("Stop", id="stop-button")
                    self.voice_button = Button("Voice", id="voice-button")
                    yield self.send_button
                    yield self.stop_button
                    yield self.voice_button

        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press events."""
        if event.button.id == "send-button":
            self.on_send_button()

        elif event.button.id == "stop-button" and self.stream_task:
            self.on_stop_button()
        elif event.button.id == "voice-button":
            self.on_voice_button()

    def on_voice_button(self):
        self.audioRecorder.recording = not self.audioRecorder.recording
        if self.audioRecorder.recording:
            self.voice_button.label = "Recording..."
            self.audioRecorder.record()
        else:
            self.voice_button.label = "Record"
            self.audioRecorder.stop_recording()

            base64 = audio.audio_to_base_64(
                self.audioRecorder.audio_data, self.audioRecorder.sample_rate
            )
            self.voicex.invoke(base64)

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
                for chunk in self.chatx.invoke(q):
                    if chunk is not None:
                        self.current_chat += chunk
                        await md.update(self.current_chat)
                        chat_pane.scroll_end(force=True)

            except asyncio.CancelledError:
                pass

        self.stream_task = asyncio.create_task(process_chunks())

        self.chat_input.clear()
        self.chat_input.focus()

    def on_stop_button(self):
        if self.stream_task:
            self.stream_task.cancel()
            self.stream_task = None


app = ConsultApp()
