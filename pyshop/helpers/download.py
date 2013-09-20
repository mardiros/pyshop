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
import zipfile
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
    tempdir = None
    olddir = os.path.abspath(os.curdir)
    try:
        tempdir = tempfile.mkdtemp(prefix='pyshop')
        # FIXME: .zip is not supported yet
        if source.endswith('.zip'):
            with zipfile.ZipFile(source, 'r') as arch:
                if [file for file in arch.namelist() if '..' in file]:
                    raise RuntimeError('Archive is not safe')
                arch.extractall(tempdir)
        else:
            arch = tarfile.open(source)
            try:
                if [file for file in arch.getnames() if '..' in file]:
                    raise RuntimeError('Archive is not safe')
                arch.extractall(tempdir)
            finally:
                arch.close()

        os.chdir(os.path.join(tempdir, os.listdir(tempdir)[0]))
        os.system('python setup.py bdist_wheel')
        distdir = os.path.join(tempdir, os.listdir(tempdir)[0], 'dist')
        wheel = os.path.join(distdir, os.listdir(distdir)[0])
        # XXX
        # As we already have serve a filename, we must respect it
        # if the archive is intended for build for a specific platform,
        # like Linux-x86_64 it will be renamed to "any" but only works
        # for  Linux-x86_64.
        shutil.move(wheel, dest)
    finally:
        os.chdir(olddir)
        if tempdir:
            shutil.rmtree(tempdir)


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
