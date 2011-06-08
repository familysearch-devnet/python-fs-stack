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
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Sociology :: Genealogy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords=['FamilySearch', 'genealogy', 'family history', 'API', 'OAuth', 'REST', 'JSON'],
    packages=['familysearch', 'familysearch.enunciate', 'familysearch.tests'],
    scripts=['examples/login.py', 'examples/login_web.py'],
    test_suite='familysearch.tests',
    tests_require=['wsgi_intercept'],
    package_data={'familysearch.tests': ['*.json']},
)
