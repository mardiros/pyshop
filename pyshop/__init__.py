# -*- coding: utf-8 -*-
"""
PyShop Web Application.
"""

from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy as ACLPolicy

from .security import groupfinder, RootFactory

from .config import includeme  # used by pyramid
from .models import create_engine
from .helpers.i18n import locale_negotiator
from .helpers.authentication import RouteSwithchAuthPolicy

__version__ = '0.9.2'


def main(global_config, **settings):
    """
    Get a PyShop WSGI application configured with settings.
    """

    settings = dict(settings)

    # Scoping sessions for Pyramid ensure session are commit/rollback
    # after the template has been rendered
    create_engine(settings, scoped=True)

    authn_policy = RouteSwithchAuthPolicy(secret=settings['pyshop.cookie_key'],
                                          callback=groupfinder)
    authz_policy = ACLPolicy()

    config = Configurator(settings=settings,
                          root_factory=RootFactory,
                          locale_negotiator=locale_negotiator,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    config.end()

    return config.make_wsgi_app()
