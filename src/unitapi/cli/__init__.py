import click
from .dsl_commands import dsl


@click.group()
def cli():
    """UnitAPI Command Line Interface"""
    pass


# Add DSL commands
cli.add_command(dsl)


# Entry point for the CLI
def main():
    """Main entry point for the CLI"""
    cli()


if __name__ == "__main__":
    main()
