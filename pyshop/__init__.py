# -*- coding: utf-8 -*-
"""
PyShop Web Application.
"""
import sys
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy as ACLPolicy
from pyramid.settings import asbool

from .security import groupfinder, RootFactory

from .config import includeme  # used by pyramid
from .models import create_engine
from .helpers.i18n import locale_negotiator
from .helpers.authentication import RouteSwitchAuthPolicy, auth_from_config

__version__ = '1.2.3'


def main(global_config, **settings):
    """
    Get a PyShop WSGI application configured with settings.
    """
    if sys.version_info[0] < 3:
        reload(sys)
        sys.setdefaultencoding('utf-8')

    settings = dict(settings)
    # Scoping sessions for Pyramid ensure session are commit/rollback
    # after the template has been rendered
    create_engine(settings, scoped=True)

    cookie_key = settings.get('pyshop.cookie_key')
    if cookie_key is not None:
        updated_methods = set()
        for key in settings.keys():
            if key.startswith('pyshop.auth.methods'):
                method_name = key.split('.')[-1]
                method_type = settings.get('.'.join(['pyshop.auth.methods', method_name, 'type']))
                if method_name not in updated_methods and method_type == 'session':
                    settings['.'.join('pyshop.auth.methods', method_name, 'secret')] = cookie_key
                    updated_methods.add(method_name)

    web_policy = auth_from_config('web', settings)
    simple_policy = auth_from_config('simple', settings)
    upload_policy = auth_from_config('upload', settings)

    authn_policy = RouteSwitchAuthPolicy(web_policy, simple_policy, upload_policy, callback=groupfinder)

    authz_policy = ACLPolicy()
    route_prefix = settings.get('pyshop.route_prefix')

    config = Configurator(settings=settings,
                          root_factory=RootFactory,
                          route_prefix = route_prefix,
                          locale_negotiator=locale_negotiator,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    config.end()

    return config.make_wsgi_app()

