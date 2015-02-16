# -*- coding: utf-8 -*-
"""
PyShop Web Application.
"""
import sys
from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy as ACLPolicy

from .security import groupfinder, RootFactory

from .config import includeme  # used by pyramid
from .models import create_engine
from .helpers.i18n import locale_negotiator
from .helpers.authentication import RouteSwitchAuthPolicy

__version__ = '1.2.2'


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

    authn_policy = RouteSwitchAuthPolicy(secret=settings['pyshop.cookie_key'],
                                         callback=groupfinder)
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
