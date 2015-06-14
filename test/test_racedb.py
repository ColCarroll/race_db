import os
import json
import unittest
from nose.tools import assert_equal

from racedb import RaceDB, time_parse

DIR = os.path.dirname(os.path.abspath(__file__))


def test_time_parse():
    assert_equal(time_parse("16:40"), 1000)
    assert_equal(time_parse("116:40"), 7000)
    assert_equal(time_parse("5:20"), 320)


class TestRaceDB(unittest.TestCase):
    def setUp(self):
        self.race = json.load(open(os.path.join(DIR, 'race.json')))
        self.sample_path = os.path.join(DIR, 'sample.json')
        self.db = RaceDB(self.sample_path)

    def tearDown(self):
        os.remove(self.sample_path)

    def test__load(self):
        self.assertEqual(self.db.data, {"races": []}, "RaceDB should initialize empty")

    def test_add(self):
        for j in range(10):
            self.db.add(self.race)
            self.assertEqual(len(self.db.races), j + 1)

    def test_save(self):
        num_races = 10
        for j in range(num_races):
            self.db.add(self.race)
        new_db = RaceDB(self.sample_path)
        self.assertListEqual(new_db.races, self.db.races,
                             "A new database should contain all races the old one did")

    def test_existing_ids(self):
        existing_ids = self.db.existing_ids()
        new_id = self.db.add(self.race)
        self.assertTrue(new_id not in existing_ids, "Adding a race should add a unique id")
        self.assertTrue(new_id in self.db.existing_ids(),
                        "The new id should now be in existing_ids")

    def test_read(self):
        funky_race = dict(self.race.items()[:])
        funky_race["name"] = "This race was pretty funky"
        new_id = self.db.add(funky_race)
        recovered_race = self.db.read(new_id)
        for key, value in funky_race.iteritems():
            self.assertEqual(value, recovered_race.get(key))

        self.assertEqual(self.db.read(-1), {},
                         "Ids are positive, non reasonable ids return empty")

    def test_update(self):
        fun_fields = {"foo": "bar", "new stuff": "wooo", "name": "update old stuff"}
        new_id = self.db.add(self.race)
        race_v1 = self.db.read(new_id)
        for key, value in fun_fields.iteritems():
            self.assertNotEqual(value, race_v1.get(key), "Fields aren't in race yet")
        race_v2 = self.db.update(new_id, fun_fields)
        race_v3 = self.db.read(new_id)
        for key, value in fun_fields.iteritems():
            self.assertEqual(value, race_v2.get(key), "Fields are in race now")
            self.assertEqual(value, race_v3.get(key), "Even if we ask for a new copy")

    def test_delete(self):
        new_id = self.db.add(self.race)
        self.assertTrue(new_id in self.db.existing_ids())
        self.db.delete(new_id)
        self.assertFalse(new_id in self.db.existing_ids())
