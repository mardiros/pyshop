#!/usr/bin/env python

from zope.interface import implements

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import CallbackAuthenticationPolicy, \
        AuthTktAuthenticationPolicy

from pyshop.models import DBSession, User


class AuthBasicAuthenticationPolicy(CallbackAuthenticationPolicy):
    implements(IAuthenticationPolicy)

    def __init__(self, callback=None):
        self.callback = callback

    def unauthenticated_userid(self, request):
        auth = request.environ.get('HTTP_AUTHORIZATION')
        if auth is None:
            return None
        scheme, data = auth.split(None, 1)
        assert scheme.lower() == 'basic'
        username, password = data.decode('base64').split(':', 1)
        if User.by_credentials(DBSession(), username, password):
            return username
        return None

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []


class RouteSwithchAuthPolicy(CallbackAuthenticationPolicy):
    implements(IAuthenticationPolicy)

    def __init__(self, secret='key',callback=None):
        self.impl = {'basic': AuthBasicAuthenticationPolicy(callback=callback),
                     'tk': AuthTktAuthenticationPolicy(secret,
                                                       callback=callback,
                                                       hashalg='sha512')
                     }
        self.callback=callback

    def get_impl(self,request):
        if request.matched_route.name in ('list_simple', 'show_simple'):
            return self.impl['basic']
        return self.impl['tk']

    def unauthenticated_userid(self, request):
        impl = self.get_impl(request)
        return impl.unauthenticated_userid(request)

    def remember(self, request, principal, **kw):
        impl = self.get_impl(request)
        return impl.remember(request, principal, **kw)

    def forget(self, request, *args, **kw):
        impl = self.get_impl(request)
        return impl.forget(request, *args, **kw)
