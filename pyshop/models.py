#-*- coding: utf-8 -*-
"""
PyShop models

Describe the sql schema of PyShop using SQLAlchemy.
PyShop uses with SQLAlchemy with the sqlite backend.
"""
import re
import sys
import logging
# from distutils.util import get_platform

import cryptacular.bcrypt
from pkg_resources import parse_version

from sqlalchemy import (Table, Column, ForeignKey, Index,
                        Integer, Boolean, Unicode, UnicodeText,
                        DateTime, Enum)
from sqlalchemy.orm import relationship, synonym, backref
from sqlalchemy.sql.expression import func, or_, and_
from sqlalchemy.ext.declarative import declared_attr

from .helpers.sqla import (Database, SessionFactory, ModelError,
                           create_engine as create_engine_base,
                           dispose_engine as dispose_engine_base
                           )

log = logging.getLogger(__file__)
crypt = cryptacular.bcrypt.BCRYPTPasswordManager()

Base = Database.register('pyshop')
DBSession = lambda: SessionFactory.get('pyshop')()

re_email = re.compile(r'^[^@]+@[a-z0-9]+[-.a-z0-9]+\.[a-z]+$', re.I)


def _whlify(filename):

    if filename.endswith('.tar.gz'):
        pkg = filename[:-7]
    elif filename.endswith('.tar.bz2'):
        pkg = filename[:-8]
    elif filename.endswith('.zip'):
        pkg = filename[:-4]
    else:
        raise NotImplementedError('filename %s not supported' % filename)

    return u'{pkg}-py{pyvermax}{pyvermin}-none-{platform}'\
            '.whl'.format(pkg=pkg,
                          platform='any',  # XXX should works ! get_platform()
                          pyvermax=sys.version_info[0],
                          pyvermin=sys.version_info[1],
                          )


def create_engine(settings, prefix='sqlalchemy.', scoped=False):
    """
    Create the SQLAlchemy engine from the paste settings.

    :param settings: WSGI Paste parameters from the ini file.
    :type settings: dict

    :param prefix: SQLAlchemy engine configuration key prefix
    :type prefix: unicode

    :param scoped: True if the created engine configure a scoped session.
    :type scoped: bool

    :return: SQLAlchemy created engine
    :rtype: :class:`sqlalchemy.Engine`
    """
    return create_engine_base('pyshop', settings, prefix, scoped)


def dispose_engine():
    """Dispose the pyshop SQLAlchemy engine"""
    dispose_engine_base('pyshop')


class Permission(Base):
    """Describe a user permission"""
    name = Column(Unicode(255), nullable=False, unique=True)


group__permission = Table('group__permission', Base.metadata,
                          Column('group_id', Integer, ForeignKey('group.id')),
                          Column('permission_id',
                                 Integer, ForeignKey('permission.id'))
                          )


class Group(Base):
    """
    Describe user's groups.
    """
    name = Column(Unicode(255), nullable=False, unique=True)
    permissions = relationship(Permission, secondary=group__permission,
                               lazy='select')

    @classmethod
    def by_name(cls, session, name):
        """
        Get a package from a given name.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param name: name of the group
        :type name: `unicode

        :return: package instance
        :rtype: :class:`pyshop.models.Group`
        """
        return cls.first(session, where=(cls.name == name,))


user__group = Table('user__group', Base.metadata,
                    Column('group_id', Integer, ForeignKey('group.id')),
                    Column('user_id', Integer, ForeignKey('user.id'))
                    )


