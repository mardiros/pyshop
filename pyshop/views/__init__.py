# -*- coding: utf-8 -*-
from .base import RedirectView


class Index(RedirectView):
    redirect_route = u'list_package'
