from python:2

RUN apt-get update
RUN apt-get install -y python-dev libmysqlclient-dev

RUN useradd -m docker


ADD . /srv/pyshop
WORKDIR /srv/pyshop

RUN python setup.py install
RUN pip install waitress
RUN pip install mysql-python
RUN python setup.py develop
RUN chown -R docker /srv/pyshop
RUN pyshop_setup -y development.ini
CMD pserve development.ini
