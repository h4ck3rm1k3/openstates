
import pprint
import sys

sys.path.insert(0, "/home/mdupont/experiments/sunlight/scrapelib/")

import scrapelib
pp = pprint.PrettyPrinter(indent=4)
import scrapelib
s = scrapelib.Scraper(requests_per_minute=10,
                      follow_robots=True)

errors = 0
index = 12345984343434
try:
    url = ("http://open.nysenate.gov/legislation/search/"
           "?search=otype:bill&searchType=&format=xml"
           "&pageIdx=%d" % index)
    with s.urlopen(url) as page:
        print page

except scrapelib.HTTPError as e:
    print "response.status_code:%s" % e.response.status_code
    code = e.response.status_code
    if code == 404:
        errors += 1
    elif code == 500:
        errors += 1
    else:
        raise
