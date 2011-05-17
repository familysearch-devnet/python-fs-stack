import familysearch
import os.path
import unittest
import urllib2
import wsgi_intercept
from wsgi_intercept.urllib2_intercept import WSGI_HTTPHandler, WSGI_HTTPSHandler
try:
    import json
except ImportError:
    import simplejson as json

try:
    import pkg_resources
    sample_person1 = pkg_resources.resource_string(__name__, 'person1.json')
    sample_person2 = pkg_resources.resource_string(__name__, 'person2.json')
except ImportError:
    data_dir = os.path.dirname(__file__)
    sample_person1 = open(os.path.join(data_dir, 'person1.json')).read()
    sample_person2 = open(os.path.join(data_dir, 'person2.json')).read()

class TestFamilySearch(unittest.TestCase):

    def setUp(self):
        self.longMessage = True
        self.agent = 'TEST_USER_AGENT'
        self.key = 'FAKE_DEV_KEY'
        self.session = 'FAKE_SESSION_ID'

    def tearDown(self):
        self.clear_request_intercpets()

    def add_request_intercept(self, response, out_environ=None, status='200 OK',
                              host='api.familysearch.org', port=443,
                              headers={'Content-Type': 'application/json'}):
        '''Globally install a request intercept returning the provided response.'''
        if out_environ is None:
            out_environ = {}
        def mock_app(environ, start_response):
            out_environ.update(environ)
            start_response(status, dict(headers).items())
            return iter(response)
        wsgi_intercept.add_wsgi_intercept(host, port, lambda: mock_app)
        return out_environ

    def clear_request_intercpets(self):
        '''Remove all installed request intercepts.'''
        wsgi_intercept.remove_wsgi_intercept()

    def install_intercept_handler(self, fs):
        '''Add the request intercept handler to the given FamilySearch instance.'''
        new_handlers = [WSGI_HTTPHandler(), WSGI_HTTPSHandler()] + fs.opener.handlers
        fs.opener = urllib2.build_opener(*new_handlers)

    def test_requires_user_agent(self):
        self.assertRaises(TypeError, familysearch.FamilySearch, key=self.key)

    def test_requires_dev_key(self):
        self.assertRaises(TypeError, familysearch.FamilySearch, agent=self.agent)

    def test_accepts_user_agent_and_dev_key(self):
        familysearch.FamilySearch(agent=self.agent, key=self.key)

    def test_changes_base(self):
        self.add_request_intercept(sample_person1, host='www.dev.usys.org', port=80)
        self.add_request_intercept(sample_person2, host='api.familysearch.org', port=443)
        fs_dev = familysearch.FamilySearch(self.agent, self.key)
        fs_prod = familysearch.FamilySearch(self.agent, self.key, base='https://api.familysearch.org:443')
        self.install_intercept_handler(fs_dev)
        self.install_intercept_handler(fs_prod)
        person1 = fs_dev.person()
        person2 = fs_prod.person()
        self.assertNotEqual(person1, person2, 'base argument failed to change base URL')
        self.assertEqual(person1['id'], json.loads(sample_person1)['persons'][0]['id'], 'wrong person returned from default base')
        self.assertEqual(person2['id'], json.loads(sample_person2)['persons'][0]['id'], 'wrong person returned from production base')

    def test_includes_user_agent(self):
        request_environ = self.add_request_intercept(sample_person1)
        fs = familysearch.FamilySearch(self.agent, self.key, base='https://api.familysearch.org:443')
        self.install_intercept_handler(fs)
        fs.person()
        self.assertIn(self.agent, fs.agent, 'user agent not included in internal user agent')
        self.assertIn('HTTP_USER_AGENT', request_environ, 'user agent header not included in request')
        self.assertIn(self.agent, request_environ['HTTP_USER_AGENT'], 'user agent not included in user agent header')

    def test_restoring_session_sets_logged_in(self):
        fs = familysearch.FamilySearch(self.agent, self.key)
        self.assertFalse(fs.logged_in, 'should not be logged in by default')
        fs = familysearch.FamilySearch(self.agent, self.key, session=self.session)
        self.assertTrue(fs.logged_in, 'should be logged in after restoring session')

if __name__ == '__main__':
    unittest.main()
