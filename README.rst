The Open State Project collects and makes available data about state legislative activities, including bill summaries, votes, sponsorships and state legislator information. This data is gathered directly from the states and made available in a common format for interested developers, through a JSON API and data dumps.

Installation
============

see http://openstates.org/contributing/

Used Modules
==========
Here are some of the important modules that play a major role in the project.

* Openstates, 
I have my own fork here https://github.com/h4ck3rm1k3/openstates which contains experimental code. Do not use it in production.

* billy
The billy system is the main driver for openstates, openstates is driven by billy.
main project :https://github.com/sunlightlabs/billy
my fork : https://github.com/h4ck3rm1k3/billy

* scrapelib
A thin layer of icing over the requests lib
main project :https://github.com/sunlightlabs/scrapelib
my fork : https://github.com/h4ck3rm1k3/scrapelib

* requests
The user friendly agent lib
main project :https://github.com/kennethreitz/requests
my fork : https://github.com/h4ck3rm1k3/requests

* urllib3

The underlying lib for managing http
official : https://github.com/shazow/urllib3
my fork : https://github.com/h4ck3rm1k3/urllib3

* pymongo
The python mongo lib, 
official : https://github.com/mongodb/mongo-python-driver
my fork : https://github.com/h4ck3rm1k3/mongo-python-driver

The bson lib is in there and used to store the binary json data.

* Api Server :
This server is my experimental server based on the kansas server. 
https://github.com/h4ck3rm1k3/openstates-api-dancer

Scraping single bills
=====================

My plan for scraping single bills : extract the list of data from the api and filter it.

Searching for bills
=====================

My plan for searching, be able to filter the API while downloading, or download only matching data. Related to single bills.


Debian Stable (python 2.6)
=============
sudo apt-get install abiword

sudo pip-2.6 install -r requirements.txt --use-mirrors
sudo pip-2.6 install -r requirements-site.txt --use-mirrors

.. sudo pip-2.6 install django-storages
.. sudo apt-get install python-docutils # - utilities for the documentation of Python modules
.. sudo apt-get install python-markdown # 
.. git clone  https://github.com/sunlightlabs/django-locksmith.git;  cd django-locksmith/;  sudo python2.6 setup.py  install
.. sudo pip-2.6 install billy #billy                     - scraping, storing, and sharing legislative information

Schema
======

The json from the states must match the schema files located in openstates/billy/schemas/, each scraper will provide a ._get_schema() method that loads the schema
and passes it to the validator. see validator.validator.SchemaValidator.


Links
=====

* `Open State Project API <http://openstates.org/api/>`_
* `Contributing Guidelines <http://openstates.org/contributing/>`_
* `Code on GitHub <http://github.com/sunlightlabs/openstates/>`_
* `Issue Tracker <http://sunlight.atlassian.net>`_
* `Open State Project Google Group <http://groups.google.com/group/fifty-state-project>`_
* `Sunlight Labs <http://sunlightlabs.com>`_
