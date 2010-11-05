# Sample OAuth authentication console app
# By Peter Henderson <peter.henderson@ldschurch.org>

import BaseHTTPServer
import functools
import random
import time
import urllib
import urllib2
import urlparse
import webbrowser

from enunciate import identity

developer_key = 'WCQY-7J1Q-GKVV-7DNM-SQ5M-9Q5H-JX3H-CMJK'
developer_secret = ''

familysearch_base_url = 'http://www.dev.usys.org'
endpoint_format = '%s/identity/v2/%%s?dataFormat=application/json' % familysearch_base_url
properties_url = endpoint_format % 'properties'
login_url = endpoint_format % 'login'

properties = identity.parse(urllib2.urlopen(properties_url)).properties
request_token_url = properties["request.token.url"]
authorize_url = properties["authorize.url"]
access_token_url = properties["access.token.url"]

AUTHORIZED_URL = "/authorized"
LOGIN_SUCCESS_HTML = """
<html>
  <head>
    <title>Login success</title>
  </head>
  <body>
    FamilySearch login successful.
    You may close this window and return to the application.
  </body>
</html>
"""
LOGIN_FAILURE_HTML = """
<html>
  <head>
    <title>Login failure</title>
  </head>
  <body>
    FamilySearch login failed.
    Please close this window, return to the application, and try again.
  </body>
</html>
"""


class OAuthLoginHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, state, *args, **kwargs):
        """Extend BaseHTTPRequestHandler.__init__ to save a state variable.
        
        state must be a mutable object for the handler to return the session ID
        """
        self.state = state
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    
    def do_GET(self):
        url = urlparse.urlparse(self.path)
        if url.path == AUTHORIZED_URL:
            authorized_url_params = dict(urlparse.parse_qsl(url.query))
            if authorized_url_params['oauth_token'] == self.state['oauth_token']:
                self.state['oauth_verifier'] = authorized_url_params['oauth_verifier']
                
                # Step 3: Once the consumer has redirected the user back to the oauth_callback
                # URL you can request the access token the user has approved. You use the 
                # request token to sign this request. After this is done you throw away the
                # request token and use the access token returned. You should store this 
                # access token somewhere safe, like a database, for future use.
                status, content = oauth_request(access_token_url, developer_key, developer_secret,
                                                token_secret=self.state['oauth_token_secret'],
                                                params={
                                                        "oauth_token": self.state['oauth_token'],
                                                        "oauth_verifier": self.state['oauth_verifier'],
                                                       })
                if status == 200:
                    self.state.clear()
                    self.state.update(urlparse.parse_qsl(content))
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(LOGIN_SUCCESS_HTML)
                    return
                else:
                    self.state.clear()
                    self.send_response(500)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(LOGIN_FAILURE_HTML)
                    return
        self.state.clear()
        self.send_error(500)
    
    def log_message(self, *args, **kwargs):
        """Override the log_message function to avoid printing the request to the terminal."""
        pass


def oauth_request(url, consumer_key, consumer_secret, token_secret="", params={}):
    """Make an OAuth request and return the HTTP status and response.
    
    Arguments:
    url -- the URL to request
    consumer_key -- the developer key (FamilySearch developer key)
    consumer_secret -- the developer secret (empty in FamilySearch's implementation)
    token_secret (optional) -- the request token secret, if requesting an access token
    params -- a dict of parameters to add to the request, such as oauth_callback, oauth_token, or oauth_verifier
    
    This function only supports the PLAINTEXT signature method.
    
    """
    url = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url[4]))
    query.update(params)
    query.update({
                  "oauth_consumer_key": consumer_key,
                  "oauth_nonce": str(random.randint(0, 99999999)),
                  "oauth_signature_method": "PLAINTEXT",
                  "oauth_signature": "%s&%s" % (consumer_secret, token_secret),
                  "oauth_timestamp": str(int(time.time())),
                 })
    url[4] = urllib.urlencode(query)
    url = urlparse.urlunparse(url)
    try:
        response = urllib2.urlopen(url)
    except urllib2.HTTPError, error:
        response = error
    return response.getcode(), response.read()


def login_oauth():
    """Get a FamilySearch session ID using OAuth.
    
    Get a request token,
    start a temporary local web server,
    open a browser to authorize the request token,
    exchange the authorized request token for an access token,
    and return the resulting session ID.
    
    Raise an exception if obtaining either the request token or access token fails.
    
    """
    state = {}
    authorize_handler = functools.partial(OAuthLoginHandler, state)
    authorize_server = BaseHTTPServer.HTTPServer(("", 0), authorize_handler)
    port = authorize_server.server_port
    callback_url = "http://localhost:%i%s" % (port, AUTHORIZED_URL)
    
    # Step 1: Get a request token. This is a temporary token that is used for 
    # having the user authorize an access token and to sign the request to obtain 
    # said access token.
    status, content = oauth_request(request_token_url, developer_key, developer_secret,
                                    params={"oauth_callback": callback_url})
    if status != 200:
        raise Exception('Error %s obtaining request token.' % status)
    state.update(urlparse.parse_qsl(content))
    
    # Step 2: Open browser to the provider's authorize page.
    webbrowser.open('%s?oauth_token=%s' % (authorize_url, state['oauth_token']))
    authorize_server.handle_request()
    if 'oauth_token' in state:
        return state['oauth_token']
    else:
        raise Exception('Error obtaining access token.')


def login_basic(username, password):
    """Get a FamilySearch session ID using Basic Authentication.
    
    Raise urllib2.HTTPError(401) if credentials are invalid.
    
    """
    credentials = "username=%s&password=%s&key=%s" % (username, password, developer_key)
    return identity.parse(urllib2.urlopen(login_url, credentials)).session.id


if __name__ == '__main__':
    session_id = login_oauth()
    print "Use session ID: %s" % session_id
