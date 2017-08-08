
import unittest

import pyramid

import pyshop.tests

from copy import deepcopy

from nose.tools import raises
from pyramid.exceptions import HTTPForbidden

from ..case import ViewTestCase
from pyshop.models import create_engine, dispose_engine
from pyshop.compat import StringIO


setUpModule = pyshop.tests.setUpModule

tearDownModule = pyshop.tests.tearDownModule


class DummyContent(object):
    filename = u'whatever.tar.gz'
    file = StringIO()


class SimpleTestCase(ViewTestCase):

    def test_get_list_ok(self):
        from pyshop.views.simple import List
        view = List(self.create_request())()
        self.assertEqual(set(view.keys()),
                         set(['pyshop', 'packages']))
        packages = [p for p in view['packages']]
        self.assertEqual(len(packages), 3)

    def test_get_show_ok(self):
        from pyshop.views.simple import Show
        view = Show(self.create_request(matchdict={
            'package_name': u'mirrored_package1'
            }))()
        self.assertEqual(set(view.keys()),
                         set(['pyshop', 'package', 'whlify']))
        self.assertEqual(view['package'].name, u'mirrored_package1')

    def test_post_uploadreleasefile_mirrored_pkg(self):

        from pyshop.views.simple import UploadReleaseFile
        from pyshop.models import ReleaseFile

        view = UploadReleaseFile(self.create_request({
            'name': u'mirrored_package1',
            'version': u'0.2',
            'filetype': u'sdist',
            'md5_digest': u'x' * 40,
            },
            post={'content': DummyContent}))()
        self.assertIsInstance(view['release_file'], ReleaseFile)

    def test_post_uploadreleasefile_existing_pkg_ok(self):

        from pyshop.views.simple import UploadReleaseFile

        view = UploadReleaseFile(self.create_request({
            'name': u'local_package1',
            'content': DummyContent,
            'version': u'0.2',
            'filetype': u'sdist',
            'md5_digest': u'x' * 40,
            'home_page': u'http://local_package1'
            }))()
        self.assertEqual(set(view.keys()),
                         set(['pyshop', 'release_file']))
        self.assertEqual(view['release_file'].filename,
                         u'local_package1-0.2.tar.gz')
        self.assertEqual(view['release_file'].release.home_page,
                         u'http://local_package1')
        self.assertEqual(view['release_file'].release.author.login,
                         u'admin')

    @raises(HTTPForbidden)
    def test_post_uploadreleasefile_bad_version(self):

        from pyshop.views.simple import UploadReleaseFile

        settings = pyramid.threadlocal.get_current_registry().settings
        settings['pyshop.upload.sanitize'] = 1

        UploadReleaseFile(self.create_request({
            'version': u'0.1dev',
        }))()


class SimpleUploadReleaseFileBadVersionFunctionalTests(unittest.TestCase):

    def setUp(self):
        from pyshop import main
        from ..conf import settings
        settings = deepcopy(settings)
        settings['pyshop.upload.sanitize'] = 1
        app = main({}, **settings)

        from pyshop.bin.install import populate
        engine = create_engine(settings)
        populate(engine, interactive=False)

        from webtest import TestApp
        self.testapp = TestApp(app)

    def tearDown(self):
        dispose_engine()

    def test_post_uploadreleasefile_bad_version_403(self):

        self.testapp.authorization = ('Basic', ('admin', 'changeme'))
        self.testapp.post('/simple/', {'version': '0.1dev'}, status=403)
