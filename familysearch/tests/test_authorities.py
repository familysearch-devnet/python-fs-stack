import familysearch
import unittest
import wsgi_intercept.httplib_intercept
try:
    import json
except ImportError:
    import simplejson as json
from common import *

sample_place = load_sample('place.json')
sample_place_list = load_sample('place_list.json')
sample_name = load_sample('name.json')
sample_name_list = load_sample('name_list.json')
sample_date = load_sample('date.json')
sample_date_list = load_sample('date_list.json')
sample_culture = load_sample('culture.json')
sample_culture_list = load_sample('culture_list.json')


class TestAuthorities(unittest.TestCase):

    def setUp(self):
        self.longMessage = True
        self.agent = 'TEST_USER_AGENT'
        self.key = 'FAKE_DEV_KEY'
        self.session = 'FAKE_SESSION_ID'
        self.id = 'FAKE_ID'
        self.id2 = 'FAKE_ID_2'
        wsgi_intercept.httplib_intercept.install()
        self.fs = familysearch.FamilySearch(self.agent, self.key, session=self.session)

    def tearDown(self):
        clear_request_intercpets()
        wsgi_intercept.httplib_intercept.uninstall()


class TestAuthoritiesPlace(TestAuthorities):

    def test_accepts_single_place(self):
        request_environ = add_request_intercept(sample_place)
        self.fs.place(self.id)
        self.assertTrue(request_environ['PATH_INFO'].endswith('place/' + self.id), 'incorrect place request with single place ID')

    def test_accepts_list_of_places(self):
        request_environ = add_request_intercept(sample_place_list)
        self.fs.place([self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('place/' + self.id + ',' + self.id2), 'incorrect place request with list of place IDs')

    def test_accepts_list_of_place_names_in_kwargs(self):
        request_environ = add_request_intercept(sample_place_list)
        self.fs.place(place=[self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('place'), 'incorrect place request with list of place names')
        self.assertIn('place=' + self.id, request_environ['QUERY_STRING'], 'one of multiple place names not included')
        self.assertIn('place=' + self.id2, request_environ['QUERY_STRING'], 'one of multiple place names not included')

    def test_accepts_list_of_place_names_in_dict(self):
        request_environ = add_request_intercept(sample_place_list)
        self.fs.place(options={'place': [self.id, self.id2]})
        self.assertTrue(request_environ['PATH_INFO'].endswith('place'), 'incorrect place request with list of place names')
        self.assertIn('place=' + self.id, request_environ['QUERY_STRING'], 'one of multiple place names not included')
        self.assertIn('place=' + self.id2, request_environ['QUERY_STRING'], 'one of multiple place names not included')

    def test_single_returns_single(self):
        add_request_intercept(sample_place)
        place = self.fs.place(self.id)
        self.assertEqual(type(place), dict, 'single place response is wrong type')

    def test_list_returns_list(self):
        add_request_intercept(sample_place_list)
        place_list = self.fs.place([self.id, self.id2])
        self.assertEqual(type(place_list), list, 'multiple place response is not a list')
        self.assertEqual(len(place_list), 2, 'multiple place response has wrong length')

    def test_adds_one_query_param_from_kwargs(self):
        request_environ = add_request_intercept(sample_place)
        self.fs.place(place='London')
        self.assertIn('place=London', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_kwargs(self):
        request_environ = add_request_intercept(sample_place)
        self.fs.place(place='London', view='full')
        self.assertIn('place=London', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('view=full', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_one_query_param_from_dict(self):
        request_environ = add_request_intercept(sample_place)
        self.fs.place(options={'place': 'London'})
        self.assertIn('place=London', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_dict(self):
        request_environ = add_request_intercept(sample_place)
        self.fs.place(options={'place': 'London', 'view': 'full'})
        self.assertIn('place=London', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('view=full', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_multiple_query_params_from_kwargs_and_dict(self):
        request_environ = add_request_intercept(sample_place)
        self.fs.place(place='London', view='full', options={'variants': 'true', 'children': 'true'})
        self.assertIn('place=London', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('view=full', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('variants=true', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('children=true', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')


class TestAuthoritiesName(TestAuthorities):

    def test_accepts_list_of_names_in_kwargs(self):
        request_environ = add_request_intercept(sample_name_list)
        self.fs.name(name=[self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('name'), 'incorrect name request with list of names')
        self.assertIn('name=' + self.id, request_environ['QUERY_STRING'], 'one of multiple names not included')
        self.assertIn('name=' + self.id2, request_environ['QUERY_STRING'], 'one of multiple names not included')

    def test_accepts_list_of_names_in_dict(self):
        request_environ = add_request_intercept(sample_name_list)
        self.fs.name(options={'name': [self.id, self.id2]})
        self.assertTrue(request_environ['PATH_INFO'].endswith('name'), 'incorrect name request with list of names')
        self.assertIn('name=' + self.id, request_environ['QUERY_STRING'], 'one of multiple names not included')
        self.assertIn('name=' + self.id2, request_environ['QUERY_STRING'], 'one of multiple names not included')

    def test_single_returns_single(self):
        add_request_intercept(sample_name)
        name = self.fs.name(name=self.id)
        self.assertEqual(type(name), dict, 'single name response is wrong type')

    def test_list_returns_list(self):
        add_request_intercept(sample_name_list)
        name_list = self.fs.name(name=[self.id, self.id2])
        self.assertEqual(type(name_list), list, 'multiple name response is not a list')
        self.assertEqual(len(name_list), 2, 'multiple name response has wrong length')

    def test_adds_one_query_param_from_kwargs(self):
        request_environ = add_request_intercept(sample_name)
        self.fs.name(name='John Smith')
        self.assertIn('name=John+Smith', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_kwargs(self):
        request_environ = add_request_intercept(sample_name)
        self.fs.name(name='John Smith', variants='false')
        self.assertIn('name=John+Smith', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('variants=false', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_one_query_param_from_dict(self):
        request_environ = add_request_intercept(sample_name)
        self.fs.name(options={'name': 'John Smith'})
        self.assertIn('name=John+Smith', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_dict(self):
        request_environ = add_request_intercept(sample_name)
        self.fs.name(options={'name': 'John Smith', 'variants': 'false'})
        self.assertIn('name=John+Smith', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('variants=false', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_multiple_query_params_from_kwargs_and_dict(self):
        request_environ = add_request_intercept(sample_name)
        self.fs.name(name='John Smith', culture=1, options={'variants': 'true', 'test': 'test'})
        self.assertIn('name=John+Smith', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('culture=1', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('variants=true', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('test=test', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')


class TestAuthoritiesDate(TestAuthorities):

    def test_accepts_list_of_dates_in_kwargs(self):
        request_environ = add_request_intercept(sample_date_list)
        self.fs.date(date=[self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('date'), 'incorrect date request with list of dates')
        self.assertIn('date=' + self.id, request_environ['QUERY_STRING'], 'one of multiple dates not included')
        self.assertIn('date=' + self.id2, request_environ['QUERY_STRING'], 'one of multiple dates not included')

    def test_accepts_list_of_dates_in_dict(self):
        request_environ = add_request_intercept(sample_date_list)
        self.fs.date(options={'date': [self.id, self.id2]})
        self.assertTrue(request_environ['PATH_INFO'].endswith('date'), 'incorrect date request with list of dates')
        self.assertIn('date=' + self.id, request_environ['QUERY_STRING'], 'one of multiple dates not included')
        self.assertIn('date=' + self.id2, request_environ['QUERY_STRING'], 'one of multiple dates not included')

    def test_single_returns_single(self):
        add_request_intercept(sample_date)
        date = self.fs.date(date=self.id)
        self.assertEqual(type(date), dict, 'single date response is wrong type')

    def test_list_returns_list(self):
        add_request_intercept(sample_date_list)
        date_list = self.fs.date(date=[self.id, self.id2])
        self.assertEqual(type(date_list), list, 'multiple date response is not a list')
        self.assertEqual(len(date_list), 2, 'multiple date response has wrong length')

    def test_adds_one_query_param_from_kwargs(self):
        request_environ = add_request_intercept(sample_date)
        self.fs.date(date='1 Jan 2000')
        self.assertIn('date=1+Jan+2000', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_kwargs(self):
        request_environ = add_request_intercept(sample_date)
        self.fs.date(date='1 Jan 2000', astro=2451545)
        self.assertIn('date=1+Jan+2000', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('astro=2451545', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_one_query_param_from_dict(self):
        request_environ = add_request_intercept(sample_date)
        self.fs.date(options={'date': '1 Jan 2000'})
        self.assertIn('date=1+Jan+2000', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_dict(self):
        request_environ = add_request_intercept(sample_date)
        self.fs.date(options={'date': '1 Jan 2000', 'astro': 2451545})
        self.assertIn('date=1+Jan+2000', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('astro=2451545', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_multiple_query_params_from_kwargs_and_dict(self):
        request_environ = add_request_intercept(sample_date)
        self.fs.date(date='1 Jan 2000', astro=2451545, options={'locale': 'en', 'test': 'test'})
        self.assertIn('date=1+Jan+2000', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('astro=2451545', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('locale=en', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('test=test', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')


class TestAuthoritiesCulture(TestAuthorities):

    def test_accepts_no_arguments(self):
        request_environ = add_request_intercept(sample_culture)
        self.fs.culture()
        self.assertTrue(request_environ['PATH_INFO'].endswith('culture'), 'culture request failed without a culture ID')

    def test_accepts_single_culture(self):
        request_environ = add_request_intercept(sample_culture)
        self.fs.culture(self.id)
        self.assertTrue(request_environ['PATH_INFO'].endswith('culture/' + self.id), 'incorrect culture request with single culture ID')

    def test_accepts_list_of_cultures(self):
        request_environ = add_request_intercept(sample_culture_list)
        self.fs.culture([self.id, self.id2])
        self.assertTrue(request_environ['PATH_INFO'].endswith('culture/' + self.id + ',' + self.id2), 'incorrect culture request with list of culture IDs')

    def test_single_returns_single(self):
        add_request_intercept(sample_culture)
        culture = self.fs.culture(self.id)
        self.assertEqual(type(culture), dict, 'single culture response is wrong type')

    def test_list_returns_list(self):
        add_request_intercept(sample_culture_list)
        culture_list = self.fs.culture([self.id, self.id2])
        self.assertEqual(type(culture_list), list, 'multiple culture response is not a list')
        self.assertEqual(len(culture_list), 2, 'multiple culture response has wrong length')

    def test_adds_one_query_param_from_kwargs(self):
        request_environ = add_request_intercept(sample_culture)
        self.fs.culture(test1='test1')
        self.assertIn('test1=test1', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_kwargs(self):
        request_environ = add_request_intercept(sample_culture)
        self.fs.culture(test1='test1', test2='test2')
        self.assertIn('test1=test1', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('test2=test2', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_one_query_param_from_dict(self):
        request_environ = add_request_intercept(sample_culture)
        self.fs.culture(options={'test1': 'test1'})
        self.assertIn('test1=test1', request_environ['QUERY_STRING'], 'single query parameter not included')

    def test_adds_multiple_query_params_from_dict(self):
        request_environ = add_request_intercept(sample_culture)
        self.fs.culture(options={'test1': 'test1', 'test2': 'test2'})
        self.assertIn('test1=test1', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('test2=test2', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')

    def test_adds_multiple_query_params_from_kwargs_and_dict(self):
        request_environ = add_request_intercept(sample_culture)
        self.fs.culture(test1='test1', test2='test2', options={'test3': 'test3', 'test4': 'test4'})
        self.assertIn('test1=test1', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('test2=test2', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('test3=test3', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')
        self.assertIn('test4=test4', request_environ['QUERY_STRING'], 'one of multiple query parameters not included')


if __name__ == '__main__':
    unittest.main()
