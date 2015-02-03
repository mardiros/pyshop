import sys
import os
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
NAME = 'pyshop'

with open(os.path.join(here, 'README.rst')) as readme:
    README = readme.read()
with open(os.path.join(here, 'CHANGES.rst')) as changes:
    CHANGES = changes.read()

with open(os.path.join(here, 'pyshop', '__init__.py')) as version:
    VERSION = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(version.read()).group(1)

requires = [
    'pyramid >= 1.2',
    'SQLAlchemy',

    'pyramid_filterwarnings',
    'pyramid_jinja2',
    'pyramid_xmlrpc',
    'pyramid_tm',
    'zope.sqlalchemy',

    'cryptacular',
    'requests',
    'docutils',
    'setuptools',            # compare package version
]


test_requires = ['nose']
if sys.version_info < (2, 7):
    test_requires.append('unittest2')


extras_require = {
    'ldap': [
        'python-ldap',
    ],
    'waitress': [
        'waitress',
    ],
    'dev': [
        'waitress',
        'pyramid_debugtoolbar',
    ],
    'shell': [
        'IPython',
    ],
    'wheelify': [
        'wheel',             # build wheels from source on the proxy
    ],
    'test': test_requires
}


if 'VIRTUAL_ENV' in os.environ:
    venv = os.environ['VIRTUAL_ENV']
    data_files = [(venv, ['pyshop.sample.ini',
                          ])]
else:
    data_files = []


setup(name=NAME,
      version=VERSION,
      description='Private Python Package Index',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
      'Programming Language :: Python',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.3',
      'Programming Language :: Python :: 3.4',
      'Development Status :: 5 - Production/Stable',
      'Environment :: Web Environment',
      'Framework :: Pyramid',
      'Topic :: Internet :: WWW/HTTP',
      'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
      'Topic :: Software Development',
      'Topic :: System :: Archiving :: Mirroring',
      'Topic :: System :: Archiving :: Packaging',
      'Intended Audience :: Developers',
      'Intended Audience :: System Administrators',
      'License :: OSI Approved :: BSD License',
      ],
      author='Guillaume Gauvrit',
      author_email='ggauvrit@laposte.net',
      url='https://github.com/mardiros/pyshop',
      keywords='web wsgi pyramid cheeseshop pypi packaging',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite=NAME,
      install_requires=requires,
      tests_require=test_requires,
      extras_require=extras_require,
      entry_points={
        'paste.app_factory': [
            "main = pyshop:main",
        ],
        'console_scripts': [
            "pyshop_setup = pyshop.bin.install:main",
            "pyshop_shell = pyshop.bin.shell:main [shell]",
            "pyshop_migrate = pyshop.bin.migrate:main",
        ],
      },
      paster_plugins=['pyramid'],
      data_files=data_files,
      )
