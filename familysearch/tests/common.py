"""Common functions used by tests in multiple test suites"""

import wsgi_intercept

try:
    import pkg_resources
    def load_sample(filename):
        return pkg_resources.resource_string(__name__, filename)
except ImportError:
    import os.path
    data_dir = os.path.dirname(__file__)
    def load_sample(filename):
        return open(os.path.join(data_dir, filename)).read()

sample_person1 = load_sample('person1.json')
sample_person2 = load_sample('person2.json')
sample_person_list = load_sample('person_list.json')
sample_persona1 = load_sample('persona1.json')
sample_persona2 = load_sample('persona2.json')
sample_persona_list = load_sample('persona_list.json')
sample_version1 = load_sample('version1.json')
sample_version2 = load_sample('version2.json')
sample_version_list = load_sample('version_list.json')
sample_pedigree1 = load_sample('pedigree1.json')
sample_pedigree2 = load_sample('pedigree2.json')
sample_pedigree_list = load_sample('pedigree_list.json')
sample_login = load_sample('login.json')
sample_identity_properties = load_sample('identity_properties.json')
sample_request_token = load_sample('request_token.txt')

default_headers = {'Content-Type': 'application/json'}

def add_request_intercept(response, out_environ=None, status='200 OK',
                          host='www.dev.usys.org', port=80,
                          headers=default_headers):
    """Globally install a request intercept returning the provided response."""
    if out_environ is None:
        out_environ = {}
    def mock_app(environ, start_response):
        out_environ.update(environ)
        start_response(status, dict(headers).items())
        return iter(response)
    wsgi_intercept.add_wsgi_intercept(host, port, lambda: mock_app)
    return out_environ

def clear_request_intercpets():
    """Remove all installed request intercepts."""
    wsgi_intercept.remove_wsgi_intercept()

