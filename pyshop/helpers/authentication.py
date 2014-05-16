from __future__ import absolute_import, print_function, unicode_literals

import sys
import binascii
import base64

from zope.interface import implementer

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import CallbackAuthenticationPolicy, \
        AuthTktAuthenticationPolicy

from pyshop.models import DBSession, User
from pyshop.compat import unicode


@implementer(IAuthenticationPolicy)
class AuthBasicAuthenticationPolicy(CallbackAuthenticationPolicy):

    def __init__(self, callback=None):
        self.callback = callback

    def authenticated_userid(self, request):

        auth = request.environ.get('HTTP_AUTHORIZATION')
        try:
            authmeth, auth = auth.split(' ', 1)
        except AttributeError as ValueError:  # not enough values to unpack
            return None

        if authmeth.lower() != 'basic':
            return None

        try:
            # Python 3's string is already unicode
            auth = base64.b64decode(auth.strip())
        except binascii.Error:  # can't decode
            return None

        if not isinstance(auth, unicode):
            auth = auth.decode('utf-8')

        try:
            login, password = auth.split(':', 1)
        except ValueError:  # not enough values to unpack
            return None

        if User.by_credentials(DBSession(), login, password):
            return login

        return None

    def unauthenticated_userid(self, request):
        return self.authenticated_userid(request)

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []


@implementer(IAuthenticationPolicy)
class RouteSwitchAuthPolicy(CallbackAuthenticationPolicy):

    def __init__(self, secret='key',callback=None):
        try:
            authtk = AuthTktAuthenticationPolicy(secret,
                                                 callback=callback,
                                                  hashalg='sha512')
        except TypeError:
            # pyramid < 1.4
            authtk = AuthTktAuthenticationPolicy(secret, callback=callback)

        self.impl = {'basic': AuthBasicAuthenticationPolicy(callback=callback),
                     'tk': authtk
                     }
        self.callback = callback

    def get_impl(self, request):
        if request.matched_route and request.matched_route.name in (
        'list_simple','show_simple',
        'show_release_file','show_external_release_file',
        'upload_releasefile'):
            return self.impl['basic']
        return self.impl['tk']

    def authenticated_userid(self, request):
        impl = self.get_impl(request)
        return impl.authenticated_userid(request)

    def unauthenticated_userid(self, request):
        impl = self.get_impl(request)
        return impl.unauthenticated_userid(request)

    def remember(self, request, principal, **kw):
        impl = self.get_impl(request)
        return impl.remember(request, principal, **kw)

    def forget(self, request, *args, **kw):
        impl = self.get_impl(request)
        return impl.forget(request, *args, **kw)
