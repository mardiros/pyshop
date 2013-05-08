# -*- coding: utf-8 -*-
"""
PyShop Views
"""
from .base import RedirectView


class Index(RedirectView):
    """
    PyShop index view.
    """
    redirect_route = u'list_package'
