from .models import DBSession, User, Group

class GroupFinder(object):

    _users = {}

    def reset(self):
        self._users = {}

    def __call__(self, login, request):

        if login in self._users:
            return self._users[login]

        user = User.by_login(DBSession(), login)
        if user:
            rv =  [g.name for g in user.groups]
        else:
            rv = []
        self._users[login] = rv
        return rv

groupfinder = GroupFinder()
