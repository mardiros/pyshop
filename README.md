pyshop
======

A cheeseshop clone (PyPI server) written in pyramid


Getting Started
---------------

.. code-block: bash

    $ virtualenv pyshop
    $ cd pyshop
    (pyshop)$ source bin/activate
    (pyshop)$ pip install git+https://github.com/mardiros/pyshop.git
    (pyshop)$ initialize_pyshop_db development.ini
    (pyshop)$ pserve development.ini


For production usage, you should create a user pyshop
with restriction right.

For editing permission, the web user interface is not ready.
You can use the pyshop shell.

    (pyshop)$ pyshop_shell


The upload on PyPI will be done when the project is more advanced.


Configuring your environment to use that new PyShop
---------------------------------------------------

Here is a all configuration files by usual python tools.


~/.pip/pip.conf
~~~~~~~~~~~~~~~

Configuration used by pip

.. code-block: ini

    [install]
    index-url = http://admin:changeme@localhost:6543/simple/


~/.pypirc
~~~~~~~~~

Configuration used by setuptools to upload package

.. code-block: ini

    [distutils]
    index-servers =
        pyshop

    [pyshop]
    username: admin
    password: changeme
    repository: http://localhost:6543/simple/


setup.cfg
~~~~~~~~~

.. code-block: ini

    [easy_install]
    index-url = http://admin:changeme@localhost:6543/simple/


Uploading a file to PyShop
--------------------------

python setup.py sdist upload  -v -r pyshop
