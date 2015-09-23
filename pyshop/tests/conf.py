
settings = {'jinja2.directories': 'pyshop:templates',
            'pyshop.cookie_key': 'sicr3t',
            'sqlalchemy.url': 'sqlite://',
            'sqlalchemy.echo': False,
            'sqlalchemy.pool_size': 1,
            'pyshop.enable_xmlrpc': False,
            'pyshop.upload.sanitize': False,
            'pyshop.upload.sanitize.regex':
                r'^(?P<version>\d+\.\d+)(?P<extraversion>(?:\.\d+)*)'
                '(?:(?P<prerel>[abc]|rc)(?P<prerelversion>\d+'
                '(?:\.\d+)*))?(?P<postdev>(\.post(?P<post>\d+))?'
                '(\.dev(?P<dev>\d+))?)?$',
            'pyshop.mirror.sanitize': False,
            'pyshop.pypi.url': 'http://localhost:65432',
            'pyshop.repository': '/tmp',
            }
