# -*- coding: utf-8 -*-
"""
PyShop Release File Download View.
"""
from pyramid.settings import asbool

from pyshop.models import DBSession, Release, ReleaseFile


def show_release_file(root, request):
    """
    Download a release file.
    Must be used with :func:`pyshop.helpers.download.renderer_factory`
    to download the release file.

    :return: download informations
    :rtype: dict
    """
    settings = request.registry.settings
    whlify = asbool(settings.get('pyshop.mirror.wheelify', '0'))
    session = DBSession()

    f = ReleaseFile.by_id(session, int(request.matchdict['file_id']))
    whlify = whlify and f.package_type == 'sdist'

    filename = f.filename_whlified if whlify else f.filename
    url = f.url
    if url and url.startswith('http://pypi.python.org'):
        url = 'https' + url[4:]

    rv = {'url': url,
          'filename': filename,
          'original': f.filename,
          'whlify': whlify
          }
    f.downloads += 1
    f.release.downloads += 1
    f.release.package.downloads += 1
    session.add(f.release.package)
    session.add(f.release)
    session.add(f)
    return rv


def show_external_release_file(root, request):
    """
    Download a release from a download url from its package information.
    Must be used with :func:`pyshop.helpers.download.renderer_factory`
    to download the release file.

    :return: download informations
    :rtype: dict
    """
    session = DBSession()

    settings = request.registry.settings
    whlify = asbool(settings.get('pyshop.mirror.wheelify', '0'))
    release = Release.by_id(session, int(request.matchdict['release_id']))

    rv = {'url': release.download_url,
          'filename': release.whlify_download_url_file,
          'original': release.download_url_file,
          'whlify': whlify
          }

    release.downloads += 1
    release.package.downloads += 1
    session.add(release.package)
    session.add(release)
    return rv
