"""
A module implementing the Identity version 2 API module

Main class: IdentityV2, meant to be mixed-in to the FamilySearch class
"""

import urllib
import urllib2

from enunciate import identity

class IdentityV2(object):

    """
    A mix-in implementing the Identity version 2 endpoints
    """

    def __init__(self):
        """Set up the URLs for this IdentityV2 object."""
        identity_base = self.base + '/identity/v2/'
        self.login_url = identity_base + 'login'
        self.initialize_url = identity_base + 'initialize'
        self.authenticate_url = identity_base + 'authenticate'
        self.logout_url = identity_base + 'logout'

        cookie_handler = urllib2.HTTPCookieProcessor()
        self.cookies = cookie_handler.cookiejar
        self.opener = urllib2.build_opener(cookie_handler)

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

from . import FamilySearch
FamilySearch.__bases__ += (IdentityV2,)