class User(Base):
    """
    Describe a user.

    This model handle `local` users granted to access pyshop and
    mirrored users from PyPI."""

    @declared_attr
    def __table_args__(cls):
        return (Index('idx_%s_login_local' % cls.__tablename__,
                      'login', 'local', unique=True),
                )

    login = Column(Unicode(255), nullable=False)
    _password = Column('password', Unicode(60), nullable=True)

    firstname = Column(Unicode(255), nullable=True)
    lastname = Column(Unicode(255), nullable=True)
    email = Column(Unicode(255), nullable=True)
    groups = relationship(Group, secondary=user__group, lazy='joined',
                          backref='users')

    local = Column(Boolean, nullable=False, default=True)

    @property
    def name(self):
        return u'%s %s' % (self.firstname, self.lastname)\
            if self.firstname and self.lastname else self.login

    def _get_password(self):
        return self._password

    def _set_password(self, password):
        self._password = unicode(crypt.encode(password))

    password = property(_get_password, _set_password)
    password = synonym('_password', descriptor=password)

    @classmethod
    def by_login(cls, session, login, local=True):
        """
        Get a user from a given login.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param login: the user login
        :type login: unicode

        :return: the associated user
        :rtype: :class:`pyshop.models.User`
        """
        user = cls.first(session,
                         where=((cls.login == login),
                                (cls.local == local),)
                         )
        # XXX it's appear that this is not case sensitive !
        return user if user and user.login == login else None

    @classmethod
    def by_credentials(cls, session, login, password):
        """
        Get a user from given credentials

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param login: username
        :type login: unicode

        :param password: user password
        :type password: unicode

        :return: associated user
        :rtype: :class:`pyshop.models.User`
        """
        user = cls.by_login(session, login, local=True)
        if not user:
            return None
        if crypt.check(user.password, password):
            return user

    @classmethod
    def get_locals(cls, session, **kwargs):
        """
        Get all local users.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :return: local users
        :rtype: generator of :class:`pyshop.models.User`
        """
        return cls.find(session, where=(cls.local == True,), order_by=cls.login,
                        **kwargs)

    def validate(self, session):
        """
        Validate that the current user can be saved.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :return: ``True``
        :rtype: bool

        :raise: :class:`pyshop.helpers.sqla.ModelError` if user is not valid
        """

        errors = []
        if not self.login:
            errors.append(u'login is required')
        else:
            other = User.by_login(session, self.login)
            if other and other.id != self.id:
                errors.append(u'duplicate login %s' % self.login)
        if not self.password:
            errors.append(u'password is required')
        if not self.email:
            errors.append(u'email is required')
        elif not re_email.match(self.email):
            errors.append(u'%s is not a valid email' % self.email)

        if len(errors):
            raise ModelError(errors)
        return True


class Classifier(Base):
    """
    Describe a Python Package Classifier.
    """

    @declared_attr
    def __table_args__(cls):
        return (Index('idx_%s_category_name' % cls.__tablename__,
                      'category', 'name', unique=True),
                )

    name = Column(Unicode(255), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey(u'classifier.id'))
    category = Column(Unicode(80), nullable=False)

    parent = relationship(u'Classifier', remote_side=u'Classifier.id',
                          backref=u'childs')

    @property
    def shortname(self):
        """
        Last part of the classifier.
        """
        return self.name.rsplit(u'::', 1)[-1].strip()

    @classmethod
    def by_name(cls, session, name):
        """
        Get a classifier from a given name.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param name: name of the classifier
        :type name: `unicode

        :return: classifier instance
        :rtype: :class:`pyshop.models.Classifier`
        """
        classifier = cls.first(session, where=(cls.name == name,))

        if not classifier:
            splitted_names = [n.strip() for n in name.split(u'::')]
            classifiers = [u' :: '.join(splitted_names[:i + 1])
                           for i in range(len(splitted_names))]
            parent_id = None
            category = splitted_names[0]

            for c in classifiers:
                classifier = cls.first(session, where=(cls.name == c,))
                if not classifier:
                    classifier = Classifier(name=c, parent_id=parent_id,
                                            category=category)
                    session.add(classifier)
                session.flush()
                parent_id = classifier.id

        return classifier


package__owner = Table('package__owner', Base.metadata,
                       Column('package_id', Integer, ForeignKey('package.id')),
                       Column('owner_id', Integer, ForeignKey('user.id'))
                       )

package__maintainer = Table('package__maintainer', Base.metadata,
                            Column('package_id',
                                   Integer, ForeignKey('package.id')),
                            Column('maintainer_id',
                                   Integer, ForeignKey('user.id'))
                            )


classifier__package = Table('classifier__package', Base.metadata,
                            Column('classifier_id',
                                   Integer, ForeignKey('classifier.id')),
                            Column('package_id',
                                   Integer, ForeignKey('package.id'))
                            )


