# -*- coding: utf-8 -*-
"""
PyShop Package Management Views.
"""
import math
import logging

from sqlalchemy.sql.expression import func
from pyramid.httpexceptions import HTTPNotFound

from pyshop.models import Package, Release, Classifier

from .base import View


log = logging.getLogger(__name__)


class List(View):

    def render(self):
        req = self.request
        page_no = 1
        page_size = 20
        if 'page_no' in req.matchdict:
            page_no = int(req.matchdict['page_no'])

        opts = {}
        if 'form.submitted' in req.params:
            opts['local_only'] = req.params.get('local_only', '0') == '1'
        else:
            opts['local_only'] = True
        if 'form.submitted' in req.params or req.params.get('classifier.added'):
            classifiers = [Classifier.by_id(self.session, id)
                           for id in set(req.params.getall('classifiers'))]

            if req.params.get('classifier.added'):
                classifiers.append(Classifier.by_name(self.session,
                                   req.params['classifier.added']))
            opts['classifiers'] = classifiers
        else:
            opts['classifiers'] = [] # TODO: set defaults in settings

        package_count = Package.by_filter(self.session, opts, count='*')

        return {u'has_page': package_count > page_size,
                u'paging': {u'route': u'list_package_page',
                            u'qs': self.request.query_string,
                            u'kwargs': {},
                            u'max': int(math.ceil(
                                        float(package_count) / page_size)),
                            u'no': page_no},
                 u'package_count': package_count,
                 u'packages': Package.by_filter(self.session, opts,
                     limit=page_size, offset=page_size * (page_no - 1),
                     order_by=func.lower(Package.name)
                     ),
                 u'filter': opts,
                 u'classifiers': Classifier.all(self.session,
                             order_by=Classifier.name)
                }


class Show(View):

    def render(self):

        package = Package.by_name(self.session,
                                  self.request.matchdict['package_name'])
        if not package:
            raise HTTPNotFound()

        if 'form.refresh_package' in self.request.params:
            package.update_at = None
            self.session.add(package)

        if 'release_version' in self.request.matchdict:
            release = Release.by_version(self.session, package.name,
                self.request.matchdict['release_version'])
        else:
            release = package.sorted_releases[0]

        return {u'package': package,
                u'release': release,
                }


class Refresh(View):

    def render(self):

        package = Package.by_name(self.session,
                                  self.request.matchdict['package_name'])
