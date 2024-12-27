import typer
from clicerin.tui import consultant

app = typer.Typer()


@app.command()
def ai():
    try:
        consultant.app.run()
    except Exception:
        pass
