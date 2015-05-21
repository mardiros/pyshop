#!/bin/bash

grep 'postgresql.localdomain' /etc/hosts &> /dev/null
if [ $? -eq 0 ]; then

  python /srv/pyshop/docker/create_database_pg.py $PYSHOP_CONFIG_URI
  pyshop_setup -y $PYSHOP_CONFIG_URI
fi

exec "$@"