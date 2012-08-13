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


class TestBillyDistricts(unittest.TestCase):

    def test_data(self):

        scrape_data = {
            u'name': u'40', u'chamber': u'upper', u'abbr': u'ks',
            u'boundary_id': u'sldu-ks-state-senate-district-40', u'num_seats': 1, '_id': u'ks-upper-40'}
        db.districts.save(scrape_data, safe=True)

    def runTest(self):
        self.test_data()

suite = TestBillyDistricts

if __name__ == "__main__":
    t = TestBillyDistricts()
    t.runTest()
