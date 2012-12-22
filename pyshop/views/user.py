import logging

from .base import View, CreateView, EditView, DeleteView

from pyshop.helpers.i18n import trans as _
from pyshop.models import User, Group


log = logging.getLogger(__name__)


class List(View):

    def render(self):

        return {u'user_count': User.get_locals(self.session, count=True),
                u'users': User.get_locals(self.session),
                }


class UserMixin:
    model = User
    matchdict_key = 'user_id'
    redirect_route = 'list_user'

    def update_view(self, model, view):
        view['groups'] = Group.all(self.session, order_by=Group.name)

    def append_groups(self, user):
        exists = []
        group_ids  = [int(id) for id in self.request.params.getall('groups')]

        for group in user.groups:
            exists.append(group.id)
            if group.id not in group_ids:
                user.groups.remove(group)

        for group_id in self.request.params.getall('groups'):
            if group_id not in exists:
                user.groups.append(Group.by_id(self.session, group_id))


class Create(UserMixin, CreateView):
    """
    Create user
    """

    def save_model(self, user):
        super(Create, self).update_model(user)
        self.append_groups(user)

    def validate(self, model, errors):
        r = self.request
        if r.params['user.password'] != r.params['confirm_password']:
            errors.append(_('password does not match'))
        return len(errors) == 0


class Edit(UserMixin, EditView):
    """
    Edit user
    """

    def save_model(self, user):
        super(Edit, self).update_model(user)
        self.append_groups(user)


class Delete(UserMixin, DeleteView):
    """
    Delete user
    """
