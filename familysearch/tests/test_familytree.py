import familysearch
import unittest
import wsgi_intercept.httplib_intercept
try:
    import json
except ImportError:
    import simplejson as json
from common import *


class TestFamilyTree(unittest.TestCase):

    def setUp(self):
        self.longMessage = True
        self.agent = 'TEST_USER_AGENT'
        self.key = 'FAKE_DEV_KEY'
        self.session = 'FAKE_SESSION_ID'
        self.id = 'FAKE_PERSON_ID'
        self.id2 = 'FAKE_PERSON_ID_2'
        wsgi_intercept.httplib_intercept.install()
        self.fs = familysearch.FamilySearch(self.agent, self.key, session=self.session)

    def tearDown(self):
        clear_request_intercpets()
        wsgi_intercept.httplib_intercept.uninstall()


class TestFamilyTreePerson(TestFamilyTree):

    def test_accepts_no_arguments(self):
        request_environ = add_request_intercept(sample_person1)
        self.fs.person()
        self.assertTrue(request_environ['PATH_INFO'].endswith('person'), 'person request failed without a person ID')

    def test_accepts_me_person(self):
        request_environ = add_request_intercept(sample_person1)
        self.fs.person('me')
        self.assertTrue(request_environ['PATH_INFO'].endswith('person'), 'person request failed with "me"')

    def test_accepts_single_person(self):
        request_environ = add_request_intercept(sample_person1)
        self.fs.person(self.id)
        self.assertTrue(request_environ['PATH_INFO'].endswith('person/' + self.id), 'incorrect person request with single person ID')

    def test_accepts_list_of_persons(self):
        request_environ = add_request_intercept(sample_person_list)
        self.fs.person([self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('person/' + self.id + ',' + self.id2), 'incorrect person request with list of person IDs')

    def test_single_returns_single(self):
        add_request_intercept(sample_person1)
        person = self.fs.person(self.id)
        self.assertEqual(type(person), dict, 'single person response is wrong type')

    def test_list_returns_list(self):
        add_request_intercept(sample_person_list)
        person_list = self.fs.person([self.id, self.id2])
        self.assertEqual(type(person_list), list, 'multiple person response is not a list')

    def test_adds_one_query_param_from_kwargs(self):
        request_environ = add_request_intercept(sample_person1)
        self.fs.person(self.id, names='all')
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_kwargs(self):
        request_environ = add_request_intercept(sample_person1)
        self.fs.person(self.id, names='all', genders='all')
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('=all&', request_environ['QUERY_STRING'], 'multiple query parameters not separated properly')
        self.assertIn('genders=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_one_query_param_from_dict(self):
        request_environ = add_request_intercept(sample_person1)
        self.fs.person(self.id, {'names': 'all'})
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_dict(self):
        request_environ = add_request_intercept(sample_person1)
        self.fs.person(self.id, {'names': 'all', 'genders': 'all'})
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('=all&', request_environ['QUERY_STRING'], 'multiple query parameters not separated properly')
        self.assertIn('genders=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_multiple_query_params_from_kwargs_and_dict(self):
        request_environ = add_request_intercept(sample_person1)
        self.fs.person(self.id, names='all', genders='all', options={'children': 'all', 'parents': 'all'})
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('genders=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('children=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('parents=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')


if __name__ == '__main__':
    unittest.main()
