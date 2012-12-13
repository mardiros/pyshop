#-*- coding: utf-8 -*-
"""
Initialize a python shell with a given environment (a config file).
"""

import os
import sys

from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings, setup_logging
from pyramid.config import Configurator

from pyshop.models import DBSession, initialize_sql
from pyshop.helpers import pypi



def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri>\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 2:
        usage(argv)
    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, 'main')
    engine = engine_from_config(settings, 'sqlalchemy.')
    initialize_sql(engine)
    pypi.set_proxy(settings['pypi.url'])

    config = Configurator(settings=settings)
    config.end()

    # XXX Configure pyramid_celery, something looks wrong, the bad way ???
    # from pyramid_celery.commands.celeryctl import CeleryCtl
    # CeleryCtl().setup_app_from_commandline(argv)

    # add models and session to locals
    from pyshop.models import (User, Group,
                               Package, Release, ReleaseFile)

    session = DBSession()
    try:
        from IPython import embed
        from IPython.config.loader import Config
        cfg = Config()
        cfg.InteractiveShellEmbed.confirm_exit = False
        embed(config=cfg, banner1="pyshop shell.")
    except ImportError:
        import code
        code.interact("pyshop shell", local=locals())


if __name__ == '__main__':
    main()
