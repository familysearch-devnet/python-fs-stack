"""
A module implementing the Identity version 2 API module

Main class: IdentityV2, meant to be mixed-in to the FamilySearch class
"""

import random
import time
import urllib
import urllib2
import urlparse

# Support Python < 2.6
if not hasattr(urlparse, 'parse_qsl'):
    import cgi
    urlparse.parse_qsl = cgi.parse_qsl

from enunciate import identity

class IdentityV2(object):

    """
    A mix-in implementing the Identity version 2 endpoints
    """

    def __init__(self):
        """
        Set up the URLs for this IdentityV2 object.
        """
        self.identity_base = self.base + '/identity/v2/'

        self.oauth_secrets = dict()

        # Assume logged_in if session_id is set
        self.logged_in = bool(self.session_id)

        cookie_handler = urllib2.HTTPCookieProcessor()
        self.cookies = cookie_handler.cookiejar
        self.opener = urllib2.build_opener(cookie_handler)

    @property
    def identity_properties(self):
        """
        Retrieve and cache the Identity version 2 module's properties.
        """
        url = self.identity_base + 'properties'
        if not hasattr(self, '_identity_properties'):
            self._identity_properties = identity.parse(self._request(url)).properties
        return self._identity_properties

    def login(self, username, password):
        """
        Log into FamilySearch using Basic Authentication.

        Web applications must use OAuth.

        """
        self.logged_in = False
        self.cookies.clear()
        url = self.identity_base + 'login'
        credentials = urllib.urlencode({'username': username,
                                        'password': password,
                                        'key': self.key})
        self.session_id = identity.parse(self._request(url, credentials)).session.id
        self.logged_in = True
        return self.session_id

    def initialize(self):
        """
        Initialize a FamilySearch session using Basic Authentication.

        This creates an unauthenticated session and should be followed by an
        authenticate call. Web applications must use OAuth.

        """
        self.logged_in = False
        self.cookies.clear()
        url = self.identity_base + 'initialize'
        key = urllib.urlencode({'key': self.key})
        self.session_id = identity.parse(self._request(url, key)).session.id
        return self.session_id

    def authenticate(self, username, password):
        """
        Authenticate a FamilySearch session using Basic Authentication.

        This should follow an initialize call. Web applications must use OAuth.

        """
        url = self.identity_base + 'authenticate'
        credentials = {'username': username, 'password': password}
        if not self.cookies and self.session_id:
            # Set sessionId parameter if the session ID is not set in a cookie
            credentials['sessionId'] = self.session_id
        credentials = urllib.urlencode(credentials)
        self.session_id = identity.parse(self._request(url, credentials)).session.id
        self.logged_in = True
        return self.session_id

    def logout(self):
        """
        Log the current session out of FamilySearch.
        """
        self.logged_in = False
        url = self.identity_base + 'logout'
        self._request(url)
        self.session_id = None
        self.cookies.clear()

    def session(self):
        """
        Keep the current session in an active state by sending an empty request.

        Calling this method is an easy way to turn a sessionId query parameter
        into a cookie without doing anything else.

        """
        url = self.identity_base + 'session'
        if not self.cookies and self.session_id:
            # Add sessionId parameter to url if cookie is not set
            url = self._add_query_params(url, sessionId=self.session_id)
        try:
            session = identity.parse(self._request(url)).session.id
            self.logged_in = True
            return session
        except:
            self.logged_in = False
            raise

    def request_token(self, callback_url='oob'):
        """
        Get a request token for step 1 of the OAuth login process.

        Returns a dictionary containing the OAuth response and stores the token
        and token secret, which are needed to get an access token (step 3).

        """
        self.logged_in = False
        self.cookies.clear()
        url = self.identity_properties['request.token.url']
        oauth_response = self._oauth_request(url, oauth_callback=callback_url)
        response = dict(urlparse.parse_qsl(oauth_response.read()))
        self.session_id = response['oauth_token']
        self.oauth_secrets[response['oauth_token']] = response['oauth_token_secret']
        return response

    def authorize(self, request_token=None):
        """
        Construct and return the User Authorization URL for step 2 of the OAuth login process.

        This URL should be loaded into the user's browser. It is the
        application's responsibility to receive the OAuth verifier from the
        callback URL (such as by running an HTTP server) or to provide a means
        for the user to enter the verifier into the application.

        """
        if not request_token:
            if self.session_id and self.session_id in self.oauth_secrets:
                # Use current session ID for oauth_token if it is set
                request_token = self.session_id
            else:
                # Otherwise, get a new request token and use it
                request_token = self.request_token()['oauth_token']
        # Add sessionId parameter to authorize.url
        url = self.identity_properties['authorize.url']
        url = self._add_query_params(url, sessionId=request_token)
        return url

    def access_token(self, verifier, request_token=None, token_secret=None):
        """
        Get an access token (session ID) to complete step 3 of the OAuth login process.

        Returns a dictionary containing the OAuth response and stores the token
        as the session ID to be used by future requests.

        """
        if not request_token and self.session_id:
            # Use current session ID for oauth_token if it is set
            request_token = self.session_id
            if not token_secret and self.session_id in self.oauth_secrets:
                # Use saved secret for oauth_token_secret if it is set
                token_secret = self.oauth_secrets[request_token]
        url = self.identity_properties['access.token.url']
        oauth_response = self._oauth_request(url, token_secret,
                                             oauth_token=request_token,
                                             oauth_verifier=verifier)
        response = dict(urlparse.parse_qsl(oauth_response.read()))
        self.session_id = response['oauth_token']
        self.session()
        self.logged_in = True
        return response

    def _oauth_request(self, url, token_secret='', params={}, **kw_params):
        """
        Make an OAuth request.

        This function only supports the PLAINTEXT signature method.
        Returns a file-like object representing the response.

        Keyword arguments:
        url -- the URL to request
        token_secret (optional) -- the request token secret, if requesting an
                                   access token (defaults to empty)
        params -- a dictionary of parameters to add to the request, such as
                  oauth_callback, oauth_token, or oauth_verifier

        Additional parameters can be passed either as a dictionary or as
        keyword arguments.

        """
        oauth_params = dict(params)
        oauth_params.update(kw_params)
        oauth_params.update({
                             'oauth_consumer_key': self.key,
                             'oauth_nonce': str(random.randint(0, 99999999)),
                             'oauth_signature_method': 'PLAINTEXT',
                             'oauth_signature': '%s&%s' % ('', token_secret),
                             'oauth_timestamp': str(int(time.time())),
                            })
        data = urllib.urlencode(oauth_params, True)
        request = urllib2.Request(url, data)
        request.add_header('User-Agent', self.agent)
        try:
            return self.opener.open(request)
        except urllib2.HTTPError, error:
            if error.getcode() == 401:
                self.logged_in = False
            raise

from . import FamilySearch
FamilySearch.__bases__ += (IdentityV2,)
