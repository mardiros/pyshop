# -*- coding: utf-8 -*-
"""
PyShop Account Management Views.

Used by administrator to manage user account.
"""
import logging

from .base import View, CreateView, EditView, DeleteView

from pyshop.helpers.i18n import trans as _
from pyshop.models import User, Group


log = logging.getLogger(__name__)


class List(View):
    """
    List All user accounts
    """
    def render(self):

        return {u'user_count': User.get_locals(self.session, count=True),
                u'users': User.get_locals(self.session),
                }


class AccountMixin:
    model = User
    matchdict_key = 'user_id'
    redirect_route = 'list_account'

    def update_view(self, model, view):
        view['groups'] = Group.all(self.session, order_by=Group.name)

    def append_groups(self, account):
        exists = []
        group_ids  = [int(id) for id in self.request.params.getall('groups')]

        for group in account.groups:
            exists.append(group.id)
            if group.id not in group_ids:
                account.groups.remove(group)

        for group_id in self.request.params.getall('groups'):
            if group_id not in exists:
                account.groups.append(Group.by_id(self.session, group_id))


class Create(AccountMixin, CreateView):
    """
    Create account
    """

    def save_model(self, account):
        super(Create, self).update_model(account)
        self.append_groups(account)

    def validate(self, model, errors):
        r = self.request
        if r.params['user.password'] != r.params['confirm_password']:
            errors.append(_('passwords do not match'))
        return len(errors) == 0


class Edit(AccountMixin, EditView):
    """
    Edit account
    """

    def save_model(self, account):
        super(Edit, self).update_model(account)
        self.append_groups(account)


class Delete(AccountMixin, DeleteView):
    """
    Delete account
    """
