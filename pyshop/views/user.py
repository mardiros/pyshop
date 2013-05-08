# -*- coding: utf-8 -*-
"""
PyShop User Management Views.

Used by the connected user to edit its account.
"""
from pyshop.models import User
from pyshop.helpers.i18n import trans as _

from .account import AccountMixin
from .base import EditView



class UserMixin(AccountMixin):
    redirect_route = 'list_package'

    def get_model(self):
        return self.user

    def update_view(self, model, view):
        pass


class Edit(UserMixin, EditView):
    """
    Edit connected user
    """


class ChangePassword(UserMixin, EditView):
    """
    Change current user password
    """

    def validate(self, model, errors):
        r = self.request

        if not User.by_credentials(self.session, model.login,
                                   r.params['current_password']):
            errors.append(_(u'current password is not correct'))
        elif r.params['user.password'] == r.params['current_password']:
            errors.append(_(u'password is inchanged'))

        if r.params['user.password'] != r.params['confirm_password']:
            errors.append(_(u'passwords do not match'))

        return len(errors) == 0
