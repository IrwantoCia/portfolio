import typer

from .version import app as version_app
from .assistant import app as ai_app

app = typer.Typer()

app.add_typer(version_app)
app.add_typer(ai_app)
