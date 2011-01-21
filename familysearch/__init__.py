"""
A library to interact with the FamilySearch API

Licensed under the FamilySearch API License Agreement;
see the included LICENSE file for details.

Example usage:

from familysearch import FamilySearch

# Log in immediately
fs = FamilySearch('ClientApp/1.0', 'developer_key', 'username', 'password')

# Log in in a separate step
fs = FamilySearch('ClientApp/1.0', 'developer_key')
fs.login('username', 'password')

# Log in in two steps
fs = FamilySearch('ClientApp/1.0', 'developer_key')
fs.initialize()
fs.authenticate('username', 'password')

# Restore a previous session
fs = FamilySearch('ClientApp/1.0', 'developer_key', session='session_id')

# Use the production system instead of the reference system
fs = FamilySearch('ClientApp/1.0', 'developer_key', base='https://api.familysearch.org')

# Log in with OAuth
import webbrowser
fs = FamilySearch('ClientApp/1.0', 'developer_key')
fs.request_token()
webbrowser.open(fs.authorize())
# [Enter username and password into browser window that opens]
verifier = [verifier from resulting web page]
fs.access_token(verifier)

# Keep current session active
fs.session()

# Log out
fs.logout()

# Print current user's family tree details
print fs.person()

# Print current user's pedigree
print fs.pedigree()
"""

import urllib
import urllib2
import urlparse

# Support Python < 2.6
if not hasattr(urlparse, 'parse_qs'):
    import cgi
    urlparse.parse_qs = cgi.parse_qs

__version__ = '0.1'


class object(object): pass
class FamilySearch(object):

    """
    A FamilySearch API proxy

    The constructor must be called with a user-agent string and a developer key.
    A username, password, session ID, and base URL are all optional.

    Public methods:

    login -- log into FamilySearch with a username and password
    initialize -- create an unauthenticated session
    authenticate -- authenticate a session with a username and password
    logout -- log out of FamilySearch, terminating the current session
    session -- keep current session active
    request_token -- get an OAuth request token
    authorize -- construct OAuth authorization URL
    access_token -- get an OAuth access token (to complete the login process)
    person -- get a person or list of persons from the family tree
    pedigree -- get the pedigree of a person or list of persons
    search -- search for persons in the family tree
    match -- search for possible duplicates in the family tree

    Public attributes:

    logged_in -- flag indicating whether this proxy instance is logged in
    """

    def __init__(self, agent, key, username=None, password=None, session=None,
                 base='http://www.dev.usys.org'):
        """
        Instantiate a FamilySearch proxy object.

        Keyword arguments:
        agent -- User-agent string to use for requests
        key -- FamilySearch developer key (optional if reusing an existing session ID)
        username (optional)
        password (optional)
        session (optional) -- existing session ID to reuse
        base (optional) -- base URL for the API;
                           defaults to 'http://www.dev.usys.org' (the Reference System)
        """
        self.agent = '%s Python-FS-Stack/%s' % (agent, __version__)
        self.key = key
        self.session_id = session
        self.base = base
        self.opener = urllib2.build_opener()

        for mixin in self.__class__.__bases__:
            mixin.__init__(self)

        if username and password:
            self.login(username, password)
        elif session:
            self.session()

    def _request(self, url, data=None):
        """
        Make a GET or a POST request to the FamilySearch API.

        Adds the User-Agent header and sets the response format to JSON.
        If the data argument is supplied, makes a POST request.
        Returns a file-like object representing the response.

        """
        url = self._add_json_format(url)
        request = urllib2.Request(url, data)
        request.add_header('User-Agent', self.agent)
        try:
            return self.opener.open(request)
        except urllib2.HTTPError, error:
            if error.getcode() == 401:
                self.logged_in = False
            raise

    def _add_subpath(self, url, subpath):
        """
        Add a subpath to the path component of the given URL.

        For example, adding sub to http://example.com/path?query
        becomes http://example.com/path/sub?query.

        """
        parts = urlparse.urlsplit(url)
        path = parts[2] + '/' + subpath
        return urlparse.urlunsplit((parts[0], parts[1], path, parts[3], parts[4]))

    def _add_query_params(self, url, params={}, **kw_params):
        """
        Add the specified query parameters to the given URL.

        Parameters can be passed either as a dictionary or as keyword arguments.

        """
        parts = urlparse.urlsplit(url)
        query_parts = urlparse.parse_qs(parts[3])
        query_parts.update(params)
        query_parts.update(kw_params)
        query = urllib.urlencode(query_parts, True)
        return urlparse.urlunsplit((parts[0], parts[1], parts[2], query, parts[4]))

    def _add_json_format(self, url):
        """
        Add dataFormat=application/json to the query string of the given URL.
        """
        return self._add_query_params(url, dataFormat='application/json')

import identity_v2
import familytree_v2
