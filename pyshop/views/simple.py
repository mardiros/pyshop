# -*- coding: utf-8 -*-
import logging
import os.path
from datetime import datetime

from sqlalchemy.sql.expression import func

from pyramid import httpexceptions as exc
from pyramid.url import route_url
from pyramid.security import authenticated_userid

from pyshop.models import User, Package, Classifier, Release, ReleaseFile
from pyshop.helpers import pypi
from pyshop.helpers.i18n import trans as _

from .base import View


log = logging.getLogger(__name__)


class List(View):

    def render(self, request, session):

        if request.method == 'POST':
            username = authenticated_userid(request)
            if not username:
                 raise exc.HTTPForbidden()

            remote_user = User.by_login(session, username)
            if not remote_user:
                raise exc.HTTPForbidden()

            params = request.params
            pkg = Package.by_name(session, params['name'])
            if pkg:
                auth = [user for user in pkg.owners + pkg.maintainers
                        if user == remote_user]
                if not auth:
                    raise exc.HTTPForbidden()
            else:
                pkg = Package(name=params['name'], local=True)
                pkg.owners.append(remote_user)

            input_file = request.POST['content'].file
            filename = request.POST['content'].filename.split(os.path.sep)[-1]
            filename = filename.split('.', 1)
            filename[0] = u'%s-%s' % (params['name'], params['version'])
            filename = u'.'.join(filename)
            dir_ = os.path.join(request.registry.settings['repository.root'],
                                filename[0].lower())
            if not os.path.exists(dir_):
                os.mkdir(dir_, 0750)

            filepath = os.path.join(dir_, filename)
            while os.path.exists(filepath):
                log.warn("File %s exists but new upload request, deleting" %
                         filepath)
                os.unlink(filepath)

            with open(filepath, 'wb') as output_file:
                input_file.seek(0)
                while True:
                    data = input_file.read(2<<16)
                    if not data:
                        break
                    output_file.write(data)
                    output_file.close()

            release = Release.by_version(session, pkg.name,
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
                classifier = Classifier.by_name(session, name)
                if not classifier:
                    classifier = Classifier(name=name)
                    session.add(classifier)

            rfile = ReleaseFile(release=release,
                                filename=filename,
                                md5_digest=params.get('md5_digest'),
                                package_type=params.get('filetype'),
                                python_version=params.get('pyversion'),
                                comment_text=params.get('comment'),
                                )

            session.add(rfile)
            session.add(release)
            pkg.update_at = func.now()
            session.add(pkg)
            return {"release_file": rfile}

        return {'packages': Package.all(session, order_by=Package.name)}


class Show(View):

    def _create_release(self, session, package, data):
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
            author = User.by_login(session, data['author'], local=False)
            if not author:
                author = User(login=data['author'],
                              local=False,
                              email=data.get('author_email'))
                session.add(author)
            release.author = author
        session.flush()
        if data.get('maintainer'):
            maintainer = User.by_login(session, data['maintainer'], local=False)
            if not maintainer:
                maintainer = User(login=data['maintainer'],
                                  local=False,
                                  email=data.get('maintainer_email'))
                session.add(maintainer)
            release.maintainer = maintainer
        session.flush()

        for name in data.get('classifiers', []):
            classifier = Classifier.by_name(session, name)
            if not classifier:
                classifier = Classifier(name=name)
                session.add(classifier)

            release.classifiers.append(classifier)

        session.flush()
        return release

    def _create_release_file(self, session, release, data):
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

    def render(self, request, session):

        api = pypi.proxy
        package_name = request.matchdict['package_name']
        pkg = Package.by_name(session, package_name)
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
            # mirror the package now
            log.info('mirror package %s now' % package_name)
            pkg = Package(name=package_name, local=False)
            roles = api.package_roles(package_name)
            for role, login in roles:
                user = User.by_login(session, login, local=False)
                if not user:
                    user = User(login=login, local=False)
                    session.add(user)
                if role == 'Owner':
                    pkg.owners.append(user)
                elif role == 'Maintainer':
                    pkg.maintainers.append(user)

        session.flush()

        refresh = True
        if not pkg.local and refresh:
            pkg_versions = pkg.versions
            for version in pypi_versions:
                if version not in pkg_versions:
                    release_data = api.release_data(package_name, version)
                    release = self._create_release(session, pkg, release_data)

                    release_files = api.release_urls(package_name, version)

                    for data in release_files:
                        rf = ReleaseFile.by_filename(session, release,
                                                     data['filename'])
                        if not rf:
                            rf = self._create_release_file(session, release,
                                                           data)

        pkg.update_at = func.now()
        session.add(pkg)
        log.info('package %s mirrored' % package_name)
        return {'package': pkg}
