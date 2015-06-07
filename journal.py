import os
import json
from dateutil import parser

import click


def time_parse(time_str):
    minutes, seconds = time_str.split(":")
    return 60 * int(minutes) + float(seconds)


class Journal(object):
    fields = (
        ("What was the name of the race?", "name", str),
        ("What date (YYYY-mm-dd) was the race?", "date", parser.parse),
        ("What city was the race held in?", "city", str),
        ("What state was the race held in?", "state", str),
        ("How long was the race (in meters)?" "distance", int),
        ("What was your time (MM:SS)?", "time", time_parse),
        ("What was your overall place?", "place_overall", int),
        ("Out of how many runners?", "runners_in_race", int),
        ("What was your age group place?", "place_ag", int),
        ("Out of how many runners in your age group?", "runners_in_ag", int),
        ("What is the url with results?", "results", str),
        ("Describe the race.", "notes", str)
        )

    def __init__(self, journal_path):
        self.journal_path = journal_path
        self.data = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.journal_path):
            self.data = {"races": []}
            self._save()
        else:
            with open(self.journal_path, 'r') as buff:
                self.data = json.load(buff)

    def _save(self):
        with open(self.journal_path, 'w') as buff:
            json.dump(self.data, buff)

    @property
    def races(self):
        return self.data["races"]

    def existing_ids(self):
        return set(race["id"] for race in self.races)

    def _get_id(self):
        new_id = 0
        existing_ids = self.existing_ids()
        while new_id in existing_ids:
            new_id += 1
        return new_id

    def add(self, race_data):
        race_data["id"] = self._get_id()
        self.races.append(race_data)
        self._save()
        return race_data["id"]

    def read(self, race_id):
        for race in self.races:
            if race["id"] == race_id:
                return race
        return {}

    def update(self, race_id, update_data):
        for race in self.races:
            if race["id"] == race_id:
                for key, value in update_data.iteritems():
                    race[key] = value
                self._save()
                return race
        return {}

    def delete(self, *race_ids):
        self.data["races"] = [race for race in self.races if race["id"] not in race_ids]
        self._save()

    def prompt(self):
        data = {j[1]: None for j in self.fields}
        while True:
            for prompt, field, func in self.fields:
                if data[field]:
                    user_input = raw_input("{} ({})".format(prompt, data[field]))
                else:
                    user_input = raw_input(prompt)
                if user_input == "":
                    data[field] = None
                else:
                    data[field] = func(user_input)
            for _, field, _ in self.fields:
                print("{}: {}".format(field, data[field]))
            is_ok = raw_input("Does that look ok [Y] or would you like to try again [N]?")
            if is_ok != "Y":
                break
        return self.add(data)

    def list(self):
        races = sorted(self.races, key=lambda j: j["date"])
        for race in races:
            print(race["name"])


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
