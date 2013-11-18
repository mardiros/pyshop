from .case import UnauthenticatedViewTestCase
from . import setUpModule, tearDownModule


class RootFactoryTestCase(UnauthenticatedViewTestCase):

    def test_get_acl_admin(self):
        from pyshop.security import RootFactory
        root = RootFactory(self.create_request())
        self.assertEqual(set(root.__acl__),
                         set([# all rights
                              (u'Allow', u'admin', u'admin_view'),
                              (u'Allow', u'admin', u'download_releasefile'),
                              (u'Allow', u'admin', u'upload_releasefile'),
                              (u'Allow', u'admin', u'user_view'),

                              # installer can download packages
                              (u'Allow', u'installer', u'download_releasefile'),

                              # installer can download/upload packages,
                              # and browse packages
                              (u'Allow', u'developer', u'download_releasefile'),
                              (u'Allow', u'developer', u'upload_releasefile'),
                              (u'Allow', u'developer', u'user_view'),
                              ]))


class GroupFinderTestCase(UnauthenticatedViewTestCase):

    def test_admin_groups(self):
        from pyshop.security import groupfinder
        self.assertEqual(set(groupfinder(u'admin', self.create_request())),
                         set([u'admin']))

    def test_installer_groups(self):
        from pyshop.security import groupfinder
        self.assertEqual(set(groupfinder(u'pip', self.create_request())),
                         set([u'installer']))

    def test_dev_groups(self):
        from pyshop.security import groupfinder
        self.assertEqual(set(groupfinder(u'local_user', self.create_request())),
                         set([u'developer']))

