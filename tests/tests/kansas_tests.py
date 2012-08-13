import unittest
#import random
#import unittest
import logging
#import traceback
import openstates.ks.action_codes_scrape
import openstates.ks.bills
import openstates.ks.committees
import openstates.ks.legislators
import lxml.etree
import billy.scrape.utils
import openstates.ks.ksapi

# code snippet, to be included in 'sitecustomize.py'
import sys


def info(type, value, tb):
    print "except hook"
    sys.__excepthook__(type, value, tb)

sys.excepthook = info
from openstates.ks.bills import KSBillScraper

format = (
    "TEST:%(pathname)s %(asctime)s %(name)s %(levelname)s"
    " %(funcName)s %(lineno)d %(message)s")
logging.basicConfig(level=logging.DEBUG, format=format, datefmt="%H:%M:%S")
_log = logging.getLogger("billy")
_log.warn("starting")


class TestKansas(unittest.TestCase):

    def test_session_list(self):
        slug = []  # b2011_12
        try:
            xpathbase = billy.scrape.utils.url_xpath(
                openstates.ks.ksapi.ksleg,
                '//a[contains(text(), "Senate Bills")]/@href')
        except lxml.etree.XMLSyntaxError as e:
            _log.debug("syntax error :%s" % e)
            return [slug]

        if (len(xpathbase) < 1):
            _log.debug(xpathbase)
            _log.debug("No XPATH data")
        else:

            _log.debug(len(xpathbase))
            _log.debug(xpathbase)
            url = xpathbase[0]

            if (url is None):
                _log.debug("No URL")
            else:
                parts = url.split('/')
                if parts is None:
                    _log.debug("No PARTS in %s" % url)

                if len(parts) > 1:
                    slug = parts[2]  # b2011_12
                    _log.debug("found slug %s" % slug)
                else:
                    _log.debug("Not enough parts in %s" % url)

    def test_metadata(self):
        metadata = {
            'terms':
            [
                {
                    "name": "2012",
                    "sessions": ['2012', '2013']
                }
            ]
        }
        return metadata

    def test_bills(self):
        metadata = self.test_metadata()
        #obj = {}
        chamber = "lower"
        time = "2012"
        bs = openstates.ks.bills.KSBillScraper(metadata, output_dir="/tmp")
        bs.scrape(chamber, time)

    def test_committees(self):
        metadata = self.test_metadata()
        chamber = "house"
        time = "2012"
        c = openstates.ks.committees.KSBillScraper(metadata, output_dir="/tmp")
        f = open('tests/tests/kansas_bill_status.json')
        d = f.read()
        c._scrape_data(chamber, time, d)

    def test_committees2(self):
        metadata = self.test_metadata()
        chamber = "house"
        time = "2012"
        c = openstates.ks.committees.KSBillScraper(metadata, output_dir="/tmp")
        c.scrape(chamber, time)

    def test_legislators(self):
        metadata = self.test_metadata()
        chamber = "house"
        time = "2012"
        c = openstates.ks.legislators.KSLegislatorScraper(
            metadata, output_dir="/tmp")
        c.scrape(chamber, time)

    def parse_action_codes(self):
        openstates.ks.action_codes_scrape.parse_action_codes(
            'openstates/ks/action_codes')
#        print openstates.ks.action_codes_scrape.voted_codes
#        print openstates.ks.action_codes_scrape.passed_codes
#        print openstates.ks.action_codes_scrape.failed_codes
#        print openstates.ks.action_codes_scrape.numbers
        print openstates.ks.action_codes_scrape.new_numbers

    def runTest(self):
        print "Hello"
        self.test_session_list()
        self.test_committees()
        self.test_legislators()
        self.test_bills()
        self.parse_action_codes()


# action_codes_scrape.py

suite = TestKansas

if __name__ == "__main__":
    t = TestKansas()
    t.runTest()
