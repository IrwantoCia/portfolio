from rich.console import Console
from rich.markdown import Markdown
from rich.live import Live
import time

content = ""
console = Console()
live = Live(console=console, vertical_overflow="visible")


def stream_output(chunk: str, done: bool = False) -> None:
    """Stream markdown content using Rich.

    Args:
        chunk (str): Markdown formatted text chunk to append and display
        done (bool): Flag indicating if this is the final chunk
    """
    global content, live

    content += chunk

    if not live.is_started:
        live.start()

    md = Markdown(content, code_theme="github-dark")
    live.update(md)
    time.sleep(0.1)

    if done:
        live.stop()
        content = ""
        console.print()  # Add newline at the end
