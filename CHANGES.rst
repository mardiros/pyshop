Changelist
==========

0.9.12
------

- Authorize developper to upload a patched version of a mirrored package
  without any restriction. Some mirrored package may have bugs that are
  critical for you, and it's better to get a mirrored package than rely
  on an external sources.

0.9.11
------

- Fix support of SQLAlchemy 0.9.x
- Fix packaging (missing LICENSE)

0.9.10
------

- Fix postgresql admin account pages

0.9.8
-----

- Add support for posgresql


0.9.7
-----

- Remove some links in the simple route.

  - Don't display home pages
  - Don't display download links in case there is archive available.
    (That fix some install for south for example)

0.9.6
-----

- Fix mirroring of package when the case and underscore are not "correct"


0.9.5
-----

- Fix mirroring of external links browsed (in case it's not a package)


0.9.4
-----

- Fix packaging

0.9.3
-----

- Fix tests for python 2.6 (unittest2 required and be installed manually)
- Fix pyramid 1.2 compatibility
- Rename command pyshop_install to python_setup
- Give the possibility to use the prefix_route via the settings 'pyshop.prefix_route'
- Give the possibility to disable xmlrpc servive via 'pyshop.enable_xmlrpc'


0.9.2
-----

- Tolerant underscore/hyphen usage in package name
- Tolerant with trailing slash in urls


0.9.1
-----

 - Fix unit tests

0.9
---

- add key "pyshop.mirror.cache.ttl" in config file.
  This settings allow to set the cache time of a package
  before refresh it on pypi.
- add a button in the web interface to force the refresh of mirrored package.
  This permit to force reset the ttl of a package on the web interface.
- add key "pyshop.upload.rewrite_filename" in config file.
  This settings disable the rename of package file uploaded on the server.
- change "satanize" to "sanitize" keys in config file.
  Modify this settings in your config file after a migration.
- add key "pyshop.mirror.wheelify" in config file.
  This settings require users to use recent version of pip and setuptools
  virtualenv 1.10.1 is OK. This is experimental.
  User and Proxy Server must run the same OS on the same architecture to
  use that feature.

0.8
---

- Use requests for xmlrpc queries too.
  - validate certificate if https is used
  - unified proxies configuration (use environment vars)
- SAWarning/DeprecationWarning removed
  - Fix mirroring link for external files

0.7.6
-----

- Mirror the download_url of the release file
- Handle hiphen and underscore [fizyk]
- Enhance mimetime handling [fizyk]
- Bugfixes and DeprecationWarning removed

0.7.5
-----

- Fix package version comparison
- Handle bdist_wheel format

To handle the wheel format, (some package like Twisted 13 use it),
for previous install, you must run a migration script like this.

::

    $ pyshop_migrate development.ini 0.7.5

The sqlite database file will be altered, YOU MAY backup it before run the
script.

0.7.4
-----

- Fix local package usage (broken since 0.7.1) [fizyk]

0.7.3
-----

- Remove all certificates and extra handling for PyPI validation as PyPI now
  uses a certificate that can be validated without these.  [disko]

0.7.2
-----

- Remove unused certificates for pypi validation

0.7.1
-----
- Securize download from pypi by forcing https and validate certificate
  pypi.python.org certificate chain is embed in the pyshop package
- Fix package order on web page

0.7
---

- Sanitize version number on upload.
  This is configurable with settings ``pyshop.upload.satanize``
  and ``pyshop.upload.satanize.regex``
- Settings ``pyshop.satanize`` and ``pyshop.satanize.regex`` have been renamed
  to ``pyshop.mirror.satanize`` and  ``pyshop.mirror.satanize.regex``

0.6
---

- Fix first connection of the web application
- Fix the usage of http proxy (forcing request version)

0.5
---

- Add Link to display all release versions
- Improve navigation
- Fix ugly version number sorting

0.4
---

- Fix release file upgrade (allow developper to override release file)
- Rename user views to account
- Add view to let the connected user to update his account

0.3
---

- The setting ``pyshop.satanize.reg`` has been renamed to
  ``pyshop.satanize.regex``
- The setting ``cookie_key`` has been renamed to ``pyshop.cookie_key``
- Fix bug on package upload. don't close the stream while writing it.
- Add basic tests on packages view

0.2
---

Packaging Issue.

0.1
---

Initial version.

- work with pip, setuptools
- mirror packages
- upload packages
- secure access with login/password
- create/update accounts
- tests for python 2.7 only
- compatible with python 2.6
