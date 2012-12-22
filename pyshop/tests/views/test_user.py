from pyshop.tests import case


class UserTestCase(case.ViewTestCase):

    def setUp(self):
        super(UserTestCase, self).setUp()
        import uuid
        import transaction
        from pyshop.models import User, Group
        self.user_login = unicode(uuid.uuid4())
        u = User(login=self.user_login, password=u'secret')
        u.groups.append(Group.by_name(self.session, u'user'))
        self.session.add(u)
        self.session.flush()
        self.user_id = u.id
        self.user_todelete = [self.user_id]

    def tearDown(self):
        from pyshop.models import User
        for id in self.user_todelete:
            u = User.by_id(self.session, id)
            self.session.delete(u)
        super(UserTestCase, self).tearDown()

    def test_get_list_ok(self):
        from pyshop.models import User
        from pyshop.views.user import List
        view = List(self.create_request())()
        self.assertEqual(set(view.keys()), {'pyshop', 'user_count', 'users'})
        self.assertEqual(view['user_count'], 4)
        self.assertEqual(len(view['users']), 4)
        self.assertIsInstance(view['users'][0], User)

    def test_get_create_ok(self):
        from pyshop.views.user import Create
        from pyshop.models import User, Group
        view = Create(self.create_request())()
        self.assertEqual(set(view.keys()), {'errors', 'groups', 'pyshop',
                                            'user'})
        self.assertEqual(view['errors'], [])
        groups = [g for g in view['groups']]
        self.assertEqual(len(groups), 3)
        self.assertIsInstance(groups[0], Group)
        self.assertIsInstance(view['user'], User)
        self.assertIsNone(view['user'].id)
        self.assertIsNone(view['user'].login)

    def test_post_create_ok(self):
        from pyshop.views.user import Create
        from pyshop.models import User, Group
        view = Create(self.create_request({'form.submitted': u'1',
                                           'user.login': u'dummy_new',
                                           'user.password': u'secret',
                                           'user.firstname': u'',
                                           'user.lastname': u'',
                                           'user.email': u'me@me.me',
                                           'confirm_password': u'secret',
                                           'groups': [u'1', u'2']
                                           }))()
        self.assertIsRedirect(view)
        self.user_todelete.append(User.by_login(self.session, u'dummy_new').id)

    def test_get_edit_ok(self):
        from pyshop.views.user import Edit
        from pyshop.models import User, Group
        view = Edit(self.create_request(matchdict={'user_id': self.user_id}))()
        self.assertEqual(set(view.keys()), {'errors', 'groups', 'pyshop',
                                               'user'})
        self.assertEqual(view['errors'], [])
        groups = [g for g in view['groups']]
        self.assertEqual(len(groups), 3)
        self.assertIsInstance(groups[0], Group)
        self.assertIsInstance(view['user'], User)
        self.assertEqual(view['user'].id, self.user_id)
        self.assertEqual(view['user'].login, self.user_login)

    def test_post_edit_ok(self):
        from pyshop.views.user import Edit
        from pyshop.models import User, Group
        view = Edit(self.create_request({'form.submitted': '1',
                                         'user.login': u'dummy_edited',
                                         'user.firstname': u'',
                                         'user.lastname': u'',
                                         'user.email': u'me@me.me',
                                         'groups': [u'1']
                                         },
                                        matchdict={'user_id': self.user_id}))()
        self.assertIsRedirect(view)
        self.session.flush()
        user = User.by_id(self.session, self.user_id)
        self.assertEqual(user.login, u'dummy_edited')
        self.assertEqual([g.id for g in user.groups], [1])

    def test_get_delete_ok(self):
        from pyshop.views.user import Delete
        from pyshop.models import User
        view = Delete(self.create_request(matchdict={'user_id': self.user_id
                                                     }))()
        self.assertEqual(set(view.keys()), {'pyshop', 'user'})
        self.assertIsInstance(view['user'], User)
        self.assertEqual(view['user'].id, self.user_id)
        self.assertEqual(view['user'].login, self.user_login)

    def test_post_delete_ok(self):
        from pyshop.views.user import Delete
        from pyshop.models import User
        view = Delete(self.create_request({'form.submitted': '1',
                                           },
                                          matchdict={'user_id': self.user_id
                                                     },))()
        self.assertIsRedirect(view)
        user = User.by_id(self.session, self.user_id)
        self.assertIsNone(user)
        self.user_todelete = []
