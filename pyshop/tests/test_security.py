from .case import UnauthenticatedViewTestCase


class RootFactoryTestCase(UnauthenticatedViewTestCase):

    def test_get_acl_admin(self):
        from pyshop.security import RootFactory
        root = RootFactory(self.create_request())
        self.assertEqual(sorted(root.__acl__),
                         [(u'Allow', u'admin', u'admin_view'),
                          (u'Allow', u'admin', u'download_releasefile'),
                          (u'Allow', u'admin', u'upload_releasefile'),
                          (u'Allow', u'admin', u'user_view'),
                          (u'Allow', u'pip', u'download_releasefile'),
                          (u'Allow', u'user', u'download_releasefile'),
                          (u'Allow', u'user', u'upload_releasefile'),
                          (u'Allow', u'user', u'user_view'),
                          ])


class GroupFinderTestCase(UnauthenticatedViewTestCase):

    def test_admin_groups(self):
        from pyshop.security import groupfinder
        self.assertEqual(sorted(groupfinder(u'admin', self.create_request())),
                         [u'admin'])
        self.assertEqual(sorted(groupfinder(u'pip', self.create_request())),
                         [u'pip'])

    def test_user_groups(self):
        from pyshop.security import groupfinder
        self.assertEqual(groupfinder(u'local_user', self.create_request()),
                         [u'user'])
