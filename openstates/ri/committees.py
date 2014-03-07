import re
import urlparse
import datetime

from billy.scrape import NoDataForPeriod
from billy.scrape.committees import CommitteeScraper, Committee

import lxml.etree
import lxml.html

COMM_BLACKLIST = [
    "Constitutional and Regulatory Issues"
    # This page is timing out. This is most likely an issue with Upstream,
    # it seems to happen all over the place.
]


class RICommitteeScraper(CommitteeScraper):
    jurisdiction = 'ri'

    def scrape(self, chamber, term_name):
        self.validate_term(term_name, latest_only=True)

        if chamber == 'upper':
            self.scrape_senate_comm()
            # scrape joint committees under senate
            self.scrape_joint_comm()
        elif chamber == 'lower':
            self.scrape_reps_comm()

    def scrape_comm_list(self, ctype):
        url = 'http://webserver.rilin.state.ri.us/CommitteeMembers/'
        self.log("looking for " + ctype)
        page = self.urlopen(url)
        root = lxml.html.fromstring(page)
        return root.xpath("//a[contains(@href,'" + ctype + "')]")

    def add_members(self, comm, url):
        page = self.urlopen(url)
        self.log(comm)
        root = lxml.html.fromstring(page)
        # The first <tr> in the table of members
        membertable = root.xpath('//p[@class="style28"]/ancestor::table[1]')[0]
        members = membertable.xpath("*")[1:]

        order = {
            "name": 0,
            "appt": 1,
            "email": 2
        }

        prefix = "Senator"

        for member in members:
            name = member[order['name']].text_content().strip()
            if name[:len(prefix)] == prefix:
                name = name[len(prefix):].strip()
            appt = member[order['appt']].text_content().strip()
            self.log("name " + name + " role " + appt)
            comm.add_member(name, appt)

    def scrape_reps_comm(self):
        base = 'http://webserver.rilin.state.ri.us'

        linklist = self.scrape_comm_list('ComMemR')
        if linklist is not None:
            for a in linklist:
                link = a.attrib['href']
                commName = a.text
                url = base + link
                self.log("url " + url)
                c = Committee('lower', commName)
                self.add_members(c, url)
                c.add_source(url)
                self.save_committee(c)

    def scrape_senate_comm(self):
        base = 'http://webserver.rilin.state.ri.us'

        linklist = self.scrape_comm_list('ComMemS')
        if linklist is not None:
            for a in linklist:
                link = a.attrib['href']
                commName = a.text
                self.log(commName)
                if commName in COMM_BLACKLIST:
                    self.log("XXX: Blacklisted")
                    continue
                url = base + link
                self.log("url " + url)
                c = Committee('upper', commName)
                self.add_members(c, url)
                c.add_source(url)
                self.save_committee(c)

    def scrape_joint_comm(self):
        base = 'http://webserver.rilin.state.ri.us'

        linklist = self.scrape_comm_list('ComMemJ')
        if linklist is not None:
            for a in linklist:
                link = a.attrib['href']
                commName = a.text
                url = base + link
                self.log("url " + url)
                c = Committee('joint', commName)
                self.add_members(c, url)
                c.add_source(url)
                self.save_committee(c)
