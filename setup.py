from distutils.core import setup

setup(name='python-fs-stack',
      version='0.1',
      description='Python wrapper for all FamilySearch APIs',
      url='https://devnet.familysearch.org/downloads/sample-code',
      author='Peter Henderson',
      author_email='peter.henderson@ldschurch.org',
      license='FamilySearch API License Agreement <https://devnet.familysearch.org/downloads/sample-code/sample-clients/sample-client-license>',
      package_dir={'': 'src'},
      packages=['enunciate'],
      scripts=['src/login.py', 'src/login_web.py'],
      )
