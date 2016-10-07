from __future__ import absolute_import, print_function, unicode_literals

import sys
import binascii
import base64

from zope.interface import implementer

from pyramid.interfaces import IAuthenticationPolicy
from pyramid.authentication import CallbackAuthenticationPolicy, \
        AuthTktAuthenticationPolicy, RemoteUserAuthenticationPolicy

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
        except AttributeError:  # not enough values to unpack
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

        if User.by_ldap_credentials(DBSession(), login, password,request.registry.settings):
            return login

        return None

    def unauthenticated_userid(self, request):
        return self.authenticated_userid(request)

    def remember(self, request, principal, **kw):
        return []

    def forget(self, request):
        return []

def basic_auth_policy_factory():
    return lambda callback: AuthBasicAuthenticationPolicy(callback=callback)


@implementer(IAuthenticationPolicy)
class DBRemoteUserAuthenticationPolicy(RemoteUserAuthenticationPolicy):
    def __init__(self, environ_key='REMOTE_USER', email_domain=None, email_key=None, callback=None, debug=False):
        if email_domain is None and email_key is None:
            raise RuntimeError("DBRemoteUserAuthenticationPolicy must have either email_domain or email_key specified")

        super(DBRemoteUserAuthenticationPolicy, self).__init__(environ_key, callback, debug)

        self.email_domain = email_domain
        self.email_key = email_key

    def _get_email(self, login, request):
        if self.email_key is not None:
            return request.environ.get(self.email_key)

        if self.email_domain is not None:
            return "%s@%s" % (login, self.email_domain)

    def authenticated_userid(self, request):
        login = super(DBRemoteUserAuthenticationPolicy, self).authenticated_userid(request)
        if User.by_remote_user_value(DBSession(), login, email=self._get_email(login, request)):
            return login
        return None


def remote_user_auth_policy_factory(login='REMOTE_USER', email_domain=None, email=None):
    return lambda callback: DBRemoteUserAuthenticationPolicy(environ_key=login, email_domain=email_domain,
            email_key=email, callback=callback)


def session_auth_policy_factory(secret):
    def get_session_policy(callback):
        try:
            return AuthTktAuthenticationPolicy(secret, callback=callback, hashalg='sha512')
        except TypeError:
            return AuthTktAuthenticationPolicy(secret, callback=callback)
    return get_session_policy


def auth_policy_factory(type, **kwargs):
    factory = {
            'session':     session_auth_policy_factory,
            'remote_user': remote_user_auth_policy_factory,
            'basic':       basic_auth_policy_factory,
        }.get(type)
    if factory is not None:
        return factory(**kwargs)
    return None


def auth_from_config(key, settings, prefix='pyshop.auth'):
    name = settings['.'.join([prefix, key])]
    type = settings['.'.join([prefix, 'methods', name, 'type'])]
    args = {}
    for key in settings.keys():
        if key.startswith('.'.join([prefix, 'methods', name])):
            arg_key = key.split('.')[-1]
            if arg_key != 'type':
                args[arg_key] = settings[key]

    return auth_policy_factory(type, **args)


@implementer(IAuthenticationPolicy)
class RouteSwitchAuthPolicy(CallbackAuthenticationPolicy):

    def __init__(self, web_auth, simple_auth, upload_auth=None, callback=None):
        if upload_auth is None:
            upload_auth = simple_auth

        self.impl = {
            'web': web_auth(callback),
            'simple': simple_auth(callback),
            'upload': upload_auth(callback)
        }
        self.callback = callback


    def get_impl(self, request):
        if request.matched_route and request.matched_route.name in (
                'list_simple', 'show_simple', 'show_release_file',
                'show_external_release_file'):
            return self.impl['simple']
        elif request.matched_route and request.matched_route.name in (
                'upload_releasefile'):
            return self.impl['upload']
        return self.impl['web']


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

