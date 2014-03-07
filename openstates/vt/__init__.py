from billy.utils.fulltext import pdfdata_to_text, text_after_line_numbers
from .bills import VTBillScraper
from .legislators import VTLegislatorScraper
from .committees import VTCommitteeScraper
from .events import VTEventScraper

metadata = dict(
    name='Vermont',
    abbreviation='vt',
    capitol_timezone='America/New_York',
    legislature_name='Vermont General Assembly',
    legislature_url='http://www.leg.state.vt.us/',
    chambers={
        'upper': {'name': 'Senate', 'title': 'Senator', 'term': 2},
        'lower': {'name': 'House', 'title': 'Representative', 'term': 2},
    },
    terms=[{'name': '2009-2010',
            'start_year': 2009,
            'end_year': 2010,
            'sessions': ['2009-2010']},
           {'name': '2011-2012',
            'start_year': 2011,
            'end_year': 2012,
            'sessions': ['2011-2012']},
           {'name': '2013-2014',
            'start_year': 2013,
            'end_year': 2014,
            'sessions': ['2013-2014']},
           ],
    session_details={'2009-2010': {'type': 'primary',
                                   'display_name': '2009-2010 Regular Session',
                                   '_scraped_name': '2009-2010 Session',
                                   },
                     '2011-2012': {'type': 'primary',
                                   'display_name': '2011-2012 Regular Session',
                                   '_scraped_name': '2011-2012 Session',
                                   },
                     '2013-2014': {'type': 'primary',
                                   'display_name': '2013-2014 Regular Session',
                                   '_scraped_name': '2013-2014 Session',
                                   },
                     },
    feature_flags=['influenceexplorer'],
    _ignored_scraped_sessions=['2009 Special Session', '2007-2008 Session',
                               '2005-2006 Session', '2005 Special Session',
                               '2003-2004 Session', '2001-2002 Session',
                               '1999-2000 Session', '1997-1998 Session',
                               '1995-1996 Session', '1993-1994 Session',
                               '1991-1992 Session', '1989-1990 Session',
                               '1987-1988 Session', '1985-1986 Session']

)


def session_list():
    from billy.scrape.utils import url_xpath
    return url_xpath('http://www.leg.state.vt.us/ResearchMain.cfm',
                     "//div[@id='ddsidebarmenu01']/ul/li/a/text()")


def extract_text(doc, data):
    return text_after_line_numbers(pdfdata_to_text(data))
