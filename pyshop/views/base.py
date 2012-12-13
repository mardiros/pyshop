# -*- coding: utf-8 -*-
import logging

from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url

from pyshop.helpers.i18n import trans as _

from .. import __version__
from ..models import DBSession, User


log = logging.getLogger(__name__)

class ViewBase(object):

    def update_response(self, request, session, response):
        pass

    def on_error(self, request, exception):
        return True

    def __call__(self, request):
        try:
            log.info("dispatch view %s", self.__class__.__name__)

            session = DBSession()
            response = self.render(request, session)
            self.update_response(request, session, response)
            # if isinstance(response, dict):
            #     log.info("rendering template with context %r", dict)
        except Exception, exc:
            if self.on_error(request, exc):
                log.error("Error on view %s" % self.__class__.__name__,
                          exc_info=True)
                raise

        return response

    def render(self, request, session):
        return {}


class View(ViewBase):

    def update_response(self, request, session, response):
        # this is a view to render
        if isinstance(response, dict):
            login = authenticated_userid(request) or u'anonymous'
            global_ = {
                'pyshop': {
                    'version': __version__,
                    'login':  login,
                    },
                }
            if login != u'anonymous':
                 global_['pyshop']['user'] = User.by_login(session, login)
            response.update(global_)


class RedirectView(View):
    redirect_route = None
    redirect_kwargs = {}

    def render(self, request, session):
        return self.redirect(request)

    def redirect(self, request):
        return HTTPFound(location=route_url(self.redirect_route, request,
                                            **self.redirect_kwargs))
