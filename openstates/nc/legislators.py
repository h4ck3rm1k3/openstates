from billy.scrape.legislators import LegislatorScraper, Legislator
import lxml.html

party_map = {'Dem': 'Democratic',
             'Rep': 'Republican',
             'Una': 'Unaffiliated'}


def get_table_item(doc, name):
    # get span w/ item
    span = doc.xpath('//span[text()="{0}"]'.format(name))[0]
    # get neighboring td's span
    dataspan = span.getparent().getnext().getchildren()[0]
    if dataspan.text:
        return (dataspan.text + '\n' +
                '\n'.join([x.tail for x in dataspan.getchildren()])).strip()
    else:
        return None


class NCLegislatorScraper(LegislatorScraper):
    jurisdiction = 'nc'

    def scrape(self, term, chambers):
        for chamber in chambers:
            self.scrape_chamber(chamber, term)

    def scrape_chamber(self, chamber, term):
        url = "http://www.ncga.state.nc.us/gascripts/members/"\
            "memberList.pl?sChamber="

        if chamber == 'lower':
            url += 'House'
        else:
            url += 'Senate'

        data = self.urlopen(url)
        doc = lxml.html.fromstring(data)
        doc.make_links_absolute('http://www.ncga.state.nc.us')
        rows = doc.xpath('//div[@id="mainBody"]/table/tr')

        for row in rows[1:]:
            party, district, full_name, counties = row.getchildren()

            party = party.text_content()
            party = party_map[party]

            district = district.text_content()

            notice = full_name.xpath('span')
            if notice:
                notice = notice[0].text_content()
                # skip resigned legislators
                if 'Resigned' in notice or 'Deceased' in notice:
                    continue
            else:
                notice = None
            link = full_name.xpath('a/@href')[0]
            full_name = full_name.xpath('a')[0].text_content()
            full_name = full_name.replace(u'\u00a0', ' ')

            # scrape legislator page details
            lhtml = self.urlopen(link)
            ldoc = lxml.html.fromstring(lhtml)
            ldoc.make_links_absolute('http://www.ncga.state.nc.us')
            photo_url = ldoc.xpath('//a[contains(@href, "pictures")]/@href')[0]
            phone = get_table_item(ldoc, 'Phone:')
            address = get_table_item(
                ldoc, 'Legislative Mailing Address:') or None
            email = ldoc.xpath(
                '//a[starts-with(@href, "mailto:")]')[0].text or ''

            # save legislator
            legislator = Legislator(term, chamber, district, full_name,
                                    photo_url=photo_url, party=party,
                                    url=link, notice=notice, email=email)
            legislator.add_source(link)
            legislator.add_office('capitol', 'Capitol Office',
                                  address=address, phone=phone)
            self.save_legislator(legislator)
