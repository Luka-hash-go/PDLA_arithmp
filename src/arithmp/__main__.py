"""Arithmp: Command-line interface for the Arithmp package."""

from pathlib import Path
import sys
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
    
    if command:
        try:
            if (result := parser.parse(None, command)) is not None:
                click.echo(result)
        except ParserException as e:
            click.echo(f"Error : {e}")
            
    elif filepath:
        try:
            if (result := parser.parse(filepath, filepath.read_text())) is not None:
                click.echo(result)
        except ParserException as e:
            click.echo(f"Error in script '{filepath}': {e}")
            
    else:
        click.echo("Interpréteur Arithmp (Ctrl+C pour quitter)")
        while True:
            try:
                expr = input("> ")
                if not expr.strip():
                    continue
                if (result := parser.parse(None, expr)) is not None:
                    click.echo(result)
            except ParserException as e:
                click.echo(f"Error : {e}")
            except (KeyboardInterrupt, EOFError):
                click.echo("\nAu revoir !")
                sys.exit(0)

if __name__ == "__main__":
    main()