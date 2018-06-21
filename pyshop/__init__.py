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
from .helpers.authentication import RouteSwitchAuthPolicy

__version__ = '1.3.0'


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

    use_remote_user = asbool(settings.get('pyshop.remote_user.use_for_auth', 'False'))
    remote_user_key = settings.get('pyshop.remote_user.login', 'REMOTE_USER')

    if use_remote_user:
        remote_user_email_domain = settings.get('pyshop.remote_user.email_domain')
        remote_user_email_key = settings.get('pyshop.remote_user.email')
        if remote_user_email_domain is None and remote_user_email_key is None:
            raise RuntimeError("Pyshop is configured for server authentication, but email isn't "\
                               "specified. Set either pyshop.remote_user.email_domain or "\
                               "pyshop.remote_user.email in the config file")
        if remote_user_email_key is not None:
            email_factory = lambda login, request: request.environ.get(remote_user_email_key)
        else:
            email_factory = lambda login, reqeust: "%s@%s" % (login, remote_user_email_domain)
    else:
        email_factory = None

    authn_policy = RouteSwitchAuthPolicy(secret=settings['pyshop.cookie_key'],
                                         callback=groupfinder,
                                         use_remote_user=use_remote_user,
                                         remote_user_key=remote_user_key,
                                         remote_user_email_factory=email_factory)

    authz_policy = ACLPolicy()
    route_prefix = settings.get('pyshop.route_prefix')

    config = Configurator(settings=settings,
                          root_factory=RootFactory,
                          route_prefix=route_prefix,
                          locale_negotiator=locale_negotiator,
                          authentication_policy=authn_policy,
                          authorization_policy=authz_policy)
    config.end()

    return config.make_wsgi_app()
