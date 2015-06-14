import logging
import os
import json
import shutil
from dateutil import parser

import click


def time_parse(time_str):
    minutes, seconds = time_str.split(":")
    return 60 * int(minutes) + float(seconds)


def date_parse(date_str):
    return parser.parse(date_str).strftime("%Y-%m-%d")


class RaceDB(object):
    fields = (
        ("What was the name of the race?", "name", str),
        ("What date (YYYY-mm-dd) was the race?", "date", date_parse),
        ("What city was the race held in?", "city", str),
        ("What state was the race held in?", "state", str),
        ("How long was the race (in meters)?", "distance", int),
        ("What was your time (MM:SS)?", "time", time_parse),
        ("What was your overall place?", "place_overall", int),
        ("Out of how many runners?", "runners_in_race", int),
        ("What was your age group place?", "place_ag", int),
        ("Out of how many runners in your age group?", "runners_in_ag", int),
        ("What is the url with results?", "results", str),
        ("Describe the race.", "notes", str)
        )

    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.expanduser("~"), ".race_db.json")
        self.db_path = db_path
        self.data = {}
        self._load()

    def _load(self):
        if not os.path.exists(self.db_path):
            self.data = {"races": []}
            self._save()
        else:
            broken = False
            with open(self.db_path, 'r') as buff:
                try:
                    self.data = json.load(buff)
                except ValueError:
                    broken = True
            if broken:
                old_path = self.db_path + ".old"
                shutil.move(self.db_path, old_path)
                logging.warn("json was corrupted! Moved remains of old database to {} and started a new one!".format(old_path))
                self.data = {"races": []}
                self._save()

    def _save(self):
        with open(self.db_path, 'w') as buff:
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

    def prompt_loop(self, data):
        for prompt, field, func in self.fields:
            if data[field]:
                user_input = raw_input("{} ({})\n>> ".format(prompt, data[field]))
            else:
                user_input = raw_input("{}\n>> ".format(prompt))
            if user_input != "":
                data[field] = func(user_input)
        return data

    def prompt(self, data=None):
        if data is None:
            data = {j[1]: None for j in self.fields}
        while True:
            self.prompt_loop(data)
            self.print_race(data)
            is_ok = raw_input("Does that look ok [Y] or would you like to try again [N]?\n>> ")
            if is_ok == "Y":
                break
        return data

    def add_prompt(self):
        return self.add(self.prompt())

    def print_race(self, race):
        for _, field, _ in self.fields:
            click.echo("{}: {}".format(field, race.get(field)))

    def update_prompt(self, race_id):
        race_id = int(race_id)
        data = self.read(race_id)
        if data == {}:
            click.echo("Race not found.  Exiting.")
        else:
            return self.update(race_id, self.prompt(data))

    def list(self, search):
        races = sorted(self.races, key=lambda j: j["date"])
        if search is not None:
            races = [race for race in races if
                     str(search).lower() in " ".join(map(str, race.values())).lower()]
        keys = ["id", "date", "name", "city", "state"]
        print("\t".join(keys))
        for race in races:
            print("\t".join(map(str, [race[key] for key in keys])))

    def copy(self, other_path):
        shutil.copy(self.db_path, other_path)
