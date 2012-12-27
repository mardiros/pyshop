# -*- coding: utf-8 -*-
import re
import logging
import os.path
from datetime import datetime

from sqlalchemy.sql.expression import func

from pyramid import httpexceptions as exc
from pyramid.settings import asbool
from pyramid.security import authenticated_userid

from pyshop.models import User, Package, Classifier, Release, ReleaseFile
from pyshop.helpers import pypi

from .base import View


log = logging.getLogger(__name__)


class List(View):

    def render(self):
        return {'packages': Package.all(self.session, order_by=Package.name)}


class UploadReleaseFile(View):
    def render(self):
        settings = self.request.registry.settings
        username = authenticated_userid(self.request)
        if not username:
             raise exc.HTTPForbidden()

        remote_user = User.by_login(self.session, username)
        if not remote_user:
            raise exc.HTTPForbidden()

        params = self.request.params
        pkg = Package.by_name(self.session, params['name'])
        if pkg:
            auth = [user for user in pkg.owners + pkg.maintainers
                    if user == remote_user]
            if not auth:
                raise exc.HTTPForbidden()
        else:
            pkg = Package(name=params['name'], local=True)
            pkg.owners.append(remote_user)

        content = self.request.POST['content']
        input_file = content.file
        # rewrite the filename, do not use the posted one for security
        filename = u'%s-%s.%s' % (params['name'], params['version'],
                                  {u'sdist': u'tar.gz',
                                   u'bdist_egg': u'egg',
                                   u'bdist_msi': u'msi',
                                   u'bdist_dmg': u'zip', # XXX or gztar ?
                                   u'bdist_rpm': u'rpm',
                                   u'bdist_dumb': u'msi',
                                   u'bdist_wininst': u'exe',
                                   }[params['filetype']])
        dir_ = os.path.join(settings['pyshop.repository'],
                            filename[0].lower())

        if not os.path.exists(dir_):
            os.mkdir(dir_, 0750)

        filepath = os.path.join(dir_, filename)
        while os.path.exists(filepath):
            log.warn('File %s exists but new upload self.request, deleting'
                     % filepath)
            os.unlink(filepath)

        size = 0
        with open(filepath, 'wb') as output_file:
            input_file.seek(0)
            while True:
                data = input_file.read(2<<16)
                if not data:
                    break
                size += len(data)
                output_file.write(data)

        release = Release.by_version(self.session, pkg.name,
                                     params['version'])
        if not release:
            release = Release(package=pkg,
                              version=params['version'],
                              summary=params.get('summary'),
                              author=remote_user,
                              home_page=params.get('home_page'),
                              license=params.get('license'),
                              description=params.get('description'),
                              keywords=params.get('keywords'),
                              platform=params.get('platform'),
                              download_url=params.get('download_url'),
                              docs_url=params.get('docs_url'),
                              )

        classifiers = params.getall('classifiers')
        for name in classifiers:
            classifier = Classifier.by_name(self.session, name)
            while classifier:
                release.classifiers.append(classifier)
                if classifier not in pkg.classifiers:
                    pkg.classifiers.append(classifier)
                classifier = classifier.parent

        rfile = ReleaseFile.by_filename(self.session, release, filename)
        if not rfile:
            rfile = ReleaseFile(release=release,
                                filename=filename,
                                size=size,
                                md5_digest=params.get('md5_digest'),
                                package_type=params['filetype'],
                                python_version=params.get('pyversion'),
                                comment_text=params.get('comment'),
                                )

        self.session.add(rfile)
        self.session.add(release)
        pkg.update_at = func.now()
        self.session.add(pkg)
        return {'release_file': rfile}


