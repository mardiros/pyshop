# -*- coding: utf-8 -*-
"""
Implement PyPiXmlRpc Service.

See: http://wiki.python.org/moin/PyPiXmlRpc

"""
import logging

from pyramid_rpc.xmlrpc import xmlrpc_method

from pyshop.models import DBSession, Package, Release, ReleaseFile
from pyshop.helpers import pypi

log = logging.getLogger(__name__)


@xmlrpc_method(endpoint='api')
def list_packages(request):
    """
    Retrieve a list of the package names registered with the package index.
    Returns a list of name strings.
    """
    session = DBSession()
    names = [p.name for p in Package.all(session, order_by=Package.name)]
    return names


@xmlrpc_method(endpoint='api')
def package_releases(request, package_name, show_hidden=False):
    """
    Retrieve a list of the releases registered for the given package_name.
    Returns a list with all version strings if show_hidden is True or
    only the non-hidden ones otherwise."""
    session = DBSession()
    package = Package.by_name(session, package_name)
    return [rel.version for rel in package.sorted_releases]


@xmlrpc_method(endpoint='api')
def package_roles(request, package_name):
    """
    Retrieve a list of users and their attributes roles for a given
    package_name. Role is either 'Maintainer' or 'Owner'.
    """
    session = DBSession()
    package = Package.by_name(session, package_name)
    owners = [('Owner', o.name) for o in package.owners]
    maintainers = [('Maintainer', o.name) for o in package.maintainers]
    return owners + maintainers


@xmlrpc_method(endpoint='api')
def user_packages(request, user):
    """
    Retrieve a list of [role_name, package_name] for a given username.
    Role is either 'Maintainer' or 'Owner'.
    """
    session = DBSession()
    owned = Package.by_owner(session, user)
    maintained = Package.by_maintainer(session, user)
    owned = [('Owner', p.name) for p in owned]
    maintained = [('Maintainer', p.name) for p in maintained]
    return owned + maintained


@xmlrpc_method(endpoint='api')
def release_downloads(request, package_name, version):
    """
    Retrieve a list of files and download count for a given package and
    release version.
    """
    session = DBSession()
    release_files = ReleaseFile.by_release(session, package_name, version)
    if release_files:
        release_files = [(f.release.package.name,
                            f.filename) for f in release_files]
    return release_files


@xmlrpc_method(endpoint='api')
def release_urls(request, package_name, version):
    """
    Retrieve a list of download URLs for the given package release.
    Returns a list of dicts with the following keys:
        url
        packagetype ('sdist', 'bdist', etc)
        filename
        size
        md5_digest
        downloads
        has_sig
        python_version (required version, or 'source', or 'any')
        comment_text
    """
    session = DBSession()
    release_files = ReleaseFile.by_release(session, package_name, version)
    return [{'url': f.url,
                'packagetype': f.package_type,
                'filename': f.filename,
                'size': f.size,
                'md5_digest': f.md5_digest,
                'downloads': f.downloads,
                'has_sig': f.has_sig,
                'comment_text': f.comment_text,
                'python_version': f.python_version
                }
            for f in release_files]


@xmlrpc_method(endpoint='api')
def release_data(request, package_name, version):
    """
    Retrieve metadata describing a specific package release.
    Returns a dict with keys for:
        name
        version
        stable_version
        author
        author_email
        maintainer
        maintainer_email
        home_page
        license
        summary
        description
        keywords
        platform
        download_url
        classifiers (list of classifier strings)
        requires
        requires_dist
        provides
        provides_dist
        requires_external
        requires_python
        obsoletes
        obsoletes_dist
        project_url
        docs_url (URL of the packages.python.org docs
                    if they've been supplied)
    If the release does not exist, an empty dictionary is returned.
    """
    session = DBSession()
    release = Release.by_version(session, package_name, version)

    if release:
        result = {'name': release.package.name,
                    'version': release.version,
                    'stable_version': '',
                    'author': release.author.name,
                    'author_email': release.author.email,
                    'home_page': release.home_page,
                    'license': release.license,
                    'summary': release.summary,
                    'description': release.description,
                    'keywords': release.keywords,
                    'platform': release.platform,
                    'download_url': release.download_url,
                    'classifiers': [c.name for c in release.classifiers],
                    #'requires': '',
                    #'requires_dist': '',
                    #'provides': '',
                    #'provides_dist': '',
                    #'requires_external': '',
                    #'requires_python': '',
                    #'obsoletes': '',
                    #'obsoletes_dist': '',
                    'bugtrack_url': release.bugtrack_url,
                    'docs_url': release.docs_url,
                    }

    if release.maintainer:
        result.update({'maintainer': release.maintainer.name,
                        'maintainer_email': release.maintainer.email,
                        })

    return dict([(key, val or '') for key, val in result.items()])


@xmlrpc_method(endpoint='api')
def search(request, spec, operator='and'):
    """
    Search the package database using the indicated search spec.

    The spec may include any of the keywords described in the above list
    (except 'stable_version' and 'classifiers'),
    for example: {'description': 'spam'} will search description fields.
    Within the spec, a field's value can be a string or a list of strings
    (the values within the list are combined with an OR),
    for example: {'name': ['foo', 'bar']}.
    Valid keys for the spec dict are listed here. Invalid keys are ignored:
        name
        version
        author
        author_email
        maintainer
        maintainer_email
        home_page
        license
        summary
        description
        keywords
        platform
        download_url
    Arguments for different fields are combined using either "and"
    (the default) or "or".
    Example: search({'name': 'foo', 'description': 'bar'}, 'or').
    The results are returned as a list of dicts
    {'name': package name,
        'version': package release version,
        'summary': package release summary}
    """
    api = pypi.proxy
    rv = []
    # search in proxy
    for k, v in spec.items():
        rv += api.search({k: v}, True)

    # search in local
    session = DBSession()
    release = Release.search(session, spec, operator)
    rv += [{'name': r.package.name,
            'version': r.version,
            'summary': r.summary,
            # hack https://mail.python.org/pipermail/catalog-sig/2012-October/004633.html
            '_pypi_ordering':'',
            } for r in release]
    return rv


@xmlrpc_method(endpoint='api')
def browse(request, classifiers):
    """
    Retrieve a list of (name, version) pairs of all releases classified
    with all of the given classifiers. 'classifiers' must be a list of
    Trove classifier strings.

    changelog(since)
    Retrieve a list of four-tuples (name, version, timestamp, action)
    since the given timestamp. All timestamps are UTC values.
    The argument is a UTC integer seconds since the epoch.
    """
    session = DBSession()
    release = Release.by_classifiers(session, classifiers)
    rv = [(r.package.name, r.version) for r in release]
    return rv
