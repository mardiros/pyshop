pyshop
======

Get your private cheeseshop running.


Getting Started
---------------

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
the host:port that host the service, ...
When the pyshop is running visit the web application,
http://localhost:8000/ by default, to check all is fine.

For production usage, you should create accounts with the "developer" group.
Visit http://localhost:6543/pyshop/user with the admin account to create
accounts. You also should use an https reverse proxy. Python packaging
core use basic authentication: it send user/password in clear.


Configuring your environment to use that new pyshop
---------------------------------------------------

Here is all configuration files for usual python tools you have to
edit for simplify the usage of pyshop.


~/.pip/pip.conf
~~~~~~~~~~~~~~~

Configuration used by pip

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


~/.pypirc
~~~~~~~~~

Configuration used by setuptools to upload package

::

    [distutils]
    index-servers =
        pyshop

    [pyshop]
    username: admin # or create an account in pyshop admin interface
    password: changeme
    repository: http://localhost:6543/simple/


setup.cfg
~~~~~~~~~

::

    [easy_install]
    index-url = http://pip:changeme@localhost:6543/simple/


Uploading a file to your pyshop
-------------------------------

python setup.py sdist upload  -v -r pyshop
