from python:2

# This image is intend to be used to test/develop
# pyshop in docker containers for mysql and postgresql
MAINTAINER Guillaume Gauvrit <guillaume@gauvr.it>

RUN apt-get update
RUN apt-get install -y python-dev libmysqlclient-dev libpq-dev

RUN useradd -m docker


ADD . /srv/pyshop
WORKDIR /srv/pyshop

RUN python setup.py install
RUN pip install waitress mysql-python psycopg2
RUN python setup.py develop
RUN chown -R docker /srv/pyshop
RUN pyshop_setup -y development.ini
CMD pserve development.ini
