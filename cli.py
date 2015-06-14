import click

from racedb import RaceDB


@click.group()
def cli():
    """This is a user interface to interact with a race database and output json."""


@cli.command("add")
@click.option("--filename", help="Which data file to use.")
def interact_with_db(filename):
    RaceDB(filename).prompt()


@cli.command("list")
@click.option("--filename", default=None, help="Which data file to use.")
@click.option("-s", "--search", default='', help="Filter list by search.", type=click.STRING)
def list_db(filename, search):
    RaceDB(filename).list(search)


@cli.command("edit")
@click.option("--filename", default=None, help="Which data file to use.")
@click.option("--race-id",
              required=True, help="Race id to edit.  Use 'list' to view ids.", type=click.INT)
def edit_db(filename, race_id):
    RaceDB(filename).update_prompt(race_id)


@cli.command("view")
@click.option("--filename", default=None, help="Which data file to use.")
@click.option("--race-id",
              required=True, help="Race id to view.  Use 'list' to view ids.", type=click.INT)
def view_db(filename, race_id):
    race_id = int(race_id)
    db = RaceDB(filename)
    db.print_race(db.read(race_id))


@cli.command("copy")
@click.option("--filename", default=None, help="Which data file to use.")
@click.option("-d", "--dest",
              required=True, help="Where to copy the race data to", type=click.Path())
def copy_db(filename, dest):
    RaceDB(filename).copy(dest)
