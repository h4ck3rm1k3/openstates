from billy.scrape.legislators import Legislator, LegislatorScraper
from billy.scrape import NoDataForPeriod
import lxml.html
import logging
import re

logger = logging.getLogger('openstates')


class NDLegislatorScraper(LegislatorScraper):
    jurisdiction = 'nd'

    def scrape(self, term, chambers):
        self.validate_term(term, latest_only=True)

        # figuring out starting year from metadata
        for t in self.metadata['terms']:
            if t['name'] == term:
                start_year = t['start_year']
                break

        root = "http://www.legis.nd.gov/assembly"
        main_url = "%s/%s-%s/members/members-by-district" % (
            root,
            term,
            start_year
        )

        page = self.urlopen(main_url)
        page = lxml.html.fromstring(page)
        page.make_links_absolute(main_url)
        for person in page.xpath("//div[contains(@class, 'all-members')]//a"):
            self.scrape_legislator_page(term, person.attrib['href'])

    def scrape_legislator_page(self, term, url):
        page = self.urlopen(url)
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)
        name = page.xpath("//h1[@id='page-title']/text()")[0]
        district = page.xpath("//a[contains(@href, 'district')]/text()")[0]
        district = district.replace("District", "").strip()

        committees = page.xpath("//a[contains(@href, 'committees')]/text()")

        party = page.xpath(
            "//div[contains(text(), 'Political Party')]"
        )[0].getnext().text_content().strip()

        photo = page.xpath(
            "//div[@class='field-person-photo']/img/@src"
        )
        photo = photo[0] if len(photo) else None

        address = page.xpath("//div[@class='adr']")[0]
        address = re.sub("\s+", " ", address.text_content()).strip()

        item_mapping = {
            "email": "email",
            "home telephone": "home-telephone",
            "cellphone": "cellphone",
            "office telephone": "office-telephone",
            "political party": "party",
            "chamber": "chamber",
            "fax": "fax"
        }
        metainf = {}

        for block in page.xpath("//div[contains(@class, 'field-label-inline')]"):
            label, items = block.xpath("./*")
            key = label.text_content().strip().lower()
            if key.endswith(":"):
                key = key[:-1]

            metainf[item_mapping[key]] = items.text_content().strip()

        chamber = {
            "Senate": "upper",
            "House": "lower"
        }[metainf['chamber']]

        kwargs = {
            "party": {"Democrat": "Democratic",
                      "Republican": "Republican"}[metainf['party']]
        }
        if photo:
            kwargs['photo_url'] = photo

        leg = Legislator(term,
                         chamber,
                         district,
                         name,
                         **kwargs)

        kwargs = {
            "address": address,
            "url": url
        }

        for key, leg_key in [
            ('email', 'email'),
            ('home-telephone', 'home_phone'),
            ('cellphone', 'cellphone'),
            ('fax', 'fax'),
            ('office-telephone', 'office_phone'),
        ]:
            if key in metainf:
                kwargs[leg_key] = metainf[key]

        leg.add_office('district',
                       'District Office',
                       **kwargs)

        # for committee in committees:
        #    leg.add_role('committee member',
        #                 term=term,
        #                 chamber=chamber,
        #                 committee=committee)

        leg.add_source(url)
        self.save_legislator(leg)
