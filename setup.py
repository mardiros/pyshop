import os
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

with open(os.path.join(here, 'pyshop', '__init__.py')) as v_file:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(v_file.read()).group(1)

requires = [
    'pyramid',
    'SQLAlchemy',
    'pyramid_debugtoolbar',
    'pyramid_scss',
    'pyramid_jinja2',
    'pyramid_xmlrpc',

    'pyramid_tm',
    'zope.sqlalchemy',

    'cryptacular',
    'requests',
    'docutils',

    # used by the shell
    'IPython',
]


if 'VIRTUAL_ENV' in os.environ:
    venv = os.environ['VIRTUAL_ENV']
    data_files = [(venv, ['production.ini',
                          'development.ini',
                          ])]
else:
    data_files = []


setup(name='pyshop',
      version=version,
      description='pyshop',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
      "Programming Language :: Python",
      "Development Status :: 3 - Alpha",
      "Framework :: Pyramid",
      "Topic :: Internet :: WWW/HTTP",
      "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      "Topic :: Software Development",
      "Intended Audience :: Developers",
      "Intended Audience :: System Administrators"
      ],
      author='Guillaume GAUVRIT',
      author_email='ggauvrit@laposte.net',
      url='',
      keywords='web wsgi bfg pylons pyramid cheeseshop pypi',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='pyshop',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = pyshop:main
      [console_scripts]
      initialize_pyshop_db = pyshop.bin.install:main
      pyshop_shell = pyshop.bin.shell:main
      """,
      paster_plugins=['pyramid'],
      data_files=data_files,
      )