class Show(View):

    def _create_release(self, package, data):

        release = Release(package=package,
                          summary=data.get('summary'),
                          version=data.get('version'),
                          stable_version=data.get('stable_version'),
                          home_page=data.get('home_page'),
                          license=data.get('license'),
                          description=data.get('description'),
                          keywords=data.get('keywords'),
                          platform=data.get('platform'),
                          download_url=data.get('download_url'),
                          bugtrack_url=data.get('bugtrack_url'),
                          docs_url=data.get('docs_url'),
                          )
        if data.get('author'):
            author = User.by_login(self.session, data['author'], local=False)
            if not author:
                author = User(login=data['author'],
                              local=False,
                              email=data.get('author_email'))
                self.session.add(author)
            release.author = author
        self.session.flush()
        if data.get('maintainer'):
            maintainer = User.by_login(self.session, data['maintainer'],
                                       local=False)
            if not maintainer:
                maintainer = User(login=data['maintainer'],
                                  local=False,
                                  email=data.get('maintainer_email'))
                self.session.add(maintainer)
            release.maintainer = maintainer
        self.session.flush()

        for name in data.get('classifiers', []):
            classifier = Classifier.by_name(self.session, name)

            while classifier:
                release.classifiers.append(classifier)
                if classifier not in package.classifiers:
                    package.classifiers.append(classifier)
                classifier = classifier.parent

        self.session.flush()
        return release

    def _create_release_file(self, release, data):
        return ReleaseFile(release=release,
                           filename=data['filename'],
                           md5_digest=data['md5_digest'],
                           url=data['url'],
                           size=data['size'],
                           package_type=data['packagetype'],
                           python_version=data['python_version'],
                           has_sig=data.get('has_sig', False),
                           comment_text=data.get('comment_text'),
                           )

    def render(self):


        api = pypi.proxy
        settings = self.request.registry.settings
        satanize = asbool(settings['pyshop.satanize'])

        package_name = self.request.matchdict['package_name']
        pkg = Package.by_name(self.session, package_name)
        refresh = True

        if pkg:
            if pkg.local:
                refresh = False
            else:
                if pkg.update_at:
                    td = datetime.now() - pkg.update_at
                    refresh = td.days > 0 or td.seconds > 10800

        if refresh:
            pypi_versions = api.package_releases(package_name, True)
            # XXX package_releases is case sensitive
            # but dependancies declaration not...
            if not pypi_versions:
                package_name = package_name.lower()
                search_result = api.search({'name': package_name}, True)
                search_result = [p for p in search_result
                                 if p['name'].lower() == package_name]
                if search_result:
                    package_name = search_result[0]['name']
                    pypi_versions = api.package_releases(package_name, True)
        else:
            pypi_versions = []

        if not pkg:
            if not pypi_versions:
                log.info('package %s has no versions' % package_name)
                return {'package': None,
                        'package_name': package_name}

            if satanize:
                re_satanize = re.compile(settings['pyshop.satanize.regex'])
                pypi_versions = [v for v in pypi_versions
                                 if re_satanize.match(v)]

            # mirror the package now
            log.info('mirror package %s now' % package_name)
            pkg = Package(name=package_name, local=False)
            roles = api.package_roles(package_name)
            for role, login in roles:
                user = User.by_login(self.session, login, local=False)
                if not user:
                    user = User(login=login, local=False)
                    self.session.add(user)
                if role == 'Owner':
                    pkg.owners.append(user)
                elif role == 'Maintainer':
                    pkg.maintainers.append(user)

        self.session.flush()

        refresh = True
        if not pkg.local and refresh:
            pkg_versions = pkg.versions
            for version in pypi_versions:
                if version not in pkg_versions:
                    release_data = api.release_data(package_name, version)
                    release = self._create_release(pkg, release_data)

                    release_files = api.release_urls(package_name, version)

                    for data in release_files:
                        rf = ReleaseFile.by_filename(self.session, release,
                                                     data['filename'])
                        if not rf:
                            rf = self._create_release_file(release, data)

        pkg.update_at = func.now()
        self.session.add(pkg)
        log.info('package %s mirrored' % package_name)
        return {'package': pkg}
