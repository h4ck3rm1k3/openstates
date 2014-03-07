import re
import datetime

from billy.scrape import NoDataForPeriod
from billy.scrape.events import Event, EventScraper

import pytz
import lxml.html

exclude_slugs = ["TBA"]
formats = [
    "%b %d %A %I:%M %p %Y",
    "%B %d %A %I:%M %p %Y"
]

replacements = {
    "Sept": "Sep"
}

now = datetime.datetime.now()


class AKEventScraper(EventScraper):
    jurisdiction = 'ak'

    _tz = pytz.timezone('US/Alaska')

    def scrape(self, chamber, session):
        if session != '28':
            raise NoDataForPeriod(session)

        if chamber == 'other':
            return

        year = now.year

        # Full calendar year
        date1 = '0101' + str(year)[2:]
        date2 = '1231' + str(year)[2:]

        url = ("http://www.legis.state.ak.us/basis/"
               "get_hearing.asp?session=%s&Chamb=B&Date1=%s&Date2=%s&"
               "Comty=&Root=&Sel=1&Button=Display" % (
                   session, date1, date2))

        page = self.urlopen(url)
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        path = "//font[starts-with(., '(H)') or starts-with(., '(S)')]"
        for font in page.xpath(path):
            match = re.match(r'^\((H|S)\)(.+)$', font.text)

            chamber = {'H': 'lower', 'S': 'upper'}[match.group(1)]
            comm = match.group(2).strip().title()

            next_row = font.xpath("../../following-sibling::tr[1]")[0]

            when = next_row.xpath("string(td[1]/font)").strip()
            when = re.sub("\s+", " ", when)
            when = "%s %s" % (when, year)

            continu = False
            for slug in exclude_slugs:
                if slug in when:
                    continu = True

            for repl in replacements:
                if repl in when:
                    when = when.replace(repl, replacements[repl])

            if continu:
                continue

            parsed_when = None
            for fmt in formats:
                try:
                    parsed_when = datetime.datetime.strptime(when, fmt)
                    break
                except ValueError:
                    pass

            if not parsed_when:
                raise

            when = parsed_when
            if when < now:
                self.warning("Dropping an event at %s. Be careful!" % (
                    when
                ))
                continue

            when = self._tz.localize(when)

            where = next_row.xpath("string(td[2]/font)").strip()

            description = "Committee Meeting\n"
            description += comm

            links = font.xpath(
                "../../td/font/a[contains(@href, 'get_documents')]")
            if links:
                agenda_link = links[0]
                event['link'] = agenda_link.attrib['href']

            cur_node = font.getparent().getparent()
            bills = []
            while cur_node is not None and cur_node.xpath(".//hr") == []:
                bills += cur_node.xpath(
                    ".//a[contains(@href, 'get_complete_bill')]/text()")
                cur_node = cur_node.getnext()

            event = Event(session, when, 'committee:meeting',
                          description, location=where)

            event.add_source(url)
            for bill in bills:
                event.add_related_bill(bill,
                                       description='Related Bill',
                                       type='consideration')

            event.add_participant('host',
                                  comm,
                                  participant_type='committee',
                                  chamber=chamber)
            self.save_event(event)