class Package(Base):
    """
    Describe a Python Package.
    """

    update_at = Column(DateTime, default=func.now())
    name = Column(Unicode(200), unique=True)
    local = Column(Boolean, nullable=False, default=False)
    owners = relationship(User, secondary=package__owner,
                          backref='owned_packages')
    downloads = Column(Integer, default=0)
    maintainers = relationship(User, secondary=package__maintainer,
                               backref='maintained_packages')

    classifiers = relationship(Classifier, secondary=classifier__package,
                               lazy='dynamic', backref='packages')

    @property
    def versions(self):
        """
        Available versions.
        """
        return [r.version for r in self.sorted_releases]

    @property
    def sorted_releases(self):
        """
        Releases sorted by version.
        """
        return sorted(self.releases,
                      cmp=lambda a, b: cmp(parse_version(a.version),
                                           parse_version(b.version)),
                      reverse=True)

    @classmethod
    def by_name(cls, session, name):
        """
        Get a package from a given name.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param name: name of the package
        :type name: `unicode

        :return: package instance
        :rtype: :class:`pyshop.models.Package`
        """
        # XXX the field "name" should be created with a
        # case insensitive collation.
        pkg = cls.first(session, where=(cls.name.like(name),))
        if not pkg:
            name = name.replace(u'-', u'_').upper()
            pkg = cls.first(session,
                            where=(cls.name.like(name),))
            # XXX _ is a like operator
            if pkg.name.upper().replace(u'-', u'_') != name:
                pkg = None
        return pkg

    @classmethod
    def by_filter(cls, session, opts, **kwargs):
        """
        Get packages from given filters.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param opts: filtering options
        :type opts: `dict

        :return: package instances
        :rtype: generator of :class:`pyshop.models.Package`
        """
        where = []

        if opts.get('local_only'):
            where.append(cls.local == True)

        if opts.get('classifiers'):
            ids = [c.id for c in opts.get('classifiers')]
            cls_pkg = classifier__package
            qry = session.query(cls_pkg.c.package_id,
                                func.count('*'))
            qry = qry.filter(cls_pkg.c.classifier_id.in_(ids))
            qry = qry.group_by(cls_pkg.c.package_id)
            qry = qry.having(func.count('*') >= len(ids))
            where.append(cls.id.in_([r[0] for r in qry.all()]))

        return cls.find(session, where=where, **kwargs)

    @classmethod
    def by_owner(cls, session, owner_name):
        """
        Get packages from a given owner username.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param owner_name: owner username
        :type owner_name: unicode

        :return: package instances
        :rtype: generator of :class:`pyshop.models.Package`
        """
        return cls.find(session,
                        join=(cls.owners),
                        where=(User.login == owner_name,),
                        order_by=cls.name)

    @classmethod
    def by_maintainer(cls, session, maintainer_name):
        """
        Get package from a given maintainer name.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param maintainer_name: maintainer username
        :type maintainer_name: unicode

        :return: package instances
        :rtype: generator of :class:`pyshop.models.Package`
        """
        return cls.find(session,
                        join=(cls.maintainers),
                        where=(User.login == maintainer_name,),
                        order_by=cls.name)

    @classmethod
    def get_locals(cls, session):
        """
        Get all local packages.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :return: package instances
        :rtype: generator of :class:`pyshop.models.Package`
        """
        return cls.find(session,
                        where=(cls.local == True,))

    @classmethod
    def get_mirrored(cls, session):
        """
        Get all mirrored packages.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :return: package instances
        :rtype: generator of :class:`pyshop.models.Package`
        """
        return cls.find(session,
                        where=(cls.local == False,))


classifier__release = Table('classifier__release', Base.metadata,
                            Column('classifier_id',
                                   Integer, ForeignKey('classifier.id')),
                            Column('release_id',
                                   Integer, ForeignKey('release.id'))
                            )


