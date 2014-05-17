
from pyshop.tests import case
from pyshop.tests import setUpModule, tearDownModule
from pyshop.compat import StringIO

class DummyContent(object):
    filename = u'whatever.tar.gz'
    file = StringIO()


class SimpleTestCase(case.ViewTestCase):

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
        from pyramid.httpexceptions import HTTPForbidden

        from pyshop.views.simple import UploadReleaseFile
        from pyshop.models import Package, Release, ReleaseFile

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
