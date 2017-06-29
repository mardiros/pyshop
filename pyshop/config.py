#-*- coding: utf-8 -*-
"""
PyShop Pyramid configuration helpers.
"""

from pyramid.interfaces import IBeforeRender
from pyramid.url import static_path, route_path
from pyramid.httpexceptions import HTTPNotFound
from pyramid_jinja2 import renderer_factory
from pyramid_rpc.xmlrpc import XMLRPCRenderer

from pyshop.helpers import pypi
from pyshop.helpers.restxt import parse_rest
from pyshop.helpers.download import renderer_factory as dl_renderer_factory


def notfound(request):
    return HTTPNotFound('Not found.')


def add_urlhelpers(event):
    """
    Add helpers to the template engine.
    """
    event['static_url'] = lambda x: static_path(x, event['request'])
    event['route_url'] = lambda name, *args, **kwargs: \
        route_path(name, event['request'], *args, **kwargs)
    event['parse_rest'] = parse_rest
    event['has_permission'] = event['request'].has_permission


def includeme(config):
    """
    Pyramid includeme file for the :class:`pyramid.config.Configurator`
    """
    settings = config.registry.settings

    # config.add_renderer('json', JSONP())
    # release file download
    config.add_renderer('repository', dl_renderer_factory)

    # Jinja configuration
    # We don't use jinja2 filename, .html instead
    config.add_renderer('.html', renderer_factory)
    # helpers
    config.add_subscriber(add_urlhelpers, IBeforeRender)
    # i18n
    config.add_translation_dirs('locale/')

    pypi_url = settings.get('pyshop.pypi.url', 'https://pypi.python.org/pypi')
    # PyPI url for XML RPC service consume
    pypi.set_proxy(pypi_url,
                   settings.get('pyshop.pypi.transport_proxy'))

    # Javascript + Media
    config.add_static_view('static', 'static', cache_max_age=3600)
    # config.add_static_view('repository', 'repository', cache_max_age=3600)

    config.add_route(u'login', u'/login',)
    config.add_view(u'pyshop.views.credentials.Login',
                    route_name=u'login',
                    renderer=u'shared/login.html')

    config.add_route(u'logout', u'/logout')
    config.add_view(u'pyshop.views.credentials.Logout',
                    route_name=u'logout',
                    permission=u'user_view')

    # Home page
    config.add_route(u'index', u'/')
    config.add_view(u'pyshop.views.Index',
                    route_name=u'index',
                    permission=u'user_view')

    # Archive downloads
    config.add_route(u'show_external_release_file',
                     u'/repository/ext/{release_id}/{filename:.*}',
                     request_method=u'GET')
    config.add_view(u'pyshop.views.repository.show_external_release_file',
                    route_name=u'show_external_release_file',
                    renderer=u'repository',
                    permission=u'download_releasefile')

    config.add_route(u'show_release_file',
                     u'/repository/{file_id}/{filename:.*}',
                     request_method=u'GET')
    config.add_view(u'pyshop.views.repository.show_release_file',
                    route_name=u'show_release_file',
                    renderer=u'repository',
                    permission=u'download_releasefile')

    # Simple views used by pip
    config.add_route(u'list_simple', u'/simple/', request_method=u'GET')

    config.add_view(u'pyshop.views.simple.List',
                    route_name=u'list_simple',
                    renderer=u'pyshop/simple/list.html',
                    permission=u'download_releasefile')

    config.add_route(u'show_simple', u'/simple/{package_name}/')
    config.add_view(u'pyshop.views.simple.Show',
                    route_name=u'show_simple',
                    renderer=u'pyshop/simple/show.html',
                    permission=u'download_releasefile')

    try:
        config.add_notfound_view(notfound, append_slash=True)
    except AttributeError:
        # Pyramid < 1.4
        pass


    # Used by setup.py sdist upload

    config.add_route(u'upload_releasefile', u'/simple/',
                     request_method=u'POST')

    config.add_view(u'pyshop.views.simple.UploadReleaseFile',
                    renderer=u'pyshop/simple/create.html',
                    route_name=u'upload_releasefile',
                    permission=u'upload_releasefile')

    # Web Services

    config.add_renderer('pyshopxmlrpc', XMLRPCRenderer(allow_none=True))
    config.add_xmlrpc_endpoint(
        'api', '/pypi/xmlrpc', default_renderer='pyshopxmlrpc')
    config.scan('pyshop.views.xmlrpc')

    # Backoffice Views

    config.add_route(u'list_package', u'/pyshop/package')
    config.add_view(u'pyshop.views.package.List',
                    route_name='list_package',
                    renderer=u'pyshop/package/list.html',
                    permission=u'user_view')

    config.add_route(u'list_package_page', u'/pyshop/package/p/{page_no}')
    config.add_view(u'pyshop.views.package.List',
                    route_name='list_package_page',
                    renderer=u'pyshop/package/list.html',
                    permission=u'user_view')

    config.add_route(u'show_package',
                     u'/pyshop/package/{package_name}')

    config.add_route(u'show_package_version',
                     u'/pyshop/package/{package_name}/{release_version}')

    config.add_view(u'pyshop.views.package.Show',
                    route_name=u'show_package',
                    renderer=u'pyshop/package/show.html',
                    permission=u'user_view')

    config.add_view(u'pyshop.views.package.Show',
                    route_name=u'show_package_version',
                    renderer=u'pyshop/package/show.html',
                    permission=u'user_view')

    # Admin  view
    config.add_route(u'list_account', u'/pyshop/account')
    config.add_view(u'pyshop.views.account.List',
                    route_name=u'list_account',
                    renderer=u'pyshop/account/list.html',
                    permission=u'admin_view')

    config.add_route(u'create_account', u'/pyshop/account/new')
    config.add_view(u'pyshop.views.account.Create',
                    route_name=u'create_account',
                    renderer=u'pyshop/account/create.html',
                    permission=u'admin_view')

    config.add_route(u'edit_account', u'/pyshop/account/{user_id}')
    config.add_view(u'pyshop.views.account.Edit',
                    route_name=u'edit_account',
                    renderer=u'pyshop/account/edit.html',
                    permission=u'admin_view')

    config.add_route(u'delete_account', u'/pyshop/delete/account/{user_id}')
    config.add_view(u'pyshop.views.account.Delete',
                    route_name=u'delete_account',
                    renderer=u'pyshop/account/delete.html',
                    permission=u'admin_view')

    config.add_route(u'purge_package', u'/pyshop/purge/package/{package_id}')
    config.add_view(u'pyshop.views.package.Purge',
                    route_name=u'purge_package',
                    renderer=u'pyshop/package/purge.html',
                    permission=u'admin_view')

    # Current user can update it's information
    config.add_route(u'edit_user', u'/pyshop/user')
    config.add_view(u'pyshop.views.user.Edit',
                    route_name=u'edit_user',
                    renderer=u'pyshop/user/edit.html',
                    permission=u'user_view')

    config.add_route(u'change_password', u'/pyshop/user/password')
    config.add_view(u'pyshop.views.user.ChangePassword',
                    route_name=u'change_password',
                    renderer=u'pyshop/user/change_password.html',
                    permission=u'user_view')

    # Credentials
    for route in ('list_simple', 'show_simple',
                  'show_release_file', 'show_external_release_file',
                  'upload_releasefile'):
        config.add_view('pyshop.views.credentials.authbasic',
                        route_name=route,
                        context='pyramid.exceptions.Forbidden'
                        )

    config.add_view('pyshop.views.credentials.Login',
                    renderer=u'shared/login.html',
                    context=u'pyramid.exceptions.Forbidden')
