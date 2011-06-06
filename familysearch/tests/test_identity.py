import familysearch
import unittest
import urllib2
import wsgi_intercept.httplib_intercept
try:
    import json
except ImportError:
    import simplejson as json
from common import *


class TestIdentity(unittest.TestCase):

    def setUp(self):
        self.longMessage = True
        self.agent = 'TEST_USER_AGENT'
        self.key = 'FAKE_DEV_KEY'
        self.session = 'FAKE_SESSION_ID'
        self.username = 'FAKE_USERNAME'
        self.password = 'FAKE_PASSWORD'
        self.callback = 'FAKE_CALLBACK'
        self.temp_token = 'FAKE_TEMP_TOKEN'
        self.secret = 'FAKE_SECRET'
        self.verifier = 'FAKE_VERIFIER'
        self.real_token = 'FAKE_TOKEN'
        wsgi_intercept.httplib_intercept.install()
        self.fs = familysearch.FamilySearch(self.agent, self.key)

    def tearDown(self):
        clear_request_intercpets()
        wsgi_intercept.httplib_intercept.uninstall()


class TestIdentityProperties(TestIdentity):

    def test_identity_properties(self):
        request_environ = add_request_intercept(sample_identity_properties)
        self.fs.identity_properties
        self.assertTrue(request_environ['PATH_INFO'].endswith('/properties'), 'properties request failed')

    def test_identity_properties_cached(self):
        add_request_intercept(sample_identity_properties)
        self.fs.identity_properties
        request_environ = add_request_intercept(sample_identity_properties)
        self.fs.identity_properties
        self.assertFalse(request_environ, 'properties request not cached')


class TestIdentityLogin(TestIdentity):

    def test_fails_without_username(self):
        add_request_intercept(sample_login)
        self.assertRaises(TypeError, self.fs.login, password=self.password)

    def test_fails_without_password(self):
        add_request_intercept(sample_login)
        self.assertRaises(TypeError, self.fs.login, username=self.username)

    def test_requires_username_and_password(self):
        add_request_intercept(sample_login)
        self.fs.login(self.username, self.password)

    def test_login_request(self):
        request_environ = add_request_intercept(sample_login)
        self.fs.login(self.username, self.password)
        self.assertTrue(request_environ['PATH_INFO'].endswith('/login'), 'login request failed')
        post_data = request_environ['wsgi.input'].read()
        self.assertIn('username=' + self.username, post_data, 'login request failed to pass username')
        self.assertIn('password=' + self.password, post_data, 'login request failed to pass password')
        self.assertIn('key=' + self.key, post_data, 'login request failed to pass developer key')

    def test_successful_login(self):
        add_request_intercept(sample_login)
        self.assertFalse(self.fs.logged_in, 'should not be logged in initially')
        session_id = self.fs.login(self.username, self.password)
        self.assertTrue(self.fs.logged_in, 'should be logged in after login request')
        self.assertEqual(self.fs.session_id, self.session, 'login request failed to set correct session ID')
        self.assertEqual(session_id, self.session, 'login request failed to return correct session ID')

    def test_failed_login(self):
        add_request_intercept('', status='401 Unauthorized')
        self.fs.logged_in = True
        self.assertRaises(urllib2.HTTPError, self.fs.login, self.username, self.password)
        self.assertFalse(self.fs.logged_in, 'should not be logged in after receiving error 401')


class TestIdentityInitialize(TestIdentity):

    def test_takes_no_arguments(self):
        add_request_intercept(sample_login)
        self.assertRaises(TypeError, self.fs.initialize, self.username)
        self.assertRaises(TypeError, self.fs.initialize, self.username, self.password)
        self.fs.initialize()

    def test_initialize_request(self):
        request_environ = add_request_intercept(sample_login)
        self.fs.initialize()
        self.assertTrue(request_environ['PATH_INFO'].endswith('/initialize'), 'initialize request failed')
        post_data = request_environ['wsgi.input'].read()
        self.assertIn('key=' + self.key, post_data, 'initialize request failed to pass developer key')

    def test_successful_initialize(self):
        add_request_intercept(sample_login)
        self.fs.logged_in = True
        session_id = self.fs.initialize()
        self.assertFalse(self.fs.logged_in, 'should not be logged in after initialize request')
        self.assertEqual(self.fs.session_id, self.session, 'initialize request failed to set correct session ID')
        self.assertEqual(session_id, self.session, 'initialize request failed to return correct session ID')


