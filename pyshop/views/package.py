# -*- coding: utf-8 -*-
"""
PyShop Package Management Views.
"""
import math
import logging
import os

from sqlalchemy.sql.expression import func
from pyramid.httpexceptions import HTTPNotFound, HTTPForbidden

from pyshop.models import Package, Release, Classifier, User

from .base import View, RedirectView


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

        opts['names'] = []
        opts['classifiers'] = [] # TODO: set defaults in settings

        if 'form.submitted' in req.params or req.params.get('classifier.added'):
            classifiers = [Classifier.by_id(self.session, id)
                           for id in set(req.params.getall('classifiers'))]
            names = req.params.getall('names')

            if req.params.get('classifier.added'):
                classifier = Classifier.by_name(self.session,
                                                req.params['classifier.added'])
                if classifier:
                    log.info('!'*80)
                    log.info(classifier.__dict__)
                    classifiers.append(classifier)
                else:
                    names.append(req.params['classifier.added'])
            opts['classifiers'] = classifiers
            opts['names'] = names

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

        owners = dict((usr.login, usr) for usr in package.owners)
        can_edit_role = self.login in owners.keys() and package.local

        if 'form.add_role' in self.request.params:

            if not can_edit_role:
                raise HTTPForbidden()

            user = User.by_login(self.session, self.request.params['login'])
            if user and user.has_permission('upload_releasefile'):
                if self.request.params['role'] == 'owner':
                    if user.login not in owners:
                        package.owners.append(user)
                else:
                    maintainers = [usr.login for usr in package.owners]
                    if user.login not in maintainers:
                        package.maintainers.append(user)
                self.session.add(package)

        if 'form.remove_maintainer' in self.request.params:
            if not can_edit_role:
                raise HTTPForbidden()

            user = User.by_login(self.session, self.request.params['login'])
            if user:
                maintainers = dict((usr.login, usr)
                                   for usr in package.maintainers)
                if user.login in maintainers:
                    package.maintainers.remove(maintainers[user.login])
                    self.session.add(package)

        if 'form.remove_owner' in self.request.params:
            if not can_edit_role:
                raise HTTPForbidden()

            user = User.by_login(self.session, self.request.params['login'])
            if user:
                if user.login in owners:
                    package.owners.remove(owners[user.login])
                    self.session.add(package)

        if 'release_version' in self.request.matchdict:
            release = Release.by_version(self.session, package.name,
                self.request.matchdict['release_version'])
        else:
            release = package.sorted_releases[0]

        return {u'package': package,
                u'release': release,
                u'can_edit_role': can_edit_role,
                }


class Refresh(View):

    def render(self):

        package = Package.by_name(self.session,
                                  self.request.matchdict['package_name'])


class Purge(RedirectView):
    model = Package
    matchdict_key = 'package_id'
    redirect_route = 'list_package'

    def delete(self, model):

        # Check for and delete any packages on disk
        repository = self.request.registry.settings['pyshop.repository']
        for release in model.releases:
            for f in release.files:
                filepath = os.path.join(repository, f.filename[0], f.filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)

        self.session.delete(model)

    def render(self):

        model = self.model.by_id(self.session,
            int(self.request.matchdict[self.matchdict_key]))

        if 'form.submitted' in self.request.params:
            self.delete(model)
            return self.redirect()

        return {self.model.__tablename__: model}
