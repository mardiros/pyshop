# -*- coding: utf-8 -*-
from pyramid.view import view_config

from .base import RedirectView


class Index(RedirectView):
    redirect_route = u'list_package'
