import logging
from pyramid.security import Allow

from .models import DBSession, Group
from .security import groupfinder

log = logging.getLogger(__name__)

class RootFactory(object):
    __name__ = None
    __parent__ = None

    _acl = None

    def __init__(self, request):
        log.info("[%s] %s %s" % (request.client_addr,
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
