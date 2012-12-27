# -*- coding: utf-8 -*-
from pyshop.models import DBSession, ReleaseFile


def get_release_file(root, request):
    session = DBSession()

    f = ReleaseFile.by_id(session, int(request.matchdict['file_id']))
    rv = {'id': f.id,
          'url': f.url,
          'filename': f.filename,
          }
    f.downloads += 1
    f.release.downloads += 1
    f.release.package.downloads += 1
    session.add(f.release.package)
    session.add(f.release)
    session.add(f)
    return rv
