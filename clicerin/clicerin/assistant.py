import typer
from clicerin.ai.chat import voice_to_text
from clicerin.tui import consultant

app = typer.Typer()


@app.command()
def transcribe(sound: str):
    try:
        voice_to_text(sound)
    except Exception as e:
        print(e)


@app.command()
def ai():
    try:
        consultant.app.run()
    except Exception:
        pass
