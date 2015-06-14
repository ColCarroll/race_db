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
@click.option("--filename", default=None, help="Which data file to use.")
@click.option("-s", "--search", default='', help="Filter list by search.", type=click.STRING)
def list_journal(filename, search):
    Journal(filename).list(search)


@cli.command("edit")
@click.option("--filename", default=None, help="Which data file to use.")
@click.option("--race-id",
              required=True, help="Race id to edit.  Use 'list' to view ids.", type=click.INT)
def edit_journal(filename, race_id):
    Journal(filename).update_prompt(race_id)


@cli.command("view")
@click.option("--filename", default=None, help="Which data file to use.")
@click.option("--race-id",
              required=True, help="Race id to view.  Use 'list' to view ids.", type=click.INT)
def view_journal(filename, race_id):
    race_id = int(race_id)
    journal = Journal(filename)
    journal.print_race(journal.read(race_id))


@cli.command("copy")
@click.option("--filename", default=None, help="Which data file to use.")
@click.option("-d", "--dest",
              required=True, help="Where to copy the journal data to", type=click.Path())
def copy_journal(filename, dest):
    Journal(filename).copy(dest)
