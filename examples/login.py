# Sample authentication console app
# By Peter Henderson <peter.henderson@ldschurch.org>

import BaseHTTPServer
import urllib2
import urlparse
import webbrowser

import familysearch

user_agent = "LoginSample"
developer_key = 'WCQY-7J1Q-GKVV-7DNM-SQ5M-9Q5H-JX3H-CMJK'
familysearch_base_url = 'http://www.dev.usys.org'


def create_proxy():
    return familysearch.FamilySearch(user_agent, developer_key, base=familysearch_base_url)


def login_oauth():
    """
    Log into FamilySearch using OAuth.

    Get a request token,
    start a temporary local web server,
    open a browser to authorize the request token,
    exchange the authorized request token for an access token,
    and return the resulting authenticated FamilySearch proxy.

    Raise an exception if obtaining either the request token or access token fails.

    """

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
        """Handle the callback request after the user authorizes the request token."""

        def do_GET(self):
            url = urlparse.urlparse(self.path)
            if url.path == AUTHORIZED_URL:
                authorized_url_params = dict(urlparse.parse_qsl(url.query))

                # Step 3: Once the consumer has redirected the user back to the oauth_callback
                # URL you can request the access token the user has approved. You use the 
                # request token to sign this request. After this is done you throw away the
                # request token and use the access token returned. You should store this 
                # access token somewhere safe, like a database, for future use.
                try:
                    access_token = fs.access_token(authorized_url_params['oauth_verifier'])
                    if 'oauth_token' in access_token:
                        self.send_response(200)
                        self.send_header("Content-type", "text/html")
                        self.end_headers()
                        self.wfile.write(LOGIN_SUCCESS_HTML)
                        return
                except urllib2.HTTPError:
                    self.send_response(500)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(LOGIN_FAILURE_HTML)
                    return
            self.send_error(500)

        def log_message(self, *args, **kwargs):
            """Override the log_message function to avoid printing the request to the terminal."""
            pass


    fs = create_proxy()
    authorize_server = BaseHTTPServer.HTTPServer(("", 0), OAuthLoginHandler)
    port = authorize_server.server_port
    callback_url = "http://localhost:%i%s" % (port, AUTHORIZED_URL)

    # Step 1: Get a request token. This is a temporary token that is used for 
    # having the user authorize an access token and to sign the request to obtain 
    # said access token.
    fs.request_token(callback_url)

    # Step 2: Open browser to the provider's authorize page.
    webbrowser.open(fs.authorize())
    authorize_server.handle_request()
    if fs.logged_in:
        return fs
    else:
        raise Exception('Error obtaining access token.')


def login_basic():
    """
    Log into FamilySearch using Basic Authentication.

    Raise urllib2.HTTPError(401) if credentials are invalid.

    """
    username = raw_input("Username: ")
    # Hide keystrokes to avoid displaying the password (only works under POSIX)
    try:
        import termios, sys
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        new = termios.tcgetattr(fd)
        new[3] = new[3] & ~termios.ECHO
        try:
            termios.tcsetattr(fd, termios.TCSADRAIN, new)
            password = raw_input("Password: ")
            print
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except ImportError:
        print "Error hiding keystrokes; your password will be visible"
        password = raw_input("Password: ")
    fs = create_proxy()
    fs.login(username, password)
    return fs


if __name__ == '__main__':
    fs = login_oauth()
    print "Use session ID: %s" % fs.session_id
