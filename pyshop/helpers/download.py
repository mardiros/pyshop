#-*- coding: utf-8 -*-
"""
Pyramid helper that mirror and serve file automatically from PyPI.

Package are mirrored safety by validating the PyPI certificate.

It is possible to use an HTTP Proxy. Pyshop use the requests library, so,
you just have to export your proxy in the environment variable `https_proxy`.
"""

import os
import os.path
import mimetypes
import logging
import tempfile
import tarfile
import shutil

import requests
from zope.interface import implements
from pyramid.interfaces import ITemplateRenderer
from pyramid.exceptions import NotFound
from wheel.egg2wheel import egg2wheel

log = logging.getLogger(__name__)
# registering mimetype for egg files
mimetypes.add_type('x-application/egg', '.egg')
mimetypes.add_type('x-application/whl', '.whl')


def build_whl(source, dest):
    tempdir = tempdir2 = None
    olddir = os.path.abspath(os.curdir)
    try:
        tempdir = tempfile.mkdtemp(prefix='pyshop')
        # FIXME: .zip is not supported yet
        arch = tarfile.open(source)
        arch.extractall(tempdir)  # XXX do not trust ! .. inside !!!
        os.chdir(os.path.join(tempdir, os.listdir(tempdir)[0]))
        os.system('python setup.py bdist_egg')
        distdir = os.path.join(tempdir, os.listdir(tempdir)[0], 'dist')
        egg = os.path.join(distdir, os.listdir(distdir)[0])
        # XXX Ugly
        # has we already have serve a filename, we must respect it
        # if the archive is intended for build for a specific platform
        # it will be renamed to "any" and it's wrong
        tempdir2 = tempfile.mkdtemp(prefix='pyshop')
        egg2wheel(egg, tempdir2)
        shutil.move(os.path.join(tempdir2, os.listdir(tempdir2)[0]), dest)
    finally:
        os.chdir(olddir)
        if tempdir:
            shutil.rmtree(tempdir)
        if tempdir2:
            shutil.rmtree(tempdir2)


class ReleaseFileRenderer(object):
    """Renderer that serve the python package"""

    implements(ITemplateRenderer)

    def __init__(self, repository_root):
        self.repository_root = repository_root

    def __call__(self, value, system):

        if 'request' in system:
            request = system['request']
            filename = value['filename']

            mime, encoding = mimetypes.guess_type(filename)

            request.response.content_type = mime
            if encoding:
                request.response.encoding = encoding

            localpath = os.path.join(self.repository_root, filename[0].lower(),
                                     filename)

            if not os.path.exists(localpath):
                sdistpath = os.path.join(self.repository_root,
                                         value['original'][0].lower(),
                                         value['original'])

                dir_ = os.path.join(self.repository_root,
                                    value['original'][0].lower())
                if not os.path.exists(dir_):
                    os.makedirs(dir_, 0o750)

                verify = value['url'].startswith('https:')

                log.info('Downloading {0}'.format(value['url']))
                resp = requests.get(value['url'], verify=verify)
                if resp.status_code == 404:
                    raise NotFound('Resource {0} not found'.format(value['original']))
                resp.raise_for_status()
                with open(sdistpath, 'wb') as file:
                    file.write(resp.content)

                if not value['whlify']:
                    return resp.content

                build_whl(sdistpath, localpath)

            data = ''
            with open(localpath, 'rb') as file:
                data = ''
                while True:
                    content = file.read(2 << 16)
                    if not content:
                        break
                    data += content
            return data


def renderer_factory(info):
    """
    Create the :class:`pyshop.helpers.download.ReleaseFileRenderer` factory.
    Packages are stored in the directory in the configuration key
    ``pyshop.repository`` of the paste ini file.
    """
    return ReleaseFileRenderer(info.settings['pyshop.repository'])
