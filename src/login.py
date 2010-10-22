# Sample OAuth authentication web app
# By Peter Henderson <peter.henderson@ldschurch.org>

# Requires:
#   - python-oauth2 <http://github.com/simplegeo/python-oauth2>
#   - httplib2 <http://code.google.com/p/httplib2/>
#   - web.py <http://webpy.org/>

import urllib2
import urlparse

import oauth2 as oauth
import web

import enunciate.identity

consumer_key = 'WCQY-7J1Q-GKVV-7DNM-SQ5M-9Q5H-JX3H-CMJK'
consumer_secret = ''

familysearch_base_url = 'http://www.dev.usys.org'
properties_url = familysearch_base_url + '/identity/v2/properties' + '?dataFormat=application/json'
properties = enunciate.identity.parse(urllib2.urlopen(properties_url)).properties
request_token_url = properties["request.token.url"]
access_token_url = properties["access.token.url"]
authorize_url = properties["authorize.url"]

urls = (
        '/', 'login',
        '/authorized', 'authorized',
        )
app = web.application(urls, globals())


class login():
    
    def GET(self):
        callback_url = web.ctx.home + '/authorized'
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer)
        client.set_signature_method(oauth.SignatureMethod_PLAINTEXT())
        
        # Step 1: Get a request token. This is a temporary token that is used for 
        # having the user authorize an access token and to sign the request to obtain 
        # said access token.
        resp, content = client.request(request_token_url + "?oauth_callback=%s" % callback_url)
        if resp['status'] != '200':
            return 'Invalid response %s.' % resp['status']
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
        token = oauth.Token(cookies.request_token, cookies.request_token_secret)
        token.set_verifier(params.oauth_verifier)
        consumer = oauth.Consumer(consumer_key, consumer_secret)
        client = oauth.Client(consumer, token)
        
        resp, content = client.request(access_token_url)
        access_token = dict(urlparse.parse_qsl(content))
        return 'Your session is: %s' % access_token['oauth_token']


if __name__ == '__main__':
    app.run()
