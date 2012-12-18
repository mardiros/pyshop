# -*- coding: utf-8 -*-
import math
import logging

from pyramid.httpexceptions import HTTPNotFound
from pyshop.models import User, Package, Classifier, Release, ReleaseFile

from .base import View

from pyshop.helpers.i18n import trans as _

log = logging.getLogger(__name__)


class List(View):

    def render(self, request, session):
        page_no = 1
        page_size = 20
        if 'page_no' in request.matchdict:
            page_no = int(request.matchdict['page_no'])

        opts = {}

        package_count = Package.by_filter(session, opts, count=True)

        return {u'has_page': package_count > page_size,
                u'paging': {u'route': u'list_package_page',
                            u'qs': request.query_string,
                            u'kwargs': {},
                            u'max': int(math.ceil(
                                        float(package_count) / page_size)),
                            u'no': page_no},
                 u'package_count': package_count,
                 u'packages': Package.by_filter(session, opts),
                }


class Show(View):

    def render(self, request, session):

        package = Package.by_name(session, request.matchdict['package_name'])
        if not package:
            raise HTTPNotFound()
        return { u'package': package}