class TestIdentityAuthenticate(TestIdentity):

    def test_fails_without_username(self):
        add_request_intercept(sample_login)
        self.assertRaises(TypeError, self.fs.authenticate, password=self.password)

    def test_fails_without_password(self):
        add_request_intercept(sample_login)
        self.assertRaises(TypeError, self.fs.authenticate, username=self.username)

    def test_requires_username_and_password(self):
        add_request_intercept(sample_login)
        self.fs.authenticate(self.username, self.password)

    def test_authenticate_request(self):
        request_environ = add_request_intercept(sample_login)
        self.fs.authenticate(self.username, self.password)
        self.assertTrue(request_environ['PATH_INFO'].endswith('/authenticate'), 'authenticate request failed')
        post_data = request_environ['wsgi.input'].read()
        self.assertIn('username=' + self.username, post_data, 'authenticate request failed to pass username')
        self.assertIn('password=' + self.password, post_data, 'authenticate request failed to pass password')

    def test_successful_authenticate(self):
        add_request_intercept(sample_login)
        self.fs.session_id = 'TEMP_SESSION_ID'
        self.assertFalse(self.fs.logged_in, 'should not be logged in initially')
        session_id = self.fs.authenticate(self.username, self.password)
        self.assertTrue(self.fs.logged_in, 'should be logged in after authenticate request')
        self.assertEqual(self.fs.session_id, self.session, 'authenticate request failed to set correct session ID')
        self.assertEqual(session_id, self.session, 'authenticate request failed to return correct session ID')

    def test_failed_authenticate(self):
        add_request_intercept('', status='401 Unauthorized')
        self.fs.logged_in = True
        self.assertRaises(urllib2.HTTPError, self.fs.authenticate, self.username, self.password)
        self.assertFalse(self.fs.logged_in, 'should not be logged in after receiving error 401')


class TestIdentityLogout(TestIdentity):

    def test_logout_request(self):
        request_environ = add_request_intercept(sample_login)
        self.fs.logout()
        self.assertTrue(request_environ['PATH_INFO'].endswith('/logout'), 'logout request failed')

    def test_successful_logout(self):
        add_request_intercept(sample_login)
        self.fs.logged_in = True
        self.fs.session_id = self.session
        self.fs.logout()
        self.assertFalse(self.fs.logged_in, 'should not be logged in after logout request')
        self.assertNotEqual(self.fs.session_id, self.session, 'logout request failed to unset session ID')


class TestIdentitySession(TestIdentity):

    def test_session_request(self):
        request_environ = add_request_intercept(sample_login)
        self.fs.session()
        self.assertTrue(request_environ['PATH_INFO'].endswith('/session'), 'session request failed')

    def test_successful_session(self):
        add_request_intercept(sample_login)
        session_id = self.fs.session()
        self.assertTrue(self.fs.logged_in, 'should be logged in after session request')
        self.assertEqual(self.fs.session_id, self.session, 'session request failed to set correct session ID')
        self.assertEqual(session_id, self.session, 'session request failed to return correct session ID')

    def test_failed_session(self):
        add_request_intercept('', status='401 Unauthorized')
        self.fs.logged_in = True
        self.assertRaises(urllib2.HTTPError, self.fs.session)
        self.assertFalse(self.fs.logged_in, 'should not be logged in after receiving error 401')


