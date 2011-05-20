import familysearch
import unittest
import urllib2
import wsgi_intercept.httplib_intercept
try:
    import json
except ImportError:
    import simplejson as json
from common import *

class TestFamilySearch(unittest.TestCase):

    def setUp(self):
        self.longMessage = True
        self.agent = 'TEST_USER_AGENT'
        self.key = 'FAKE_DEV_KEY'
        self.session = 'FAKE_SESSION_ID'
        self.username = 'FAKE_USERNAME'
        self.password = 'FAKE_PASSWORD'
        self.cookie = 'FAKE_COOKIE=FAKE_VALUE'
        wsgi_intercept.httplib_intercept.install()

    def tearDown(self):
        clear_request_intercpets()
        wsgi_intercept.httplib_intercept.uninstall()

    def test_requires_user_agent(self):
        self.assertRaises(TypeError, familysearch.FamilySearch, key=self.key)

    def test_requires_dev_key(self):
        self.assertRaises(TypeError, familysearch.FamilySearch, agent=self.agent)

    def test_accepts_user_agent_and_dev_key(self):
        familysearch.FamilySearch(agent=self.agent, key=self.key)

    def test_changes_base(self):
        add_request_intercept(sample_person1, host='www.dev.usys.org', port=80)
        add_request_intercept(sample_person2, host='api.familysearch.org', port=443)
        fs_dev = familysearch.FamilySearch(self.agent, self.key)
        fs_prod = familysearch.FamilySearch(self.agent, self.key, base='https://api.familysearch.org')
        person1 = fs_dev.person()
        person2 = fs_prod.person()
        self.assertNotEqual(person1, person2, 'base argument failed to change base URL')
        self.assertEqual(person1['id'], json.loads(sample_person1)['persons'][0]['id'], 'wrong person returned from default base')
        self.assertEqual(person2['id'], json.loads(sample_person2)['persons'][0]['id'], 'wrong person returned from production base')

    def test_includes_user_agent(self):
        request_environ = add_request_intercept(sample_person1)
        fs = familysearch.FamilySearch(self.agent, self.key)
        fs.person()
        self.assertIn(self.agent, fs.agent, 'user agent not included in internal user agent')
        self.assertIn('HTTP_USER_AGENT', request_environ, 'user agent header not included in request')
        self.assertIn(self.agent, request_environ['HTTP_USER_AGENT'], 'user agent not included in user agent header')

    def test_restoring_session_sets_logged_in(self):
        fs = familysearch.FamilySearch(self.agent, self.key)
        self.assertFalse(fs.logged_in, 'should not be logged in by default')
        fs = familysearch.FamilySearch(self.agent, self.key, session=self.session)
        self.assertTrue(fs.logged_in, 'should be logged in after restoring session')

    def test_username_and_password_set_logged_in(self):
        add_request_intercept(sample_login)
        fs = familysearch.FamilySearch(self.agent, self.key, self.username, self.password)
        self.assertTrue(fs.logged_in, 'should be logged in after providing username and password')

    def test_requests_json_format(self):
        request_environ = add_request_intercept(sample_person1)
        fs = familysearch.FamilySearch(self.agent, self.key, session=self.session)
        fs.person()
        self.assertIn('QUERY_STRING', request_environ, 'query string not included in request')
        self.assertIn('dataFormat=application%2Fjson', request_environ['QUERY_STRING'], 'dataFormat not included in query string')

    def test_not_logged_in_if_error_401(self):
        add_request_intercept('', status='401 Unauthorized')
        fs = familysearch.FamilySearch(self.agent, self.key, session=self.session)
        self.assertTrue(fs.logged_in, 'should be logged in after restoring session')
        self.assertRaises(urllib2.HTTPError, fs.person)
        self.assertFalse(fs.logged_in, 'should not be logged after receiving error 401')

    def test_passes_cookies_back(self):
        fs = familysearch.FamilySearch(self.agent, self.key)

        # First request sets a cookie
        headers = default_headers.copy()
        headers['Set-Cookie'] = self.cookie + '; Path=/'
        add_request_intercept(sample_login, headers=headers)
        fs.login(self.username, self.password)

        # Second request should receive the cookie back
        request_environ = add_request_intercept(sample_person1)
        fs.person()
        self.assertIn('HTTP_COOKIE', request_environ, 'cookie header not included in request')
        self.assertIn(self.cookie, request_environ['HTTP_COOKIE'], 'previously-set cookie not included in cookie header')

if __name__ == '__main__':
    unittest.main()
