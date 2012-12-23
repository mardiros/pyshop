import os
import os.path
import mimetypes

import requests
from zope.interface import implements
from pyramid.interfaces import ITemplateRenderer


class ReleaseFileRenderer(object):
    implements(ITemplateRenderer)

    def __init__(self, repository_root):
        self.repository_root = repository_root

    def __call__(self, value, system):

        if 'request' in system:
            request = system['request']

            mime, encoding = mimetypes.guess_type(value['filename'])
            request.response_content_type = mime
            if encoding:
                request.response_encoding = encoding

            f = os.path.join(self.repository_root,
                             value['filename'][0].lower(),
                             value['filename'])

            if not os.path.exists(f):
                dir_ = os.path.join(self.repository_root,
                             value['filename'][0].lower())
                if not os.path.exists(dir_):
                    os.makedirs(dir_, 0750)

                resp = requests.get(value['url'])
                with open(f, 'wb') as rf:
                    rf.write(resp.content)
                return resp.content
            else:
                data = ''
                with open(f, 'rb') as rf:
                    data = ''
                    while True:
                        content = rf.read(2<<16)
                        if not content:
                            break
                        data += content
                return data


def renderer_factory(info):
    return ReleaseFileRenderer(info.settings['pyshop.repository'])
