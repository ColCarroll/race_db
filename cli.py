import click

from journal import Journal


@click.group()
def cli():
    """This is a user interface to interact with a race journal and output json."""


@cli.command("add")
@click.option("--filename", help="Which data file to use.")
def interact_with_journal(filename):
    Journal(filename).prompt()


@cli.command("list")
@click.option("--filename", help="Which data file to use.")
def list_journal(filename):
    Journal(filename).list()
