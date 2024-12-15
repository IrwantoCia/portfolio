import typer
from rich.console import Console
from .stdio.stdout import stream_output
from .openai.chat import test, voice_to_text, converse
from clicerin.helper import audio
from clicerin.tui import consultant

app = typer.Typer()


@app.command()
def show():
    console = Console()
    console.print("Ask (press Ctrl+D or Ctrl+Z on a new line to finish):")
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        console.print()
        pass

    q = "\n".join(lines)
    for chunk in test(q):
        if chunk is not None:
            stream_output(chunk, False)
    stream_output("", True)


@app.command()
def record():
    try:
        data, rate = audio.record()
        audio.save(data, rate)
    except Exception as e:
        print(e)


@app.command()
def play(sound: str):
    try:
        audio.play_audio(file_path=sound)
    except Exception as e:
        print(e)


@app.command()
def transcript(sound: str):
    try:
        voice_to_text(sound)
    except Exception as e:
        print(e)


@app.command()
def talk():
    try:
        data, rate = audio.record()
        base64 = audio.audio_to_base_64(data, rate)
        result = converse(base64)
        # audio.play_audio_base_64(result)

    except Exception as e:
        print(e)


@app.command()
def consult():
    try:
        consultant.app.run()
    except Exception:
        pass
