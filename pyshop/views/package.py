# -*- coding: utf-8 -*-
import math
import logging

from pyramid.httpexceptions import HTTPNotFound

from pyshop.helpers.i18n import trans as _
from pyshop.models import User, Package, Classifier, Release, ReleaseFile

from .base import View


log = logging.getLogger(__name__)


class List(View):

    def render(self):
        page_no = 1
        page_size = 20
        if 'page_no' in self.request.matchdict:
            page_no = int(self.request.matchdict['page_no'])

        opts = {}

        package_count = Package.by_filter(self.session, opts, count=True)

        return {u'has_page': package_count > page_size,
                u'paging': {u'route': u'list_package_page',
                            u'qs': self.request.query_string,
                            u'kwargs': {},
                            u'max': int(math.ceil(
                                        float(package_count) / page_size)),
                            u'no': page_no},
                 u'package_count': package_count,
                 u'packages': Package.by_filter(self.session, opts),
                }


class Show(View):

    def render(self):

        package = Package.by_name(self.session,
                                  self.request.matchdict['package_name'])
        if not package:
            raise HTTPNotFound()
        return { u'package': package}
