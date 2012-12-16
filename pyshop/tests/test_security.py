from .case import UnauthenticatedViewTestCase


class RootFactoryTestCase(UnauthenticatedViewTestCase):

    def test_get_acl_admin(self):
        from pyshop.security import RootFactory
        root = RootFactory(self.create_request())
        self.assertEqual(root.__acl__,
                         [('Allow', u'user', u'user_view'),
                          ('Allow', u'user', u'download_releasefile'),
                          ('Allow', u'user', u'upload_releasefile'),
                          ('Allow', u'admin', u'user_view'),
                          ('Allow', u'admin', u'download_releasefile'),
                          ('Allow', u'admin', u'upload_releasefile'),
                          ('Allow', u'admin', u'admin_view')])


class GroupFinderTestCase(UnauthenticatedViewTestCase):

    def test_admin_groups(self):
        from pyshop.security import groupfinder
        self.assertEqual(sorted(groupfinder('admin', self.create_request())),
                         [u'admin', u'user'])

    def test_user_groups(self):
        from pyshop.security import groupfinder
        self.assertEqual(groupfinder('local_user', self.create_request()),
                         [u'user'])
