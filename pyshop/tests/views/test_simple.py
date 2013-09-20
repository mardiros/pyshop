from pyshop.tests import case
from pyshop.tests import setUpModule, tearDownModule


class SimpleTestCase(case.ViewTestCase):

    def test_get_list_ok(self):
        from pyshop.views.simple import List
        view = List(self.create_request())()
        self.assertEqual(set(view.keys()), {'pyshop', 'packages'})
        packages = [p for p in view['packages']]
        self.assertEqual(len(packages), 3)

    def test_get_show_ok(self):
        from pyshop.views.simple import Show
        view = Show(self.create_request(matchdict={
            'package_name': u'mirrored_package1'
            }))()
        self.assertEqual(set(view.keys()), {'pyshop', 'package', 'whlify'})
        self.assertEqual(view['package'].name, u'mirrored_package1')

    def test_post_uploadreleasefile_existing_pkg_ko_403(self):
        from pyramid.httpexceptions import HTTPForbidden

        from pyshop.views.simple import UploadReleaseFile

        view = UploadReleaseFile(self.create_request({
            'name': u'mirrored_package1'
            }))
        # only owner and maintainer are authorized to upload
        self.assertRaises(HTTPForbidden, view)

    def test_post_uploadreleasefile_existing_pkg_ok(self):
        from cStringIO import StringIO
        from pyramid.httpexceptions import HTTPForbidden

        from pyshop.views.simple import UploadReleaseFile
        from pyshop.models import Package, Release, ReleaseFile

        class Content(object):
            filename = u'whatever.tar.gz'
            file = StringIO()

        view = UploadReleaseFile(self.create_request({
            'name': u'local_package1',
            'content': Content,
            'version': u'0.2',
            'filetype': u'sdist',
            'md5_digest': u'x' * 40,
            'home_page': u'http://local_package1'
            }))()
        self.assertEquals(set(view.keys()), {'pyshop', 'release_file'})
        self.assertEquals(view['release_file'].filename,
                          u'local_package1-0.2.tar.gz')
        self.assertEquals(view['release_file'].release.home_page,
                          u'http://local_package1')
        self.assertEquals(view['release_file'].release.author.login,
                          u'admin')
