# -*- coding: utf-8 -*-
"""
PyShop Views baseclass.
"""
import logging

from pyramid.security import authenticated_userid
from pyramid.httpexceptions import HTTPFound
from pyramid.url import route_url

from pyshop.helpers.sqla import ModelError

from .. import __version__
from ..models import DBSession, User


log = logging.getLogger(__name__)

class ViewBase(object):
    """
    PyShop view base class.
    """

    def __init__(self, request):
        self.request = request
        self.session = DBSession()
        login = authenticated_userid(self.request)
        if login:
            self.login = login
            self.user = User.by_login(self.session, login)
        else:
           self.login = u'anonymous'
           self.user = None

    def update_response(self, response):
        pass

    def on_error(self, exception):
        return True

    def __call__(self):
        try:
            log.info('dispatch view %s', self.__class__.__name__)
            response = self.render()
            self.update_response(response)
            # if isinstance(response, dict):
            #     log.info("rendering template with context %r", dict)
            self.session.flush()
        except Exception as exc:
            if self.on_error(exc):
                log.error('Error on view %s' % self.__class__.__name__,
                          exc_info=True)
                raise
        return response

    def render(self):
        return {}


class View(ViewBase):
    """
    Base class of every views.
    """

    def update_response(self, response):
        # this is a view to render
        if isinstance(response, dict):
            global_ = {
                'pyshop': {
                    'version': __version__,
                    'login':  self.login,
                    'user':  self.user,
                    },
                }
            response.update(global_)


class RedirectView(View):
    """
    Base class of every view that redirect after post.
    """
    redirect_route = None
    redirect_kwargs = {}

    def render(self):
        return self.redirect()

    def redirect(self):
        return HTTPFound(location=route_url(self.redirect_route, self.request,
                                            **self.redirect_kwargs))


class CreateView(RedirectView):
    """
    Base class of every create view.
    """

    model = None
    matchdict_key = None

    def parse_form(self):
        kwargs = {}
        prefix = self.model.__tablename__
        for k, v in self.request.params.items():
            if v and k.startswith(prefix):
                kwargs[k.split('.').pop()] = v
        return kwargs

    def get_model(self):
        return self.model()

    def update_model(self, model):
        """
        trivial implementation for simple data in the form,
        using the model prefix.
        """
        for k, v in self.parse_form().items():
            setattr(model, k, v)

    def update_view(self, model, view):
        """
        render initialize trivial view propertie,
        but update_view is a method to customize the view to render.
        """

    def validate(self, model, errors):
        return len(errors) == 0

    def save_model(self, model):
        log.debug('saving %s' % model.__class__.__name__)
        log.debug('%r' % model.__dict__)
        self.session.add(model)

    def render(self):
        if 'form.cancelled' in self.request.params:
            return self.redirect()

        log.debug('rendering %s' % self.__class__.__name__)
        errors = []
        model = self.get_model()

        if 'form.submitted' in self.request.params:

            self.validate(model, errors)

            if not errors:
                try:
                    self.update_model(model)
                    model.validate(self.session)
                except ModelError as exc:
                    errors.extend(exc.errors)

            if not errors:
                self.save_model(model)
                return self.redirect()

        rv =  {'errors': errors, self.model.__tablename__: model}
        self.update_view(model, rv)
        log.debug(repr(rv))
        return rv


class EditView(CreateView):
    """
    Base class of every edit view.
    """

    def get_model(self):
        return self.model.by_id(self.session,
                                int(self.request.matchdict[self.matchdict_key]))


class DeleteView(RedirectView):
    """
    Base class of every delete view.
    """
    model = None
    matchdict_key = None
    redirect_route = None
    redirect_kwargs = {}

    def delete(self, model):
        self.session.delete(model)

    def render(self):

        model = self.model.by_id(self.session,
            int(self.request.matchdict[self.matchdict_key]))

        if 'form.submitted' in self.request.params:
            self.delete(model)
            return self.redirect()

        return {self.model.__tablename__: model}
