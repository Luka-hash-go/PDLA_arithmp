"""Arithmp: Command-line interface for the Arithmp package."""

from pathlib import Path
import click
from .parser import Parser, ParserException

@click.command()
@click.option("-c", "command", type=str, help="Évalue directement l'expression donnée.")
@click.argument("filepath", type=click.Path(exists=True, path_type=Path), required=False)
def main(command: str | None, filepath: Path | None) -> None:
    """
    Main entry point for the Arithmp command-line interface.
    """
    parser = Parser()
    try:
        if command:
            if (result := parser.parse(None, command)) is not None:
                click.echo(result)
        elif filepath:
            if (result := parser.parse(filepath, filepath.read_text())) is not None:
                click.echo(result)
        else:
            click.echo("Usage : arithmp -c 'expression' ou arithmp <fichier>")
    except ParserException as e:
         click.echo(f"Error : {e}")

if __name__ == "__main__":
    main()
