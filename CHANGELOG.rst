===========================
 python-fs-stack Changelog
===========================

0.2 (8 Jun 2011)
----------------

* Supports Python 2.4
* Supports Authorities requests (place, name, date, and culture)
* Supports Person Version Read and Persona Read
* Properly sends session ID on first request without needing to call session()
* Search and Match return a single object instead of a one-item list
* Supports pickling using any protocol (0-2)
* Allows authorize() to supply arbitrary parameters
* Handles HTTP 401 (Unauthorized) for Python 2.4 and 2.5 (GitHub issue 1)
* Full regression test coverage (requires wsgi_intercept)
* The login.py example reads the password more portably


0.1 (21 Jan 2011)
-----------------

* Initial release
* Supports Family Tree Read requests only (person, pedigree, search, match)
* Returns parsed JSON
* Requires Python 2.5
