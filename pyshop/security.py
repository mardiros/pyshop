import logging
from pyramid.security import Allow

from .models import DBSession, User, Group

log = logging.getLogger(__name__)


class GroupFinder(object):

    _users = {}

    def reset(self):
        self._users = {}

    def __call__(self, login, request):

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
    __name__ = None
    __parent__ = None

    _acl = None

    def __init__(self, request):
        log.info(u'[%s] %s %s' % (request.client_addr,
                                  request.method,
                                  request.current_route_url()
                                  ))
        self.__acl__ = self.get_acl(request)

    def get_acl(self, request):
        if RootFactory._acl is None:
            acl = []
            session = DBSession()
            groups = Group.all(session)
            for g in groups:
                acl.extend([(Allow, g.name, p.name) for p in g.permissions])
            RootFactory._acl = acl

        return RootFactory._acl
