# -*- coding: utf-8 -*-

from .base import RedirectView

from . import credentials
from . import simple
from . import package

class _Index(RedirectView):
    redirect_route = u'list_package'

index = _Index()
login = credentials.Login()
logout = credentials.Logout()

list_simple = simple.List()
show_simple = simple.Show()

list_package = package.List()
show_package = package.Show()
