pyshop
======

Getting Started
---------------

Pyshop is a private packaging repository for python.

The aim is to split private projects in distinct private package and keep a
setup.py clean and working, by declaring all dependancies, exactly as public
package from PyPI.

Pyshop also mirror packages from PyPI safety (using ssl by checking
certificate).

Pyshop use clear and simple ACL to manage privilleges:

-   an installer group that can only download release file
-   a developer group that can download/upload release file and browse the
    website and
-   an admin group that have developer privilleges and accounts management.

So, every users, including "pip", must be authenticated by login and password.

Installation
------------

::

    $ virtualenv pyshop
    $ cd pyshop
    (pyshop)$ source bin/activate
    (pyshop)$ pip install pyshop
    (pyshop)$ cp pyshop.sample.ini pyshop.ini
    (pyshop)$ vim pyshop.ini  # change the pyshop.cookie_key setting
    (pyshop)$ pyshop_install pyshop.ini
    (pyshop)$ pserve pyshop.ini start --log-file=pyshop.log

You shoud edit the pyshop.ini file in order to configure the pyshop.cookie_key,
the host:port that host the service.  When the pyshop is running visit the web
application, http://localhost:8000/ by default, to check all is fine.

For production usage, you should create accounts with the "developer" group.
Visit http://localhost:6543/pyshop/user with the admin account to create
accounts. You also should use an https reverse proxy. Python packaging core use
basic authentication: it send user/password in clear.

Configuring your environment to use that new pyshop
---------------------------------------------------

Here is all configuration files for usual python tools you have to edit for
simplify the usage of pyshop.

~/.pip/pip.conf
~~~~~~~~~~~~~~~

Configuration used by pip.  This is a user file, you can set a developper or
the pip generic account.

::

    [global]
    # when mirroring a package,
    # pyshop retrieve informations from PyPI and
    # store them in its DB.
    # Be patient, it is not so long.
    default-timeout = 60
    timeout = 60
    [install]
    index-url = http://pip:changeme@localhost:6543/simple/

setup.cfg
~~~~~~~~~

A setup.cfg file is used by the "python setup.py develop" to install
dependancies. You should use a generic account with have installer privilleges
only, shared by every developper.

This file is a "per project file" at the root of the package.

::

    [easy_install]
    index-url = http://pip:changeme@localhost:6543/simple/

This should work now::

    python setup.py develop


~/.pypirc
~~~~~~~~~

Configuration used by setuptools to upload package.
Every developper should have it's own account to upload package.

::

    [distutils]
    index-servers =
        pyshop

    [pyshop]
    username: admin  # or create an account in pyshop admin interface
    password: changeme
    repository: http://localhost:6543/simple/


This should works now::

    python setup.py sdist upload -v -r pyshop /pypi/pypiserver

Feature Missing
---------------

Developper can't add other accounts to give them upload right to their project.
This can be done in the database or in the pyshop shell by an administrator.

::

    $ pyshop_shell pyshop.ini
    In [1]: pkg = Package.by_name(session, u'pyshop')
    In [2]: pkg.owners.append(User.by_login(session, u'admin'))
    In [3]: session.commit()


Alternatives
------------

 - pypiserver: https://pypi.python.org/pypi/pypiserver
 - localshop: http://pypi.python.org/pypi/localshop
 - djangopypi: http://pypi.python.org/pypi/djangopypi
 - chishop: http://pypi.python.org/pypi/chishop
