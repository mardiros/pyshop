from python:2

# This image is intend to be used to test/develop
# pyshop in docker containers for mysql and postgresql
MAINTAINER Guillaume Gauvrit <guillaume@gauvr.it>

RUN apt-get update
RUN apt-get install -y python-dev libmysqlclient-dev libpq-dev git

RUN pip install git+https://github.com/mardiros/pyramid_xmlrpc.git
RUN pip install waitress mysql-python psycopg2

RUN useradd -m docker

ADD . /srv/pyshop
WORKDIR /srv/pyshop


RUN python setup.py install
RUN python setup.py develop

RUN chown -R docker /srv/pyshop

ENV PYSHOP_CONFIG_URI pyshop.sample.ini
RUN pyshop_setup -y $PYSHOP_CONFIG_URI

RUN cp /srv/pyshop/docker/entrypoint.sh /docker-entrypoint.sh
RUN chmod 750  /docker-entrypoint.sh
RUN chown docker /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

CMD pserve $PYSHOP_CONFIG_URI
