from .case import ModelTestCase
from . import setUpModule, tearDownModule


class GroupTestCase(ModelTestCase):

    def test_by_name(self):
        from pyshop.models import Group
        grp = Group.by_name(self.session, u'admin')
        self.assertIsInstance(grp, Group)
        self.assertEqual(grp.name, u'admin')


class UserTestCase(ModelTestCase):

    def test_by_login_ok_mirrored(self):
        from pyshop.models import User
        user = User.by_login(self.session, u'johndo', local=False)
        self.assertIsInstance(user, User)
        self.assertEqual(user.login, u'johndo')

    def test_by_login_ko_mirrored(self):
        from pyshop.models import User
        user = User.by_login(self.session, u'johndo')
        self.assertEqual(user, None)

    def test_by_login_ok_local(self):
        from pyshop.models import User
        user = User.by_login(self.session, u'local_user')
        self.assertIsInstance(user, User)

    def test_by_credentials_ko_unexists(self):
        from pyshop.models import User
        user = User.by_credentials(self.session, u'u404', u"' OR 1 = 1 #")
        self.assertEqual(user, None)

    def test_by_credentials_ko_mirrored(self):
        from pyshop.models import User
        user = User.by_credentials(self.session, u'johndo', '')
        self.assertEqual(user, None)

    def test_by_credentials_ko_password(self):
        from pyshop.models import User
        user = User.by_credentials(self.session, u'admin', 'CHANGEME')
        self.assertIsNone(user)

    def test_by_credentials_ok(self):
        from pyshop.models import User
        user = User.by_credentials(self.session, u'local_user', 'secret')
        self.assertIsInstance(user, User)
        self.assertEqual(user.login, u'local_user')
        self.assertEqual(user.name, u'Local User')

    def test_hash_password(self):
        from pyshop.models import User
        u = User(login=u'test_password', password=u'secret')
        self.assertNotEqual(u.password, u'secret', 'password must be hashed')


class ClassifierTestCase(ModelTestCase):

    def test_by_name(self):
        from pyshop.models import Classifier
        clsfier = Classifier.by_name(self.session,
                                     u'Topic :: Software Development')
        self.assertIsInstance(clsfier, Classifier)
        self.assertEqual(clsfier.category, u'Topic')
        self.assertEqual(clsfier.name, u'Topic :: Software Development')

        parent = Classifier.by_name(self.session, u'Topic')
        self.assertEqual(clsfier.parent_id, parent.id)
        self.assertEqual(sorted([c.shortname for c in parent.childs]),
                         [u'Software Development', u'System'])


class PackageTestCase(ModelTestCase):

    def test_versions(self):
        from pyshop.models import Package
        pkg = Package.by_name(self.session, u'mirrored_package1')
        self.assertIsInstance(pkg, Package)
        self.assertEqual(pkg.id, 1)
        self.assertEqual(pkg.versions, [u'0.2', u'0.1'])

    def test_by_name(self):
        from pyshop.models import Package
        pkg = Package.by_name(self.session, u'mirrored_package1')
        self.assertIsInstance(pkg, Package)
        self.assertEqual(pkg.id, 1)
        self.assertEqual(pkg.name, u'mirrored_package1')

    def test_by_owner(self):
        from pyshop.models import Package
        pkges = Package.by_owner(self.session, u'johndo')
        self.assertIsInstance(pkges, list)
        pkges = [pkg.name for pkg in pkges]
        self.assertEqual(pkges, [u'mirrored_package1', u'mirrored_package2'])

    def test_by_maintainer(self):
        from pyshop.models import Package
        pkges = Package.by_maintainer(self.session, u'janedoe')
        self.assertIsInstance(pkges, list)
        pkges = [pkg.name for pkg in pkges]
        self.assertEqual(pkges, [u'mirrored_package2'])

    def test_get_locals(self):
        from pyshop.models import Package
        pkges = Package.get_locals(self.session)
        self.assertIsInstance(pkges, list)
        pkges = [pkg.name for pkg in pkges]
        self.assertEqual(pkges, [u'local_package1'])

    def test_get_mirrored(self):
        from pyshop.models import Package
        pkges = Package.get_mirrored(self.session)
        self.assertIsInstance(pkges, list)
        pkges = [pkg.name for pkg in pkges]
        self.assertEqual(pkges, [u'mirrored_package1', u'mirrored_package2'])


class ReleaseTestCase(ModelTestCase):

    def test_by_version(self):
        from pyshop.models import Release
        release = Release.by_version(self.session, u'mirrored_package2', u'1.0')
        self.assertIsInstance(release, Release)
        self.assertEqual(release.package.name, u'mirrored_package2')
        self.assertEqual(release.version, u'1.0')

    def test_by_classifiers(self):
        from pyshop.models import Release
        releases = Release.by_classifiers(self.session,
                                          [u'Intended Audience :: Developers'])
        self.assertIsInstance(releases, list)
        releases = [(r.package.name, r.version) for r in releases]
        self.assertEqual(releases, [(u'local_package1', u'0.1')])

    def test_search_by_author(self):
        from pyshop.models import Release
        releases = Release.search(self.session, {'author': 'janedoe'}, 'and')
        self.assertIsInstance(releases, list)
        releases = [(r.package.name, r.version) for r in releases]
        self.assertEqual(releases, [(u'mirrored_package1', u'0.1')])

    def test_sorted_releases(self):
        from pyshop.models import Package
        pkg = Package.by_name(self.session, u'mirrored_package1')
        self.assertEqual([release.version for release in pkg.sorted_releases],
                         ['0.2', '0.1'])


class ReleaseFileTestCase(ModelTestCase):

    def test_by_release(self):
        from pyshop.models import ReleaseFile
        files = ReleaseFile.by_release(self.session, u'mirrored_package2',
                                       u'1.0')
        self.assertIsInstance(files, list)
        files = [f.filename for f in files]
        self.assertEqual(files, [u'mirrored_package2-1.0.tar.gz'])

    def by_filename(self):
        from pyshop.models import ReleaseFile
        file = ReleaseFile.by_filename(self.session, u'mirrored_package1',
                                       u'mirrored_package1-0.2.egg')
        self.assertIsInstance(file, ReleaseFile)
        self.assertEqual(file.release.package.name, u'mirrored_package1')
        self.assertEqual(file.release.version, u'0.2')
        self.assertEqual(file.package_type, u'bdist_egg')
