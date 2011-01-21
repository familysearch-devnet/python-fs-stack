=================
 python-fs-stack
=================

``python-fs-stack`` provides a Python package that simplifies access to the
FamilySearch_ `REST-style API`_.

.. _FamilySearch: https://new.familysearch.org/
.. _REST-style API: https://devnet.familysearch.org/docs/api


.. contents::


Dependencies
============

- Python 2.5 or later
- simplejson_, if using Python older than 2.6

.. _simplejson: http://pypi.python.org/pypi/simplejson


Installation
============

::

  python setup.py install


Example Usage
=============

First, import the FamilySearch class::

  from familysearch import FamilySearch


Authenticating with FamilySearch
--------------------------------

``python-fs-stack`` supports several ways of initiating a session with
FamilySearch, including Basic Authentication, OAuth, and resuming a previous
session.

Log in immediately with Basic Authentication::

  fs = FamilySearch('ClientApp/1.0', 'developer_key', 'username', 'password')

Log in in a separate step with Basic Authentication::

  fs = FamilySearch('ClientApp/1.0', 'developer_key')
  fs.login('username', 'password')

Log in in two steps with Basic Authentication::

  fs = FamilySearch('ClientApp/1.0', 'developer_key')
  fs.initialize()
  fs.authenticate('username', 'password')

Log in with OAuth::

  import webbrowser
  fs = FamilySearch('ClientApp/1.0', 'developer_key')
  fs.request_token()
  webbrowser.open(fs.authorize())
  # [Enter username and password into browser window that opens]
  verifier = [verifier from resulting web page]
  fs.access_token(verifier)

Resume a previous session::

  fs = FamilySearch('ClientApp/1.0', 'developer_key', session='session_id')

Use the production system instead of the reference system::

  fs = FamilySearch('ClientApp/1.0', 'developer_key', base='https://api.familysearch.org')


Maintaining and Ending a Session
--------------------------------

Keep the current session active::

  fs.session()

Log out::

  fs.logout()


Accessing Family Tree Information
---------------------------------

Print current user's family tree details::

  print fs.person()

To specify a person ID to retrieve, pass the ID as an argument::

  print fs.person('ABCD-123')

To print multiple family tree entries, pass a list of IDs as an argument. To
pass additional parameters to the API, simply pass them as named arguments::

  print fs.person(['ABCD-123', 'EFGH-456'], events='all', children='all')

Print current user's pedigree::

  print fs.pedigree()

Format the pedigree output more nicely::

  import pprint
  pprint.pprint(fs.pedigree())


Searching for Persons in the Family Tree
----------------------------------------

Search for a male named John Smith::

  results = fs.search(givenName='John', familyName='Smith', gender='Male', maxResults=10)

Retrieve the second page of the previous search::

  more_results = fs.search(contextId=results[0]['contextId'], maxResults=10, startIndex=10)

Search for an exact match for John Smith (use an ``options`` dict to specify
options with periods in their names)::

  results = fs.search(options={'givenName.exact': 'John', 'familyName.exact': 'Smith'}, gender='Male', maxResults=10)

Searching for Possible Duplicates
---------------------------------

Search for possible duplicates of a person::

  results = fs.match('ABCD-123')

Compute match score between two persons::

  results = fs.match('ABCD-123', id='EFGH-456')

Search for possible duplicates matching specified parameters::

  results = fs.match(givenName='John', familyName='Smith', gender='Male', birthDate='1900', birthPlace='USA', deathDate='1950', deathPlace='USA')