class TestIdentityRequestToken(TestIdentity):

    def test_request_token_without_callback_request(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        self.fs.request_token()
        self.assertTrue(request_environ['PATH_INFO'].endswith('/request_token'), 'request_token request failed')
        post_data = request_environ['wsgi.input'].read()
        self.assertIn('oauth_callback=oob', post_data, 'request_token request failed to pass callback')
        self.assertIn('oauth_consumer_key=' + self.key, post_data, 'request_token request failed to pass developer key')
        self.assertIn('oauth_nonce=', post_data, 'request_token request failed to pass nonce')
        self.assertIn('oauth_signature=%26', post_data, 'request_token request failed to pass signature')
        self.assertIn('oauth_signature_method=PLAINTEXT', post_data, 'request_token request failed to pass signature method')
        self.assertIn('oauth_timestamp=', post_data, 'request_token request failed to pass timestamp')

    def test_request_token_with_callback_request(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        self.fs.request_token(callback_url=self.callback)
        self.assertTrue(request_environ['PATH_INFO'].endswith('/request_token'), 'request_token request failed')
        post_data = request_environ['wsgi.input'].read()
        self.assertIn('oauth_callback=' + self.callback, post_data, 'request_token request failed to pass correct callback')
        self.assertIn('oauth_consumer_key=' + self.key, post_data, 'request_token request failed to pass developer key')
        self.assertIn('oauth_nonce=', post_data, 'request_token request failed to pass nonce')
        self.assertIn('oauth_signature=%26', post_data, 'request_token request failed to pass signature')
        self.assertIn('oauth_signature_method=PLAINTEXT', post_data, 'request_token request failed to pass signature method')
        self.assertIn('oauth_timestamp=', post_data, 'request_token request failed to pass timestamp')

    def test_request_token_response(self):
        add_request_intercept(sample_identity_properties)
        add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        response = self.fs.request_token()
        self.assertIn('oauth_token', response, 'request_token failed to return token')
        self.assertEqual(response['oauth_token'], self.temp_token, 'request_token failed to return correct token')
        self.assertIn('oauth_token_secret', response, 'request_token failed to return token secret')
        self.assertEqual(response['oauth_token_secret'], self.secret, 'request_token failed to return correct token secret')

    def test_request_token_state(self):
        add_request_intercept(sample_identity_properties)
        add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        self.fs.request_token()
        self.assertFalse(self.fs.logged_in, 'should not be logged in after request_token request')
        self.assertEqual(self.fs.session_id, self.temp_token, 'request_token request failed to set correct session ID')
        self.assertIn(self.temp_token, self.fs.oauth_secrets, 'request_token request failed to set correct OAuth temporary credentials identifier')
        self.assertEqual(self.fs.oauth_secrets[self.temp_token], self.secret, 'request_token request failed to set correct OAuth temporary credentials shared-secret')


class TestIdentityAuthorize(TestIdentity):

    def test_authorize_without_parameters(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        url = self.fs.authorize()
        self.assertTrue(request_environ, 'request_token endpoint not called')
        self.assertEqual(url, 'http://www.dev.usys.org:2/identity/v2/authorize?sessionId=FAKE_TEMP_TOKEN', 'authorize URL incorrect')

    def test_authorize_with_saved_request_token_parameter(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        self.fs.session_id = self.temp_token
        self.fs.oauth_secrets = {self.temp_token: self.secret}
        url = self.fs.authorize()
        self.assertFalse(request_environ, 'request_token endpoint unexpectedly called')
        self.assertEqual(url, 'http://www.dev.usys.org:2/identity/v2/authorize?sessionId=FAKE_TEMP_TOKEN', 'authorize URL incorrect')

    def test_authorize_with_request_token_parameter(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        url = self.fs.authorize(self.temp_token)
        self.assertFalse(request_environ, 'request_token endpoint unexpectedly called')
        self.assertEqual(url, 'http://www.dev.usys.org:2/identity/v2/authorize?sessionId=FAKE_TEMP_TOKEN', 'authorize URL incorrect')

    def test_authorize_with_more_parameters_from_kwargs(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        url = self.fs.authorize(self.temp_token, template='mobile')
        self.assertFalse(request_environ, 'request_token endpoint unexpectedly called')
        self.assertTrue(url.startswith('http://www.dev.usys.org:2/identity/v2/authorize?'), 'authorize URL incorrect')
        self.assertIn('sessionId=FAKE_TEMP_TOKEN', url, 'session ID not included')
        self.assertIn('template=mobile', url, 'additional parameter from kwargs not included')

    def test_authorize_with_more_parameters_from_dict(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        url = self.fs.authorize(self.temp_token, {'template': 'mobile'})
        self.assertFalse(request_environ, 'request_token endpoint unexpectedly called')
        self.assertTrue(url.startswith('http://www.dev.usys.org:2/identity/v2/authorize?'), 'authorize URL incorrect')
        self.assertIn('sessionId=FAKE_TEMP_TOKEN', url, 'session ID not included')
        self.assertIn('template=mobile', url, 'additional parameter from dict not included')

    def test_authorize_with_more_parameters_from_kwargs_and_dict(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_request_token, port=1, headers={'Content-type': 'text/plain'})
        url = self.fs.authorize(self.temp_token, {'template': 'mobile'}, template2='mobile')
        self.assertFalse(request_environ, 'request_token endpoint unexpectedly called')
        self.assertTrue(url.startswith('http://www.dev.usys.org:2/identity/v2/authorize?'), 'authorize URL incorrect')
        self.assertIn('sessionId=FAKE_TEMP_TOKEN', url, 'session ID not included')
        self.assertIn('template=mobile', url, 'additional parameter from dict not included')
        self.assertIn('template2=mobile', url, 'additional parameter from kwargs not included')


class TestIdentityAccessToken(TestIdentity):

    def test_requires_verifier(self):
        add_request_intercept(sample_identity_properties)
        add_request_intercept(sample_access_token, port=3, headers={'Content-type': 'text/plain'})
        self.assertRaises(TypeError, self.fs.access_token)
        self.fs.access_token(self.verifier)

    def test_access_token_saved_request(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_access_token, port=3, headers={'Content-type': 'text/plain'})
        # Use saved request_token and saved secret
        self.fs.session_id = self.temp_token
        self.fs.oauth_secrets = {self.temp_token: self.secret}
        self.fs.access_token(self.verifier)
        self.assertTrue(request_environ['PATH_INFO'].endswith('/access_token'), 'access_token request failed')
        post_data = request_environ['wsgi.input'].read()
        self.assertIn('oauth_consumer_key=' + self.key, post_data, 'access_token request failed to pass developer key')
        self.assertIn('oauth_nonce=', post_data, 'access_token request failed to pass nonce')
        self.assertIn('oauth_signature=%26' + self.secret, post_data, 'access_token request failed to pass signature with OAuth temporary credentials shared-secret')
        self.assertIn('oauth_signature_method=PLAINTEXT', post_data, 'access_token request failed to pass signature method')
        self.assertIn('oauth_timestamp=', post_data, 'access_token request failed to pass timestamp')
        self.assertIn('oauth_token=' + self.temp_token, post_data, 'access_token request failed to pass OAuth temporary credentials identifier')
        self.assertIn('oauth_verifier=' + self.verifier, post_data, 'access_token request failed to pass OAuth verification code')

    def test_access_token_with_session_id_request(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_access_token, port=3, headers={'Content-type': 'text/plain'})
        # Use saved secret but explicit request_token
        self.fs.oauth_secrets = {self.temp_token: self.secret}
        self.fs.access_token(self.verifier, request_token=self.temp_token)
        self.assertTrue(request_environ['PATH_INFO'].endswith('/access_token'), 'access_token request failed')
        post_data = request_environ['wsgi.input'].read()
        self.assertIn('oauth_consumer_key=' + self.key, post_data, 'access_token request failed to pass developer key')
        self.assertIn('oauth_nonce=', post_data, 'access_token request failed to pass nonce')
        self.assertIn('oauth_signature=%26' + self.secret, post_data, 'access_token request failed to pass signature with OAuth temporary credentials shared-secret')
        self.assertIn('oauth_signature_method=PLAINTEXT', post_data, 'access_token request failed to pass signature method')
        self.assertIn('oauth_timestamp=', post_data, 'access_token request failed to pass timestamp')
        self.assertIn('oauth_token=' + self.temp_token, post_data, 'access_token request failed to pass OAuth temporary credentials identifier')
        self.assertIn('oauth_verifier=' + self.verifier, post_data, 'access_token request failed to pass OAuth verification code')

    def test_access_token_with_session_id_and_secret_request(self):
        add_request_intercept(sample_identity_properties)
        request_environ = add_request_intercept(sample_access_token, port=3, headers={'Content-type': 'text/plain'})
        # Used explicit request_token and explicit secret
        self.fs.access_token(self.verifier, request_token=self.temp_token, token_secret=self.secret)
        self.assertTrue(request_environ['PATH_INFO'].endswith('/access_token'), 'access_token request failed')
        post_data = request_environ['wsgi.input'].read()
        self.assertIn('oauth_consumer_key=' + self.key, post_data, 'access_token request failed to pass developer key')
        self.assertIn('oauth_nonce=', post_data, 'access_token request failed to pass nonce')
        self.assertIn('oauth_signature=%26' + self.secret, post_data, 'access_token request failed to pass signature with OAuth temporary credentials shared-secret')
        self.assertIn('oauth_signature_method=PLAINTEXT', post_data, 'access_token request failed to pass signature method')
        self.assertIn('oauth_timestamp=', post_data, 'access_token request failed to pass timestamp')
        self.assertIn('oauth_token=' + self.temp_token, post_data, 'access_token request failed to pass OAuth temporary credentials identifier')
        self.assertIn('oauth_verifier=' + self.verifier, post_data, 'access_token request failed to pass OAuth verification code')

    def test_access_token_response(self):
        add_request_intercept(sample_identity_properties)
        add_request_intercept(sample_access_token, port=3, headers={'Content-type': 'text/plain'})
        response = self.fs.access_token(self.verifier)
        self.assertIn('oauth_token', response, 'access_token failed to return token')
        self.assertEqual(response['oauth_token'], self.real_token, 'access_token failed to return correct token')
        self.assertIn('oauth_token_secret', response, 'access_token failed to return token secret')
        self.assertEqual(response['oauth_token_secret'], self.secret, 'access_token failed to return correct token secret')

    def test_request_token_state(self):
        add_request_intercept(sample_identity_properties)
        add_request_intercept(sample_access_token, port=3, headers={'Content-type': 'text/plain'})
        self.fs.session_id = self.temp_token
        self.fs.oauth_secrets = {self.temp_token: self.secret}
        self.fs.access_token(self.verifier)
        self.assertTrue(self.fs.logged_in, 'should be logged in after access_token request')
        self.assertEqual(self.fs.session_id, self.real_token, 'access_token request failed to set correct session ID')
        self.assertNotIn(self.temp_token, self.fs.oauth_secrets, 'access_token request failed to unset old OAuth temporary credentials identifier')


if __name__ == '__main__':
    unittest.main()
