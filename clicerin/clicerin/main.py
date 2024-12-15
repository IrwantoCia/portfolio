import typer

from .version import app as version_app
from .stream import app as stream_app

app = typer.Typer()

app.add_typer(version_app)
app.add_typer(stream_app)
