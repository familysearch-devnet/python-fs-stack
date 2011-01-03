"""
A module implementing the Identity version 2 API module

Main class: IdentityV2, meant to be mixed-in to the FamilySearch class
"""

import random
import time
import urllib
import urllib2
import urlparse

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
        self.session_url = identity_base + 'session'

        properties_url = identity_base + 'properties'
        self.identity_properties = identity.parse(self._request(properties_url)).properties
        self.request_token_url = self.identity_properties['request.token.url']
        self.authorize_url = self.identity_properties['authorize.url']
        self.access_token_url = self.identity_properties['access.token.url']
        self.oauth_secrets = dict()

        cookie_handler = urllib2.HTTPCookieProcessor()
        self.cookies = cookie_handler.cookiejar
        self.opener = urllib2.build_opener(cookie_handler)

    def login(self, username, password):
        """
        Log into FamilySearch using Basic Authentication.

        Web applications must use OAuth.

        """
        self.cookies.clear()
        credentials = urllib.urlencode({'username': username, 'password': password, 'key': self.key})
        self.session = identity.parse(self._request(self.login_url, credentials)).session.id
        return self.session

    def initialize(self):
        """
        Initialize a FamilySearch session using Basic Authentication.

        This creates an unauthenticated session and should be followed by an
        authenticate call. Web applications must use OAuth.

        """
        self.cookies.clear()
        key = urllib.urlencode({'key': self.key})
        self.session = identity.parse(self._request(self.initialize_url, key)).session.id
        return self.session

    def authenticate(self, username, password):
        """
        Authenticate a FamilySearch session using Basic Authentication.

        This should follow an initialize call. Web applications must use OAuth.

        """
        credentials = {'username': username, 'password': password}
        if not self.cookies and self.session:
            # Set sessionId parameter if the session ID is not set in a cookie
            credentials['sessionId'] = self.session
        credentials = urllib.urlencode(credentials)
        self.session = identity.parse(self._request(self.authenticate_url, credentials)).session.id
        return self.session

    def logout(self):
        """
        Log the current session out of FamilySearch.
        """
        self._request(self.logout_url)
        self.session = None
        self.cookies.clear()

    def session_read(self):
        """
        Keep the current session in an active state by sending an empty request.

        Calling this method is an easy way to turn a sessionId query parameter
        into a cookie without doing anything else.

        """
        if not self.cookies and self.session:
            # Add sessionId parameter to session_url if cookie is not set
            parts = urlparse.urlsplit(self.session_url)
            query_parts = urlparse.parse_qs(parts[4])
            query_parts['sessionId'] = self.session
            query = urllib.urlencode(query_parts, True)
            url = urlparse.urlunsplit((parts[0], parts[1], parts[2], query, parts[4]))
        else:
            url = self.session_url
        return identity.parse(self._request(url)).session.id

    def request_token(self, callback_url='oob'):
        """
        Get a request token for step 1 of the OAuth login process.

        Returns a dictionary containing the OAuth response and stores the token
        and token secret, which are needed to get an access token (step 3).

        """
        self.cookies.clear()
        oauth_response = self._oauth_request(self.request_token_url,
                                             oauth_callback=callback_url)
        response = dict(urlparse.parse_qsl(oauth_response.read()))
        self.session = response['oauth_token']
        self.oauth_secrets[response['oauth_token']] = response['oauth_token_secret']
        return response

    def authorize(self, request_token=None):
        """
        Construct and return the Authorize URL for step 2 of the OAuth login process.

        This URL should be loaded into the user's browser. It is the
        application's responsibility to receive the OAuth verifier from the
        callback URL (such as by running an HTTP server) or to provide a means
        for the user to enter the verifier into the application.

        """
        if not request_token:
            if self.session and self.session in self.oauth_secrets:
                # Use current session ID for oauth_token if it is set
                request_token = self.session
            else:
                # Otherwise, get a new request token and use it
                request_token = self.request_token()['oauth_token']
        # Add sessionId parameter to authorize_url
        parts = urlparse.urlsplit(self.authorize_url)
        query_parts = urlparse.parse_qs(parts[4])
        query_parts['sessionId'] = request_token
        query = urllib.urlencode(query_parts, True)
        url = urlparse.urlunsplit((parts[0], parts[1], parts[2], query, parts[4]))
        return url

    def access_token(self, verifier, request_token=None, token_secret=None):
        """
        Get an access token (session ID) to complete step 3 of the OAuth login process.
        """
        if not request_token and self.session:
            # Use current session ID for oauth_token if it is set
            request_token = self.session
            if not token_secret and self.session in self.oauth_secrets:
                # Use saved secret for oauth_token_secret if it is set
                token_secret = self.oauth_secrets[request_token]
        oauth_response = self._oauth_request(self.access_token_url, token_secret,
                                             oauth_token=request_token,
                                             oauth_verifier=verifier)
        response = dict(urlparse.parse_qsl(oauth_response.read()))
        self.session = response['oauth_token']
        self.session_read()
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
        return self.opener.open(request)

from . import FamilySearch
FamilySearch.__bases__ += (IdentityV2,)
