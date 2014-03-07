import re
import datetime

from billy.scrape.committees import CommitteeScraper, Committee

import lxml.html


class NVCommitteeScraper(CommitteeScraper):
    jurisdiction = 'nv'

    def scrape(self, chamber, term):

        for t in self.metadata['terms']:
            if t['name'] == term:
                session = t['sessions'][-1]

        sessionsuffix = 'th'
        if str(session)[-1] == '1':
            sessionsuffix = 'st'
        elif str(session)[-1] == '2':
            sessionsuffix = 'nd'
        elif str(session)[-1] == '3':
            sessionsuffix = 'rd'
        insert = str(session) + sessionsuffix + str(term[0:4])

        chamber_letter = {'lower': 'A', 'upper': 'S'}[chamber]

        url = 'http://www.leg.state.nv.us/Session/%s/Committees/%s_Committees/' % (
            insert, chamber_letter)

        page = self.urlopen(url)
        root = lxml.html.fromstring(page)
        for com_a in root.xpath('//strong/a'):
            com_url = url + com_a.get('href')
            if com_a.text == 'Committee of the Whole':
                continue
            com = Committee(chamber, com_a.text)
            com.add_source(com_url)
            self.scrape_comm_members(chamber, com, com_url)
            self.save_committee(com)

    def scrape_comm_members(self, chamber, committee, url):
        html = self.urlopen(url)
        doc = lxml.html.fromstring(html)
        for li in doc.xpath('//li'):
            pieces = li.text_content().split(' - ')
            name = pieces[0].strip()
            role = pieces[1] if len(pieces) == 2 else 'member'
            committee.add_member(name, role)
