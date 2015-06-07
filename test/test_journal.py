import os
import json
import unittest
from nose.tools import assert_equal

from journal import Journal, time_parse

DIR = os.path.dirname(os.path.abspath(__file__))


def test_time_parse():
    assert_equal(time_parse("16:40"), 1000)
    assert_equal(time_parse("116:40"), 7000)
    assert_equal(time_parse("5:20"), 320)


class TestJournal(unittest.TestCase):
    def setUp(self):
        self.race = json.load(open(os.path.join(DIR, 'race.json')))
        self.sample_path = os.path.join(DIR, 'sample.json')
        self.journal = Journal(self.sample_path)

    def tearDown(self):
        os.remove(self.sample_path)

    def test__load(self):
        self.assertEqual(self.journal.data, {"races": []}, "Journal should initialize empty")

    def test_add(self):
        for j in range(10):
            self.journal.add(self.race)
            self.assertEqual(len(self.journal.races), j + 1)

    def test_save(self):
        num_races = 10
        for j in range(num_races):
            self.journal.add(self.race)
        new_journal = Journal(self.sample_path)
        self.assertListEqual(new_journal.races, self.journal.races,
                             "A new journal should contain all races the old one did")

    def test_existing_ids(self):
        existing_ids = self.journal.existing_ids()
        new_id = self.journal.add(self.race)
        self.assertTrue(new_id not in existing_ids, "Adding a race should add a unique id")
        self.assertTrue(new_id in self.journal.existing_ids(),
                        "The new id should now be in existing_ids")

    def test_read(self):
        funky_race = dict(self.race.items()[:])
        funky_race["name"] = "This race was pretty funky"
        new_id = self.journal.add(funky_race)
        recovered_race = self.journal.read(new_id)
        for key, value in funky_race.iteritems():
            self.assertEqual(value, recovered_race.get(key))

        self.assertEqual(self.journal.read(-1), {},
                         "Ids are positive, non reasonable ids return empty")

    def test_update(self):
        fun_fields = {"foo": "bar", "new stuff": "wooo", "name": "update old stuff"}
        new_id = self.journal.add(self.race)
        race_v1 = self.journal.read(new_id)
        for key, value in fun_fields.iteritems():
            self.assertNotEqual(value, race_v1.get(key), "Fields aren't in race yet")
        race_v2 = self.journal.update(new_id, fun_fields)
        race_v3 = self.journal.read(new_id)
        for key, value in fun_fields.iteritems():
            self.assertEqual(value, race_v2.get(key), "Fields are in race now")
            self.assertEqual(value, race_v3.get(key), "Even if we ask for a new copy")

    def test_delete(self):
        new_id = self.journal.add(self.race)
        self.assertTrue(new_id in self.journal.existing_ids())
        self.journal.delete(new_id)
        self.assertFalse(new_id in self.journal.existing_ids())
