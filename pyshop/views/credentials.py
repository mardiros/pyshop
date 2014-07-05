# -*- coding: utf-8 -*-
"""
PyShop Credentials Views.
"""
from __future__ import absolute_import, print_function, unicode_literals
import logging
import base64

from pyramid.httpexceptions import HTTPFound
from pyramid.url import resource_url, route_url
from pyramid.security import remember, forget
from pyramid.response import Response

from pyshop.helpers.i18n import trans as _
from pyshop.models import DBSession, User
from pyshop.compat import unicode

from .base import View

log = logging.getLogger(__name__)


class Login(View):

    def render(self):

        login_url = resource_url(self.request.context, self.request, 'login')
        referrer = self.request.url
        # never use the login form itself as came_from
        if referrer == login_url:
            referrer = '/'
        came_from = self.request.params.get('came_from', referrer)
        login = self.request.params.get('user.login', '')
        if 'form.submitted' in self.request.params:
            password = self.request.params.get('user.password', u'')
            if password:
                if User.by_ldap_credentials(self.session, login, password,
                                            self.request.registry.settings) is not None:
                    log.info('login %r succeed' % login)
                    headers = remember(self.request, login)
                    return HTTPFound(location=came_from,
                                     headers=headers)
 
                if User.by_credentials(self.session, login, password) is not None:
                    log.info('login %r succeed' % login)
                    headers = remember(self.request, login)
                    return HTTPFound(location=came_from,
                                     headers=headers)

        return {'came_from': came_from,
                'user': User(login=login),
                }


class Logout(View):

    def render(self):

        return HTTPFound(location=route_url('index', self.request),
                         headers=forget(self.request))


def authbasic(request):
    """
    Authentification basic, Upload pyshop repository access
    """
    if len(request.environ.get('HTTP_AUTHORIZATION','')) > 0:
        auth = request.environ.get('HTTP_AUTHORIZATION')
        scheme, data = auth.split(None, 1)
        assert scheme.lower() == 'basic'
        data = base64.b64decode(data)
        if not isinstance(data, unicode):
            data = data.decode('utf-8')
        username, password = data.split(':', 1)
        if User.by_ldap_credentials(DBSession(), username, password, request.registry.settings):
            return HTTPFound(location=request.url)
        if User.by_credentials(DBSession(), username, password):
            return HTTPFound(location=request.url)
    return Response(status=401,
                    headerlist=[(b'WWW-Authenticate',
                                 b'Basic realm="pyshop repository access"'
                                 )],
                    )
