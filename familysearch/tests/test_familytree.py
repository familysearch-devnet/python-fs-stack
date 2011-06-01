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
        self.assertEqual(len(person_list), 2, 'multiple person response has wrong length')

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


class TestFamilyTreePersona(TestFamilyTree):

    def test_does_not_accept_no_arguments(self):
        add_request_intercept(sample_persona)
        self.assertRaises(TypeError, self.fs.persona)

    def test_does_not_accept_me_persona(self):
        request_environ = add_request_intercept(sample_persona)
        self.fs.persona('me')
        self.assertFalse(request_environ['PATH_INFO'].endswith('persona'), 'persona request should not handle "me" specially')

    def test_accepts_single_persona(self):
        request_environ = add_request_intercept(sample_persona)
        self.fs.persona(self.id)
        self.assertTrue(request_environ['PATH_INFO'].endswith('persona/' + self.id), 'incorrect persona request with single persona ID')

    def test_accepts_list_of_personas(self):
        request_environ = add_request_intercept(sample_persona_list)
        self.fs.persona([self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('persona/' + self.id + ',' + self.id2), 'incorrect persona request with list of persona IDs')

    def test_single_returns_single(self):
        add_request_intercept(sample_persona)
        persona = self.fs.persona(self.id)
        self.assertEqual(type(persona), dict, 'single persona response is wrong type')

    def test_list_returns_list(self):
        add_request_intercept(sample_persona_list)
        persona_list = self.fs.persona([self.id, self.id2])
        self.assertEqual(type(persona_list), list, 'multiple persona response is not a list')
        self.assertEqual(len(persona_list), 2, 'multiple persona response has wrong length')

    def test_adds_one_query_param_from_kwargs(self):
        request_environ = add_request_intercept(sample_persona)
        self.fs.persona(self.id, names='all')
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_kwargs(self):
        request_environ = add_request_intercept(sample_persona)
        self.fs.persona(self.id, names='all', genders='all')
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('=all&', request_environ['QUERY_STRING'], 'multiple query parameters not separated properly')
        self.assertIn('genders=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_one_query_param_from_dict(self):
        request_environ = add_request_intercept(sample_persona)
        self.fs.persona(self.id, {'names': 'all'})
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_dict(self):
        request_environ = add_request_intercept(sample_persona)
        self.fs.persona(self.id, {'names': 'all', 'genders': 'all'})
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('=all&', request_environ['QUERY_STRING'], 'multiple query parameters not separated properly')
        self.assertIn('genders=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_multiple_query_params_from_kwargs_and_dict(self):
        request_environ = add_request_intercept(sample_persona)
        self.fs.persona(self.id, names='all', genders='all', options={'children': 'all', 'parents': 'all'})
        self.assertIn('names=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('genders=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('children=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('parents=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')


class TestFamilyTreeVersion(TestFamilyTree):

    def test_does_not_accept_no_arguments(self):
        add_request_intercept(sample_version)
        self.assertRaises(TypeError, self.fs.version)

    def test_does_not_accept_me_version(self):
        request_environ = add_request_intercept(sample_version)
        self.fs.version('me')
        self.assertFalse(request_environ['PATH_INFO'].endswith('version'), 'person version request should not handle "me" specially')

    def test_accepts_single_person(self):
        request_environ = add_request_intercept(sample_version)
        self.fs.version(self.id)
        self.assertTrue(request_environ['PATH_INFO'].endswith('version/' + self.id), 'incorrect person version request with single person ID')

    def test_accepts_list_of_persons(self):
        request_environ = add_request_intercept(sample_version_list)
        self.fs.version([self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('version/' + self.id + ',' + self.id2), 'incorrect person version request with list of person IDs')

    def test_single_returns_single(self):
        add_request_intercept(sample_version)
        version = self.fs.version(self.id)
        self.assertEqual(type(version), dict, 'single person version response is wrong type')

    def test_list_returns_list(self):
        add_request_intercept(sample_version_list)
        version_list = self.fs.version([self.id, self.id2])
        self.assertEqual(type(version_list), list, 'multiple person version response is not a list')
        self.assertEqual(len(version_list), 2, 'multiple person version response has wrong length')

    def test_does_not_add_accept_kwargs(self):
        add_request_intercept(sample_version)
        self.assertRaises(TypeError, self.fs.version, self.id, names='all')

    def test_does_not_accept_options_dict(self):
        add_request_intercept(sample_version)
        self.assertRaises(TypeError, self.fs.version, self.id, {'names': 'all'})


class TestFamilyTreePedigree(TestFamilyTree):

    def test_accepts_no_arguments(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree()
        self.assertTrue(request_environ['PATH_INFO'].endswith('pedigree'), 'pedigree request failed without a person ID')

    def test_accepts_me_pedigree(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree('me')
        self.assertTrue(request_environ['PATH_INFO'].endswith('pedigree'), 'pedigree request failed with "me"')

    def test_accepts_single_pedigree(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id)
        self.assertTrue(request_environ['PATH_INFO'].endswith('pedigree/' + self.id), 'incorrect pedigree request with single person ID')

    def test_accepts_list_of_pedigrees(self):
        request_environ = add_request_intercept(sample_pedigree_list)
        self.fs.pedigree([self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('pedigree/' + self.id + ',' + self.id2), 'incorrect pedigree request with list of person IDs')

    def test_single_returns_single(self):
        add_request_intercept(sample_pedigree)
        pedigree = self.fs.pedigree(self.id)
        self.assertEqual(type(pedigree), dict, 'single pedigree response is wrong type')

    def test_list_returns_list(self):
        add_request_intercept(sample_pedigree_list)
        pedigree_list = self.fs.pedigree([self.id, self.id2])
        self.assertEqual(type(pedigree_list), list, 'multiple pedigree response is not a list')
        self.assertEqual(len(pedigree_list), 2, 'multiple pedigree response has wrong length')

    def test_adds_one_numeric_query_param_from_kwargs(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id, ancestors=4)
        self.assertIn('ancestors=4', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_one_string_query_param_from_kwargs(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id, properties='all')
        self.assertIn('properties=all', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_kwargs(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id, ancestors=4, properties='all')
        self.assertIn('ancestors=4', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('properties=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_one_numeric_query_param_from_dict(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id, {'ancestors': 4})
        self.assertIn('ancestors=4', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_one_string_query_param_from_dict(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id, {'properties': 'all'})
        self.assertIn('properties=all', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_dict(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id, {'ancestors': 4, 'properties': 'all'})
        self.assertIn('ancestors=4', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('properties=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_query_params_from_kwargs_and_dict(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id, ancestors=4, options={'properties': 'all'})
        self.assertIn('ancestors=4', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('properties=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_query_params_from_dict_and_kwargs(self):
        request_environ = add_request_intercept(sample_pedigree)
        self.fs.pedigree(self.id, {'ancestors': 4}, properties='all')
        self.assertIn('ancestors=4', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('properties=all', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')


if __name__ == '__main__':
    unittest.main()
