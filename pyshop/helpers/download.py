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

import requests
from zope.interface import implements
from pyramid.interfaces import ITemplateRenderer
from pyramid.exceptions import NotFound

log = logging.getLogger(__name__)
# registering mimetype for egg files
mimetypes.add_type('x-application/egg', '.egg')


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
                dir_ = os.path.join(self.repository_root,
                                    filename[0].lower())
                if not os.path.exists(dir_):
                    os.makedirs(dir_, 0o750)

                verify = value['url'].startswith('https:')

                log.info('Downloading {0}'.format(value['url']))
                resp = requests.get(value['url'], verify=verify)
                if resp.status_code == 404:
                    raise NotFound('Resource {0} not found'.format(filename))
                resp.raise_for_status()
                with open(localpath, 'wb') as file:
                    file.write(resp.content)
                return resp.content
            else:
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
