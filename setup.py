import familysearch
try:
    # Setuptools or Distribute is required to support running `python setup.py test`
    from setuptools import setup
except ImportError:
    # Distutils supports everything else; just run the test suite manually
    from distutils.core import setup

setup(
    name='python-fs-stack',
    version=familysearch.__version__,
    description='Python wrapper for all FamilySearch APIs',
    long_description=open('README.rst').read(),
    url='https://devnet.familysearch.org/downloads/sample-code',
    author='Peter Henderson',
    author_email='peter.henderson@ldschurch.org',
    license='FamilySearch API License Agreement <https://devnet.familysearch.org/downloads/sample-code/sample-clients/sample-client-license>',
    packages=['familysearch', 'familysearch.enunciate', 'familysearch.tests'],
    scripts=['examples/login.py', 'examples/login_web.py'],
    test_suite='familysearch.tests',
    tests_require=['wsgi_intercept'],
    package_data={'familysearch.tests': ['*.json']},
)
