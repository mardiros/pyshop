from .account import AccountMixin
from .base import EditView


class UserMixin(AccountMixin):
    redirect_route = 'list_package'

    def get_model(self):
        return self.user


class Edit(UserMixin, EditView):
    """
    Edit account
    """
