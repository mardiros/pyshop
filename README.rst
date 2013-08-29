pyshop
======

Getting Started
---------------

Pyshop is a private repository for python packages.

The aim is to split private projects in distinct private packages and keep a
setup.py clean and working, by declaring all dependencies, exactly as public
packages on PyPI.

Pyshop also mirrors packages from PyPI safely (using SSL and checking
server certificate).

Pyshop uses clear and simple ACLs to manage privileges:

-   an installer group that can only download release files,
-   a developer group that can download and upload release files and browse the
    website,
-   an admin group that has developer privileges and accounts management.

Since pyshop is intended to host private packages, every user, including *pip*,
must be authenticated by login and password.

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

You should edit the pyshop.ini file in order to configure the
``pyshop.cookie_key`` and the host:port that hosts the service. When the server
is running visit the website, http://localhost:8000/ by default, to check
everything is fine.

For production usage, you should create accounts with the *developer* group.
Visit http://localhost:8000/pyshop/user with the admin account to create
accounts.

You also should also use an https reverse proxy. Python packaging core uses
HTTP basic authentication: it sends user/password in clear.

Configuring your environment
----------------------------

Here are all configuration files you will need to modify for usual python tools
to use your newly deployed private mirror.

~/.pip/pip.conf
~~~~~~~~~~~~~~~

Configuration used by pip.  This is a user file, you can set a developer or
the generic pip account.

::

    [global]
    # when mirroring a package, pyshop retrieves information from PyPI and
    # stores it in its database. Be patient, it is not so long.
    default-timeout = 120
    timeout = 120

    [install]
    index-url = http://pip:changeme@localhost:8000/simple/


Note:
If you are using a WSGI server that kills requests if it is too long, like
uWSGI or gunicorn, set an appropriate timeout for this service too.

setup.cfg and pydistutils.cfg
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

setup.cfg and pydistutils.cfg are used when running *python setup.py develop*
to install your package or when using *easy_install*. You should use a generic
account with installer privileges only, shared by all developers.

This setting can be set per project or in user ``$HOME`` (see
`setuptools documentation`_ for details)

.. _`setuptools documentation`:  https://pythonhosted.org/setuptools/easy_install.html#configuration-files

::

    [easy_install]
    index-url = http://pip:changeme@localhost:8000/simple/

This should work now::

    python setup.py develop

~/.pypirc
~~~~~~~~~

Configuration used by setuptools to upload files.
All developers should have this configuration in their ``$HOME`` to upload
packages.

::

    [distutils]
    index-servers =
        pyshop

    [pyshop]
    username: admin  # or create an account in pyshop admin interface
    password: changeme
    repository: http://localhost:8000/simple/

This should work now::

    python setup.py sdist upload -v -r pyshop

Missing Features
----------------

Developer cannot add other accounts to give them upload right to their project.
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
