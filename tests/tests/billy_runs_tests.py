import unittest
import random
import unittest
import logging
import traceback
import billy.scrape

format = (
    "TEST:%(pathname)s %(asctime)s %(name)s %(levelname)s %(funcName)s %(lineno)d %(message)s")
logging.basicConfig(level=logging.DEBUG, format=format, datefmt="%H:%M:%S")
_log = logging.getLogger("billy")
_log.warn("starting")

from billy import db


class TestBillyRuns(unittest.TestCase):

    def test_data(self):

        try:
            scrape_data = ""
            db.billy_runs.save(scrape_data, safe=True)
        except TypeError as e:
            print e

        try:
            scrape_data = {}
            db.billy_runs.save(scrape_data, safe=True)
        except TypeError as e:
            print e

    def runTest(self):
        self.test_data()

suite = TestBillyRuns

if __name__ == "__main__":
    t = TestBillyRuns()
    t.runTest()
