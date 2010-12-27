# Sample OAuth authentication web app
# By Peter Henderson <peter.henderson@ldschurch.org>

# Requires:
#   - web.py <http://webpy.org/>

import random
import time
import urllib
import urllib2
import urlparse

import web

from familysearch.enunciate import identity

consumer_key = 'WCQY-7J1Q-GKVV-7DNM-SQ5M-9Q5H-JX3H-CMJK'
consumer_secret = ''

familysearch_base_url = 'http://www.dev.usys.org'
properties_url = familysearch_base_url + '/identity/v2/properties' + '?dataFormat=application/json'
properties = identity.parse(urllib2.urlopen(properties_url)).properties
request_token_url = properties["request.token.url"]
authorize_url = properties["authorize.url"]
access_token_url = properties["access.token.url"]

urls = (
        '/', 'login',
        '/authorized', 'authorized',
        )
app = web.application(urls, globals())


def oauth_request(url, consumer_key, consumer_secret, token_secret="", params={}):
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


class login():

    def GET(self):
        callback_url = web.ctx.home + '/authorized'
        
        # Step 1: Get a request token. This is a temporary token that is used for 
        # having the user authorize an access token and to sign the request to obtain 
        # said access token.
        status, content = oauth_request(request_token_url, consumer_key, consumer_secret,
                                        params={"oauth_callback": callback_url})
        if status != 200:
            return 'Invalid response %s.' % status
        request_token = dict(urlparse.parse_qsl(content))
        web.setcookie('request_token', request_token['oauth_token'])
        web.setcookie('request_token_secret', request_token['oauth_token_secret'])
        
        # Step 2: Redirect to the provider's authorize page.
        raise web.found('%s?oauth_token=%s' % (authorize_url, request_token['oauth_token']))


class authorized():

    def GET(self):
        # Step 3: Once the consumer has redirected the user back to the oauth_callback
        # URL you can request the access token the user has approved. You use the 
        # request token to sign this request. After this is done you throw away the
        # request token and use the access token returned. You should store this 
        # access token somewhere safe, like a database, for future use.
        cookies = web.cookies(request_token='', request_token_secret='')
        params = web.input(oauth_verifier='')
        
        status, content = oauth_request(access_token_url, consumer_key, consumer_secret,
                                        token_secret=cookies.request_token_secret,
                                        params={
                                                "oauth_token": cookies.request_token,
                                                "oauth_verifier": params.oauth_verifier,
                                               })
        access_token = dict(urlparse.parse_qsl(content))
        return 'Your session is: %s' % access_token['oauth_token']


if __name__ == '__main__':
    app.run()
