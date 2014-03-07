import re
import socket
import datetime
from operator import methodcaller
import htmlentitydefs

import lxml.html

from billy.scrape.bills import BillScraper, Bill
from billy.scrape.votes import Vote

from .actions import Categorizer


strip = methodcaller('strip')


def unescape(text):
    '''Removes HTML or XML character references and entities
    from a text string.

    @param text The HTML (or XML) source text.
    @return The plain text, as a Unicode string, if necessary.

    Source: http://effbot.org/zone/re-sub.htm#unescape-html'''

    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text  # leave as is
    return re.sub("&#?\w+;", fixup, text)


class BillNotFound(Exception):

    'Raised if bill is not found on their site.'


class MEBillScraper(BillScraper):
    jurisdiction = 'me'
    categorizer = Categorizer()

    def scrape(self, chamber, session):
        if session[-1] == "1":
            session_abbr = session + "st"
        elif session[-1] == "2":
            session_abbr = session + "nd"
        elif session[-1] == "3":
            session_abbr = session + "rd"
        else:
            session_abbr = session + "th"

        self.scrape_session(session, session_abbr, chamber)

    def scrape_session(self, session, session_abbr, chamber):
        url = ('http://www.mainelegislature.org/legis/bills/bills_%s'
               '/billtexts/' % session_abbr)

        page = self.urlopen(url, retry_on_404=True)
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for link in page.xpath('//a[contains(@href, "contents")]/@href'):
            self.scrape_session_directory(session, chamber, link)

    def scrape_session_directory(self, session, chamber, url):
        # decide xpath based on upper/lower
        link_xpath = {'lower': '//big/a[starts-with(text(), "HP")]',
                      'upper': '//big/a[starts-with(text(), "SP")]'}[chamber]

        page = self.urlopen(url, retry_on_404=True)
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for link in page.xpath(link_xpath):
            bill_id = link.text
            title = link.xpath("string(../../following-sibling::dd[1])")

            # A temporary hack to add one particular title that's missing
            # on the directory page.
            if len(title) == 0:
                if session == '125' and bill_id == 'SP0681':
                    msg = 'Adding hard-coded title for bill_id %r'
                    self.warning(msg % bill_id)
                    title = ('An Act To Simplify the Certificate of Need '
                             'Process and Lessen the Regulatory Burden on'
                             ' Providers')

            if not title:
                title = '[Title not available]'

            if (title.lower().startswith('joint order') or
                    title.lower().startswith('joint resolution')):
                bill_type = 'joint resolution'
            else:
                bill_type = 'bill'

            bill = Bill(session, chamber, bill_id, title, type=bill_type)
            try:
                self.scrape_bill(bill, link.attrib['href'])
            except BillNotFound:
                continue
            else:
                self.save_bill(bill)

    def scrape_bill(self, bill, url):
        session_id = (int(bill['session']) - 124) + 8
        url = ("http://www.mainelegislature.org/LawMakerWeb/summary.asp"
               "?paper=%s&SessionID=%d" % (bill['bill_id'], session_id))
        html = self.urlopen(url, retry_on_404=True)
        page = lxml.html.fromstring(html)
        page.make_links_absolute(url)

        # Add the LD number in.
        for ld_num in page.xpath("//b[contains(text(), 'LD ')]/text()"):
            if re.search(r'LD \d+', ld_num):
                bill['ld_number'] = ld_num

        if 'Bill not found.' in html:
            self.warning('%s returned "Bill not found." page' % url)
            raise BillNotFound

        bill.add_source(url)

        # Add bill sponsors.
        try:
            xpath = '//a[contains(@href, "sponsors")]/@href'
            sponsors_url = page.xpath(xpath)[0]
        except IndexError:
            msg = ('Page didn\'t contain sponsors url with expected '
                   'format. Page url was %s' % url)
            raise ValueError(msg)
        sponsors_html = self.urlopen(sponsors_url, retry_on_404=True)
        sponsors_page = lxml.html.fromstring(sponsors_html)
        sponsors_page.make_links_absolute(sponsors_url)

        tr_text = sponsors_page.xpath('//tr')
        tr_text = [tr.text_content() for tr in tr_text]
        rgx = '(Speaker|President|Senator|Representative) ([A-Z ]+)'
        for text in tr_text:
            text = str(text)

            if 'the Majority' in text:
                # At least one bill was sponsored by 'the Majority'.
                bill.add_sponsor('primary', 'the Majority',
                                 chamber=bill['chamber'])
                continue

            if text.lower().startswith('sponsored by:'):
                type_ = 'primary'
            elif 'introduc' in text.lower():
                type_ = 'primary'
            elif text.lower().startswith('cosponsored by:'):
                type_ = 'cosponsor'
            else:
                continue

            for match in re.finditer(rgx, text):
                chamber_title, name = map(strip, match.groups())
                if chamber_title in ['President', 'Speaker']:
                    chamber = bill['chamber']
                else:
                    chamber = {'Senator': 'upper',
                               'Representative': 'lower'}
                    chamber = chamber[chamber_title]
                bill.add_sponsor(type_.lower(), name.strip(), chamber=chamber)

        bill.add_source(sponsors_url)

        docket_link = page.xpath("//a[contains(@href, 'dockets.asp')]")[0]
        self.scrape_actions(bill, docket_link.attrib['href'])

        # Add signed by guv action.
        if page.xpath('//b[contains(text(), "Signed by the Governor")]'):
            date = page.xpath(
                ('string(//td[contains(text(), "Date")]/'
                 'following-sibling::td/b/text())'))
            dt = datetime.datetime.strptime(date, "%m/%d/%Y")
            bill.add_action(
                action="Signed by Governor", date=dt,
                actor="governor", type=["governor:signed"])

        xpath = "//a[contains(@href, 'rollcalls.asp')]"
        votes_link = page.xpath(xpath)[0]
        self.scrape_votes(bill, votes_link.attrib['href'])

        spon_link = page.xpath("//a[contains(@href, 'subjects.asp')]")[0]
        spon_url = spon_link.get('href')
        bill.add_source(spon_url)
        spon_html = self.urlopen(spon_url, retry_on_404=True)
        sdoc = lxml.html.fromstring(spon_html)
        xpath = '//table[@class="sectionbody"]/tr[2]/td/text()'
        srow = sdoc.xpath(xpath)[1:]
        if srow:
            bill['subjects'] = [s.strip() for s in srow if s.strip()]

        ver_link = page.xpath("//a[contains(@href, 'display_ps.asp')]")[0]
        ver_url = ver_link.get('href')
        try:
            ver_html = self.urlopen(ver_url, retry_on_404=True)
        except socket.timeout:
            pass
        else:
            if ver_html:
                vdoc = lxml.html.fromstring(ver_html)
                vdoc.make_links_absolute(ver_url)
                # various versions: billtexts, billdocs, billpdfs
                vurl = vdoc.xpath('//a[contains(@href, "billtexts/")]/@href')
                if vurl:
                    bill.add_version('Initial Version', vurl[0],
                                     mimetype='text/html')

    def scrape_votes(self, bill, url):
        page = self.urlopen(url, retry_on_404=True)
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        path = "//div/a[contains(@href, 'rollcall.asp')]"
        for link in page.xpath(path):
            # skip blank motions, nothing we can do with these
            # seen on /LawMakerWeb/rollcalls.asp?ID=280039835
            if link.text:
                motion = link.text.strip()
                url = link.attrib['href']

                self.scrape_vote(bill, motion, url)

    def scrape_vote(self, bill, motion, url):
        page = self.urlopen(url, retry_on_404=True)
        page = lxml.html.fromstring(page)

        yeas_cell = page.xpath("//td[text() = 'Yeas (Y):']")[0]
        yes_count = int(yeas_cell.xpath("string(following-sibling::td)"))

        nays_cell = page.xpath("//td[text() = 'Nays (N):']")[0]
        no_count = int(nays_cell.xpath("string(following-sibling::td)"))

        abs_cell = page.xpath("//td[text() = 'Absent (X):']")[0]
        abs_count = int(abs_cell.xpath("string(following-sibling::td)"))

        ex_cell = page.xpath("//td[text() = 'Excused (E):']")[0]
        ex_count = int(ex_cell.xpath("string(following-sibling::td)"))

        other_count = abs_count + ex_count

        if 'chamber=House' in url:
            chamber = 'lower'
        elif 'chamber=Senate' in url:
            chamber = 'upper'

        date_cell = page.xpath("//td[text() = 'Date:']")[0]
        date = date_cell.xpath("string(following-sibling::td)")
        try:
            date = datetime.datetime.strptime(date, "%B %d, %Y")
        except ValueError:
            date = datetime.datetime.strptime(date, "%b. %d, %Y")

        outcome_cell = page.xpath("//td[text()='Outcome:']")[0]
        outcome = outcome_cell.xpath("string(following-sibling::td)")

        vote = Vote(chamber, date, motion,
                    outcome == 'PREVAILS',
                    yes_count, no_count, other_count)
        vote.add_source(url)

        member_cell = page.xpath("//td[text() = 'Member']")[0]
        for row in member_cell.xpath("../../tr")[1:]:
            name = row.xpath("string(td[2])")
            # name = name.split(" of ")[0]

            vtype = row.xpath("string(td[4])")
            if vtype == 'Y':
                vote.yes(name)
            elif vtype == 'N':
                vote.no(name)
            elif vtype == 'X' or vtype == 'E':
                vote.other(name)

        bill.add_vote(vote)

    def scrape_actions(self, bill, url):
        page = self.urlopen(url, retry_on_404=True)
        page = lxml.html.fromstring(page)
        bill.add_source(url)

        path = "//b[. = 'Date']/../../../following-sibling::tr"
        for row in page.xpath(path):
            date = row.xpath("string(td[1])")
            date = datetime.datetime.strptime(date, "%m/%d/%Y").date()

            chamber = row.xpath("string(td[2])").strip()
            if chamber == 'Senate':
                chamber = 'upper'
            elif chamber == 'House':
                chamber = 'lower'

            action = gettext(row[2])
            action = unescape(action).strip()

            actions = []
            for action in action.splitlines():
                action = re.sub(r'\s+', ' ', action)
                if not action or 'Unfinished Business' in action:
                    continue

                actions.append(action)

            for action in actions:
                attrs = dict(actor=chamber, action=action, date=date)
                attrs.update(self.categorizer.categorize(action))
                bill.add_action(**attrs)


def _get_chunks(el, buff=None, until=None):
    tagmap = {'br': '\n'}
    buff = buff or []

    # Tag, text, tail, recur...
    yield tagmap.get(el.tag.lower(), '')
    yield el.text or ''
    # if el.text == until:
    #     return
    for kid in el:
        for text in _get_chunks(kid):
            yield text
            # if text == until:
            #     return
    if el.tail:
        yield el.tail
        # if el.tail == until:
        #     return
    if el.tag == 'text':
        yield '\n'


def gettext(el):
    '''Join the chunks, then split and rejoin to normalize the whitespace.
    '''
    return ''.join(_get_chunks(el))
