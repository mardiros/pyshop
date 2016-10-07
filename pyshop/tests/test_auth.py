from .case import UnauthenticatedViewTestCase
from . import setUpModule, tearDownModule

class AuthConfigTestaCase(UnauthenticatedViewTestCase):
    settings = {
        'pyshop.auth.web': 'session',
        'pyshop.auth.simple': 'basic',
        'pyshop.auth.other': 'remote_user',
        'pyshop.auth.methods.basic.type': 'basic',
        'pyshop.auth.methods.session.type': 'session',
        'pyshop.auth.methods.session.secret': 'imasecret',
        'pyshop.auth.methods.remote_user.type': 'remote_user',
        'pyshop.auth.methods.remote_user.email_domain': 'example.com'
    }

    @staticmethod
    def _callback():
        pass

    def test_basic_auth_from_config(self):
        from pyshop.helpers.authentication import auth_from_config
        from pyshop.helpers import authentication as auth
        af = auth_from_config('simple', self.settings)
        self.assertEqual(callable(af), True)
        a = af(self._callback)
        self.assertIsInstance(a, auth.AuthBasicAuthenticationPolicy)
        self.assertEqual(a.callback, self._callback)


    def test_session_auth_from_config(self):
        from pyshop.helpers.authentication import auth_from_config
        from pyshop.helpers import authentication as auth
        af = auth_from_config('web', self.settings)
        self.assertEqual(callable(af), True)
        a = af(self._callback)
        self.assertIsInstance(a, auth.AuthTktAuthenticationPolicy)
        self.assertEqual(a.callback, self._callback)


    def test_remote_user_auth_from_config(self):
        from pyshop.helpers.authentication import auth_from_config
        from pyshop.helpers import authentication as auth
        af = auth_from_config('other', self.settings)
        self.assertEqual(callable(af), True)
        a = af(self._callback)
        self.assertIsInstance(a, auth.DBRemoteUserAuthenticationPolicy)
        self.assertEqual(a.callback, self._callback)

