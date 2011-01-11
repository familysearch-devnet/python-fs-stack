# Sample OAuth authentication web app
# By Peter Henderson <peter.henderson@ldschurch.org>

# Requires:
#   - web.py <http://webpy.org/>

import familysearch
import web

user_agent = "LoginWebSample"
developer_key = 'WCQY-7J1Q-GKVV-7DNM-SQ5M-9Q5H-JX3H-CMJK'
familysearch_base_url = 'http://www.dev.usys.org'

urls = (
        '/', 'login',
        '/authorized', 'authorized',
        )
app = web.application(urls, globals())


class login():

    def GET(self):
        callback_url = web.ctx.home + '/authorized'
        
        # Step 1: Get a request token. This is a temporary token that is used for 
        # having the user authorize an access token and to sign the request to obtain 
        # said access token.
        fs = familysearch.FamilySearch(user_agent, developer_key, base=familysearch_base_url)
        try:
            request_token = fs.request_token(callback_url)
            # Save these cookies so the web app doesn't have to manage state
            # with multiple FamilySearch proxy objects
            web.setcookie('request_token', request_token['oauth_token'])
            web.setcookie('request_token_secret', request_token['oauth_token_secret'])
        except:
            return 'Error obtaining request token.'
        
        # Step 2: Redirect to the provider's authorize page.
        raise web.found(fs.authorize())


class authorized():

    def GET(self):
        # Step 3: Once the consumer has redirected the user back to the oauth_callback
        # URL you can request the access token the user has approved. You use the 
        # request token to sign this request. After this is done you throw away the
        # request token and use the access token returned. You should store this 
        # access token somewhere safe, like a database, for future use.
        cookies = web.cookies(request_token='', request_token_secret='')
        params = web.input(oauth_verifier='')
        
        fs = familysearch.FamilySearch(user_agent, developer_key, base=familysearch_base_url)
        try:
            fs.access_token(params.oauth_verifier, cookies.request_token, cookies.request_token_secret)
            return 'Your session is: %s' % fs.session_id
        except:
            return 'Error obtaining access token.'


if __name__ == '__main__':
    app.run()
