import os.path
import sys
from importlib import import_module
from pyramid.config import Configurator
from pyramid.paster import get_appsettings, setup_logging

from pyshop.helpers.sqla import create_engine, dispose_engine
from pyshop.models import DBSession


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> <migration_version>\n'
          '(example: "%s development.ini 0.7.5")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) != 3:
        usage(argv)
    version = argv[2]
    version = version.replace('.', '_')
    try:
        migration = import_module('pyshop.bin.migration.migr_%s' % version)
    except ImportError:
        print('No migration script for that version found')
        sys.exit()

    config_uri = argv[1]
    setup_logging(config_uri)
    settings = get_appsettings(config_uri)
    engine = create_engine('pyshop', settings, scoped=False)

    config = Configurator(settings=settings)
    config.end()

    migration.main(argv[:-1])
    dispose_engine('pyshop')


if __name__ == '__main__':
    main()
