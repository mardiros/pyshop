# -*- coding: utf-8 -*-
import logging

from pyramid.httpexceptions import HTTPNotFound
from pyshop.models import User, Package, Classifier, Release, ReleaseFile

from .base import View

from pyshop.helpers.i18n import trans as _

log = logging.getLogger(__name__)


class List(View):

    def render(self, request, session):

        return {u'local_packages': Package.get_locals(session),
                u'mirrored_packages': Package.get_mirrored(session),
                }


class Show(View):

    def render(self, request, session):

        package = Package.by_name(session, request.matchdict['package_name'])
        if not package:
            raise HTTPNotFound()
        return { u'package': package}
