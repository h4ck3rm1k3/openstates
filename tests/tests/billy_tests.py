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


class TestBilly(unittest.TestCase):

    def test_sessions(self):

        metadata = {
            'session_details': {
                "2012": {"_scraped_name": "2012"},
                "2013": {"_scraped_name": "2013"},
            },
            'terms':
            [
                {
                    "name": "2012",
                    "sessions": ['2012', '2013']
                }
            ]
        }

        obj = {}
        chamber = "lower"
        time = "2012"
        sessions = [
            "2012"
        ]

        billy.scrape.check_sessions(metadata, sessions)

    def runTest(self):
        self.test_sessions()


suite = TestBilly

if __name__ == "__main__":
    t = TestBilly()
    t.runTest()
