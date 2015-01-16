from pyshop.tests import case
from pyshop.tests import setUpModule, tearDownModule


class PackageTestCase(case.ViewTestCase):

    def test_list_default_ok(self):
        from pyshop.models import Package, Classifier
        from pyshop.views.package import List
        view = List(self.create_request())()
        self.assertEqual(set(view.keys()),
                         set(['pyshop', 'has_page', 'paging', 'filter',
                              'package_count', 'packages', 'classifiers']))
        # by default, list filter local packages
        self.assertEqual(view['package_count'], 1)
        self.assertEqual(len(view['packages']), 1)
        self.assertIsInstance(view['packages'][0], Package)

        classifiers = [c for c in view['classifiers']]
        self.assertEqual(len(classifiers), 13)
        self.assertIsInstance(classifiers[0], Classifier)

    def test_show_ok(self):
        from pyshop.models import Package
        from pyshop.views.package import Show
        view = Show(self.create_request(
            matchdict={'package_name': u'local_package1'}))()
        self.assertEqual(set(view.keys()),
                         set(['pyshop', 'release', 'package',
                              'can_edit_role']))
        self.assertIsInstance(view['package'], Package)
        self.assertEqual(view['package'].name, u'local_package1')