class Release(Base):
    """
    Describe Python Package Release.
    """

    @declared_attr
    def __table_args__(cls):
        return (Index('idx_%s_package_id_version' % cls.__tablename__,
                      'package_id', 'version', unique=True),
                )

    version = Column(Unicode(16), nullable=False)
    summary = Column(Unicode(255))
    downloads = Column(Integer, default=0)

    package_id = Column(Integer, ForeignKey(Package.id),
                        nullable=False)
    author_id = Column(Integer, ForeignKey(User.id))
    maintainer_id = Column(Integer, ForeignKey(User.id))
    stable_version = Column(Unicode(16))
    home_page = Column(Unicode(255))
    license = Column(UnicodeText())
    description = Column(UnicodeText())
    keywords = Column(Unicode(255))
    platform = Column(Unicode(24))
    download_url = Column(Unicode(800))
    bugtrack_url = Column(Unicode(800))
    docs_url = Column(Unicode(800))
    classifiers = relationship(Classifier, secondary=classifier__release,
                               lazy='dynamic', cascade='all, delete')
    package = relationship(Package, lazy='join',
                           backref=backref('releases',
                                           cascade='all, delete-orphan'))
    author = relationship(User, primaryjoin=author_id == User.id)
    maintainer = relationship(User, primaryjoin=maintainer_id == User.id)

    @property
    def download_url_file(self):
        """
        Filename of the download_url if any.
        """
        url = self.download_url
        return url.rsplit('/', 1).pop() if url else None

    @property
    def can_download_url_whl(self):
        filename = self.download_url_file.split('#').pop(0)
        return (self.filename.endswith('.tar.gz') or
                self.filename.endswith('.tar.bz2') or
                self.filename.endswith('.zip'))

    @property
    def whlify_download_url_file(self):
        return _whlify(self.download_url_file.split('#').pop(0))

    @classmethod
    def by_version(cls, session, package_name, version):
        """
        Get release for a given version.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param package_name: package name
        :type package_name: unicode

        :param version: version
        :type version: unicode

        :return: release instance
        :rtype: :class:`pyshop.models.Release`
        """
        return cls.first(session,
                         join=(Package,),
                         where=((Package.name == package_name),
                                (cls.version == version)))

    @classmethod
    def by_classifiers(cls, session, classifiers):
        """
        Get releases for given classifiers.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param classifiers: classifiers
        :type classifiers: unicode

        :return: release instances
        :rtype: generator of :class:`pyshop.models.Release`
        """
        return cls.find(session,
                        join=(cls.classifiers,),
                        where=(Classifier.name.in_(classifiers),),
                        )

    @classmethod
    def search(cls, session, opts, operator):
        """
        Get releases for given filters.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param opts: filtering options
        :type opts: dict

        :param operator: filtering options joining operator (`and` or `or`)
        :type operator: basestring

        :return: release instances
        :rtype: generator of :class:`pyshop.models.Release`
        """
        available = {'name': Package.name,
                     'version': cls.version,
                     'author': User.login,
                     'author_email': User.email,
                     'maintainer': User.login,
                     'maintainer_email': User.email,
                     'home_page': cls.home_page,
                     'license': cls.license,
                     'summary': cls.summary,
                     'description': cls.description,
                     'keywords': cls.keywords,
                     'platform': cls.platform,
                     'download_url': cls.download_url
                     }
        oper = {'or': or_, 'and': and_}
        join_map = {'name': Package,
                    'author': cls.author,
                    'author_email': cls.author,
                    'maintainer': cls.maintainer,
                    'maintainer_email': cls.maintainer,
                    }
        where = []
        join = []
        for opt, val in opts.items():
            field = available[opt]
            if hasattr(val, '__iter__'):
                stmt = or_([field.like(u'%%%s%%' % v) for v in val])
            else:
                stmt = field.like(u'%%%s%%' % val)
            where.append(stmt)
            if opt in join_map:
                join.append(join_map[opt])
        return cls.find(session, join=join,
                        where=(oper[operator](*where),))


class ReleaseFile(Base):
    """
    Describe a release file.
    """

    release_id = Column(Integer, ForeignKey(Release.id),
                        nullable=False)
    filename = Column(Unicode(200), unique=True, nullable=False)
    md5_digest = Column(Unicode(50))
    size = Column(Integer)
    package_type = Column(Enum(u'sdist', u'bdist_egg', u'bdist_msi',
                               u'bdist_dmg', u'bdist_rpm', u'bdist_dumb',
                               u'bdist_wininst',
                               u'bdist_wheel'), nullable=False)

    python_version = Column(Unicode(25))
    url = Column(Unicode(1024))
    downloads = Column(Integer, default=0)
    has_sig = Column(Boolean, default=False)
    comment_text = Column(UnicodeText())

    release = relationship(Release, lazy='join',
                           backref=backref('files',
                                           cascade='all, delete-orphan'))

    @property
    def filename_whlified(self):
        assert self.package_type == 'sdist'
        return _whlify(self.filename)

    @classmethod
    def by_release(cls, session, package_name, version):
        """
        Get release files for a given package
        name and for a given version.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param package_name: package name
        :type package_name: unicode

        :param version: version
        :type version: unicode

        :return: release files
        :rtype: generator of :class:`pyshop.models.ReleaseFile`
        """
        return cls.find(session,
                        join=(Release, Package),
                        where=(Package.name == package_name,
                               Release.version == version,
                               ))

    @classmethod
    def by_filename(cls, session, release, filename):
        """
        Get a release file for a given realease and a given filename.

        :param session: SQLAlchemy session
        :type session: :class:`sqlalchemy.Session`

        :param release: release
        :type release: :class:`pyshop.models.Release`

        :param filename: filename of the release file
        :type filename: unicode

        :return: release file
        :rtype: :class:`pyshop.models.ReleaseFile`
        """
        return cls.first(session,
                         where=(ReleaseFile.release_id == release.id,
                                ReleaseFile.filename == filename,
                                ))
