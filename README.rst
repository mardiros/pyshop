pyshop
======

A cheeseshop clone (PyPI server) written in pyramid


Getting Started
---------------

::

    $ virtualenv pyshop
    $ cd pyshop
    (pyshop)$ source bin/activate
    (pyshop)$ pip install git+https://github.com/mardiros/pyshop.git
    (pyshop)$ pyshop_install development.ini
    (pyshop)$ pserve development.ini  --log-file=pyshop.log


For production usage, you should create a user pyshop
with restriction right.

For editing permission, the web user interface is not ready.
You can use the pyshop shell.

::

    (pyshop)$ pyshop_shell


The upload on PyPI will be done when the project is more advanced.


Configuring your environment to use that new PyShop
---------------------------------------------------

Here is all configuration files by usual python tools you have to
edit to use PyShop.


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


Uploading a file to PyShop
--------------------------

python setup.py sdist upload  -v -r pyshop
