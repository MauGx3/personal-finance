"""Command-line interface."""

import typer


app: typer.Typer = typer.Typer()


@app.command(name="robust_python")
def main() -> None:
    """robust_python."""


if __name__ == "__main__":
    app()  # pragma: no cover
