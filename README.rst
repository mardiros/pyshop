======
pyshop
======


.. image:: https://travis-ci.org/mardiros/pyshop.png?branch=master
   :target: https://travis-ci.org/mardiros/pyshop

Getting Started
===============

Pyshop is a private repository for python packages.

The aim is to split private projects in distinct private packages and keep a
setup.py clean and working, by declaring all dependencies, exactly as public
packages on PyPI.

Pyshop also proxies and caches packages from PyPI safely using SSL and checking server
certificate.

Pyshop uses clear and simple ACLs to manage privileges:

- an installer group that can only download release files,
- a developer group that can download and upload release files and browse the
  website,
- an admin group that has developer privileges and accounts management.

Since pyshop is intended to host private packages, every user, including *pip*,
must be authenticated by login and password.

Installation
============

::

    $ virtualenv pyshop
    $ cd pyshop
    (pyshop)$ source bin/activate
    (pyshop)$ pip install "pyshop[waitress]"
    (pyshop)$ cp pyshop.sample.ini pyshop.ini
    (pyshop)$ vim pyshop.ini  # change the pyshop.cookie_key setting
    (pyshop)$ pyshop_setup pyshop.ini
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

The pythop.sample.ini file use waitress as the default WSGI server, but,
if you are familiar with another WSGI server that support paste format,
you could use it.

Using Docker
------------

Currently, there is an image of pyshop used for development purpose,
it support both MySQL and PostgreSQL. The PostgreSQL integration is
fully operation, you can run a new Pyshop install using docker-compose,
with the command:

::

    docker-compose up pgpyshop


It will create the database with the default pyshop users:

* privileged user:   login admin, password: changeme
* unprivileged user: login pip, password changeme

If you want to use a different orchestrator, you have to link the postgresql
container to Pyshop container with the name postgresql.localdomain

The MySQL support does not automate the database setup right now.


The official Docker image of Pyshop is available here on the Docker Hub:

https://registry.hub.docker.com/u/mardiros/pyshop/



Configuring your environment
============================

Here are all configuration files you will need to modify for usual python tools
to use your newly deployed private repository.

~/.pip/pip.conf
---------------

Configuration used by pip. This is a user file, you can set a developer or
the generic pip account.

::

    [global]
    # when mirroring a package, pyshop retrieves information from PyPI and
    # stores it in its database. Be patient, it is not so long.
    default-timeout = 120
    timeout = 120

    [install]
    index-url = http://pip:changeme@localhost:8000/simple/

    [search]
    index = http://pip:changeme@localhost:8000/pypi


.. note::

  If you are using a WSGI server that kills requests if it is too long, like
  uWSGI or gunicorn, set an appropriate timeout for this service too.

setup.cfg and pydistutils.cfg
-----------------------------

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
---------

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


Alternatives
============

- pypiserver: https://pypi.python.org/pypi/pypiserver
- localshop: http://pypi.python.org/pypi/localshop
- djangopypi: http://pypi.python.org/pypi/djangopypi
- chishop: http://pypi.python.org/pypi/chishop
