from pyshop.models import (create_engine, dispose_engine,
                           Base, DBSession,
                           Group, User, Permission,
                           Classifier, Package, Release,  ReleaseFile
                           )
from pyshop.bin.install import populate


SQLA_SETTINGS = {
    'sqlalchemy.url': 'sqlite://',
    'sqlalchemy.echo': False,
    'sqlalchemy.pool_size': 1
    }


def setUp():

    engine = create_engine(SQLA_SETTINGS)
    populate(engine, interactive=False)

    session = DBSession()
    local_user = User(login=u'local_user', password=u'secret', local=True,
                      firstname='Local', lastname='User')
    jdo = User(login=u'johndo', local=False)
    jdoe = User(login=u'janedoe', local=False)

    session.add(jdo)
    session.add(jdoe)
    session.add(local_user)

    classifiers_names = [u'Programming Language :: Python',
                         u'Programming Language :: Python :: 2.6',
                         u'Programming Language :: Python :: 2.7',
                         u'Topic :: Software Development',
                         u'Topic :: System :: Archiving :: Mirroring',
                         u'Topic :: System :: Archiving :: Packaging',
                         u'Intended Audience :: Developers',
                         u'Intended Audience :: System Administrators'
                         ]
    classifiers = [Classifier(name=c)  for c in classifiers_names]
    [session.add(c) for c in classifiers]

    pack1 = Package(name=u'mirrored_package1')
    pack1.owners.append(jdo)
    pack1.owners.append(jdoe)
    pack1.downloads = 7
    session.add(pack1)

    release1 = Release(package=pack1, version=u'0.1',
                       summary='Common Usage Library',
                       author=jdoe)
    for c in classifiers[:3]:
        release1.classifiers.append(c)
    session.add(release1)
    release1.files.append(ReleaseFile(filename=u'mirrored_package1-0.1.tar.gz',
                                      package_type=u'sdist'))
    session.add(release1)

    release2 = Release(package=pack1, version=u'0.2',
                       summary='Common Usage Library')
    for c in classifiers[:5]:
        release2.classifiers.append(c)
    release2.files.append(ReleaseFile(filename=u'mirrored_package1-0.2.tar.gz',
                                      package_type=u'sdist'))
    release2.files.append(ReleaseFile(filename=u'mirrored_package1-0.2.egg',
                                      package_type=u'bdist_egg'))
    session.add(release2)

    pack2 = Package(name=u'mirrored_package2')
    pack2.owners.append(jdo)
    pack2.maintainers.append(jdoe)
    pack2.downloads = 1
    session.add(pack2)

    release3 = Release(package=pack2, version=u'1.0',
                       summary='Web Framework For Everybody')
    for c in classifiers[:3] + classifiers[-2:-2]:
        release3.classifiers.append(c)
    session.add(release3)
    release3.files.append(ReleaseFile(filename=u'mirrored_package2-1.0.tar.gz',
                                      package_type=u'sdist'))
    session.add(release3)

    pack3 = Package(name=u'local_package1', local=True)
    pack3.owners.append(local_user)
    session.add(pack3)

    release4 = Release(package=pack3, version=u'0.1',
                       summary='Pet Shop Application')
    for c in classifiers:
        release4.classifiers.append(c)
    release4.files.append(ReleaseFile(filename=u'local_package1-0.1.tar.gz',
                                      package_type=u'sdist'))
    session.add(release4)

    session.commit()


def tearDown():
    dispose_engine()
