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


if __name__ == '__main__':
    unittest.main()
