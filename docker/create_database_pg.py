#!/usr/bin/python
"""
Create the database and the user/role, associate it in case,
the database does not exists.

"""
import sys
import psycopg2
import logging
from datetime import datetime, timedelta
import time

from pyramid.paster import get_appsettings, setup_logging

from sqlalchemy.engine.url import make_url

config_uri = sys.argv[1]

setup_logging(config_uri)
settings = get_appsettings(config_uri)
log = logging.getLogger(__name__)


setting_url = settings['sqlalchemy.url']
url = make_url(setting_url)

if url.drivername not in ('postgresql', 'postgresql+psycopg2'):
    log.warn('{0} is not a postgresql database. ignored'.format(setting_url))
    sys.exit(0)

params = {'db': url.database,
          'user': url.username,
          'password': url.password,
          'encoding': 'utf-8',
          }

# wait util the docker container is ready
con = psycopg2.connect(database='postgres', user='postgres',
                       host=url.host,
                       port=(url.port or 5432),
                       async=1)

log.info('Waiting connection to {host}'.format(host=url.host))
time_end = datetime.now() + timedelta(seconds=10)
while time_end > datetime.now():
    try:
        state = con.poll()
    except:
        pass
    if state == psycopg2.extensions.POLL_OK:
        break
    time.sleep(0.2)
if not con.status:
    raise RuntimeError('Could not connect to SQL server in less than '
                       '%r seconds' % 10)
con.close()

con = None
try:
    log.info('Connecting to {host}'.format(host=url.host))
    con = psycopg2.connect(database='postgres', user='postgres',
                           host=url.host,
                           port=(url.port or 5432))
    con.set_session(autocommit=True)
    cur = con.cursor()
    cur.execute("""SELECT count(*)
                   FROM pg_user
                   WHERE usename = '{user}'
                   """.format(**params))
    exists = cur.fetchone()[0]
    if not exists:
        log.info('Create user {user}'.format(**params))
        cur.execute(""" CREATE USER {user} WITH PASSWORD '{password}'
                    """.format(**params))

    cur.execute("""SELECT count(*)
                   FROM pg_database
                   WHERE datname = '{db}'
                   """.format(**params))
    exists = cur.fetchone()[0]
    if not exists:
        log.info('Create database {db}'.format(**params))
        cur.execute(""" CREATE DATABASE {db}
                        WITH owner = {user}
                        ENCODING '{encoding}'
                    """.format(**params))
    con.commit()
    con = psycopg2.connect(database=params['db'], user='postgres',
                           host=url.host,
                           port=(url.port or 5432))
    con.set_session(autocommit=True)
    cur = con.cursor()
    cur.execute("""CREATE EXTENSION IF NOT EXISTS "uuid-ossp" """)
    con.commit()
    con = None
except psycopg2.DatabaseError as exc:
    import traceback
    traceback.print_exc(file=sys.stderr)
    # sys.exit(1)
finally:
    if con:
        con.close()
