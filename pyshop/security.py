"""
Pyramid security concern.

see http://docs.pylonsproject.org/projects/pyramid/en/latest/tutorials/wiki2/authorization.html
"""

import logging
from pyramid.security import Allow

from .models import DBSession, User, Group

log = logging.getLogger(__name__)


class GroupFinder(object):
    """
    Method creator of :meth:`groupfinder`
    """
    _users = {}

    def reset(self):
        """
        Reset the cache of users groups.
        """
        self._users = {}

    def __call__(self, login, request):
        """
        :param login: user login
        :type login: unicode

        :param request: pyramid request
        :type login: :class:`pyramid.request.Request`

        :return: list of groups name.
        :rtype: list of unicode
        """
        if login in self._users:
            return self._users[login]

        user = User.by_login(DBSession(), login)
        if user:
            rv =  [g.name for g in user.groups]
        else:
            rv = []
        self._users[login] = rv
        return rv

groupfinder = GroupFinder()


class RootFactory(object):
    """
    Pyramid root factory that contains the ACL.

    :param request: pyramid request
    :type login: :class:`pyramid.request.Request`
    """

    __name__ = None
    __parent__ = None

    _acl = None

    def __init__(self, request):
        ca = request.client_addr
        rm = request.method
        try:
            cru = request.current_route_url()
        except ValueError as e:
            cru = str(e)

        log.info(u'[%s] %s %s' % (ca, rm, cru))
        self.__acl__ = self.get_acl(request)

    def get_acl(self, request):
        """
        Get ACL.
        Initialize the __acl__ from the sql database once,
        then use the cached version.

        :param request: pyramid request
        :type login: :class:`pyramid.request.Request`

        :return: ACLs in pyramid format. (Allow, group name, permission name)
        :rtype: list of tupple
        """
        if RootFactory._acl is None:
            acl = []
            session = DBSession()
            groups = Group.all(session)
            for g in groups:
                acl.extend([(Allow, g.name, p.name) for p in g.permissions])
            RootFactory._acl = acl

        return RootFactory._acl
