#-*- coding: utf-8 -*-
"""
Initialize a python shell with a given environment (a config file).
"""

import os
import sys

from sqlalchemy import engine_from_config

from pyramid.paster import get_appsettings, setup_logging
from pyramid.config import Configurator

from pyshop.helpers.sqla import create_engine, dispose_engine
from pyshop.models import DBSession
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
    settings = get_appsettings(config_uri)
    engine = create_engine('pyshop', settings, scoped=False)

    config = Configurator(settings=settings)
    config.end()

    from pyshop.models import (User, Group,
                               Classifier, Package, Release, ReleaseFile)

    session = DBSession()
    try:
        from IPython import embed
        from IPython.config.loader import Config
        cfg = Config()
        cfg.InteractiveShellEmbed.confirm_exit = False
        embed(config=cfg, banner1="Welcome to PyShop shell.")
    except ImportError:
        import code
        code.interact("pyshop shell", local=locals())


if __name__ == '__main__':
    main()
