import unittest

import transaction
from webob.multidict import MultiDict
from pyramid import testing
from pyramid.authorization import ACLAuthorizationPolicy

from pyshop.models import DBSession


class ModelTestCase(unittest.TestCase):

    def setUp(self):
        transaction.begin()
        self.session = DBSession()

    def tearDown(self):
        transaction.commit()

class DummyRoute(object):
    name = 'index'


class DummyRequest(testing.DummyRequest):
    method = u'GET'
    application_url = u'http://pyshop.exemple.net'
    host = u'pyshop.exemple.net:80'
    client_addr = u'127.0.0.8'
    matched_route = DummyRoute


class UnauthenticatedViewTestCase(unittest.TestCase):

    def setUp(self):
        from pyshop.config import includeme
        from .conf import settings
        super(UnauthenticatedViewTestCase, self).setUp()
        self.maxDiff = None
        authz_policy = ACLAuthorizationPolicy()
        self.config = testing.setUp(settings=settings)
        self.config.include(includeme)
        self.session = DBSession()
        transaction.begin()

    def tearDown(self):
        super(UnauthenticatedViewTestCase, self).tearDown()
        transaction.commit()
        testing.tearDown()

    def create_request(self, params=None, environ=None, matchdict=None,
                headers=None,
                path='/', cookies=None, post=None, **kw):
        if params and not isinstance(params, MultiDict):
            params = MultiDict(**params)
        rv  = DummyRequest(params, environ, headers, path, cookies,
                post, matchdict=(matchdict or {}), **kw)
        return rv

    def assertIsRedirect(self, view, *args, **kwargs):
        self.assertIsInstance(view, HTTPFound, *args, **kwargs)
