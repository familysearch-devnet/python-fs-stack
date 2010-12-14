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

# Log out
fs.logout()

# Print current user's family tree details
print fs.person()
"""

try:
    import json
except ImportError:
    import simplejson as json
import urllib
import urllib2
import urlparse

from enunciate import identity

__version__ = '0.1'


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
    person -- get a person or list of persons from the family tree
    """

    def __init__(self, agent, key, username=None, password=None, session=None, base='http://www.dev.usys.org'):
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
        self.session = session
        self.base = base
        identity_base = base + '/identity/v2/'
        self.login_url = identity_base + 'login'
        self.initialize_url = identity_base + 'initialize'
        self.authenticate_url = identity_base + 'authenticate'
        self.logout_url = identity_base + 'logout'
        familytree_base = base + '/familytree/v2/'
        self.person_url = familytree_base + 'person'

        cookie_handler = urllib2.HTTPCookieProcessor()
        self.cookies = cookie_handler.cookiejar
        self.opener = urllib2.build_opener(cookie_handler)

        if username and password:
            self.login(username, password)

    def login(self, username, password):
        """
        Log into FamilySearch using Basic Authentication.

        Web applications must use OAuth.

        """
        credentials = urllib.urlencode({'username': username, 'password': password, 'key': self.key})
        self.session = identity.parse(self._request(self.login_url, credentials)).session.id
        return self.session

    def initialize(self):
        """
        Initialize a FamilySearch session using Basic Authentication.

        This creates an unauthenticated session and should be followed by an
        authenticate call. Web applications must use OAuth.

        """
        key = urllib.urlencode({'key': self.key})
        self.session = identity.parse(self._request(self.initialize_url, key)).session.id
        return self.session

    def authenticate(self, username, password):
        """
        Authenticate a FamilySearch session using Basic Authentication.

        This should follow an initialize call. Web applications must use OAuth.

        """
        credentials = urllib.urlencode({'username': username, 'password': password})
        self.session = identity.parse(self._request(self.authenticate_url, credentials)).session.id
        return self.session

    def logout(self):
        """
        Log the current session out of FamilySearch.
        """
        self._request(self.logout_url)
        self.session = None
        self.cookies.clear()

    def person(self, person_id=None, options={}, **kw_options):
        """
        Get a representation of a person or list of persons from the family tree.
        """
        if isinstance(person_id, list):
            person_id = ",".join(person_id)
        elif person_id == 'me':
            person_id = None
        url = self.person_url
        if person_id:
            url = self._add_subpath(url, person_id)
        if options or kw_options:
            url = self._add_query_params(url, options, **kw_options)
        response = json.load(self._request(url))['persons']
        if len(response) == 1:
            return response[0]
        else:
            return response

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
        return self.opener.open(request)

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
