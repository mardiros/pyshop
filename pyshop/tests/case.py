import unittest

import transaction
from webob.multidict import MultiDict
from pyramid import testing
from pyramid.httpexceptions import HTTPFound
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
        self.session.flush()
        transaction.commit()
        testing.tearDown()

    def create_request(self, params=None, environ=None, matchdict=None,
                headers=None,
                path='/', cookies=None, post=None, **kw):
        if params and not isinstance(params, MultiDict):
            mparams = MultiDict()
            for k, v in params.items():
                if hasattr(v, '__iter__'):
                    [mparams.add(k, vv) for vv in v]
                else:
                    mparams.add(k, v)
                params = mparams
        rv  = DummyRequest(params, environ, headers, path, cookies,
                post, matchdict=(matchdict or {}), **kw)
        return rv

    def assertIsRedirect(self, view):
        self.assertIsInstance(view, HTTPFound)


class ViewTestCase(UnauthenticatedViewTestCase):

    def setUp(self):
        super(ViewTestCase, self).setUp()
        self.config.testing_securitypolicy(userid=u'admin',
                                           permissive=True)
