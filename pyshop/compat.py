import sys


if sys.version < '3':

     unicode = __builtins__['unicode']
     bytes = str
     from cStringIO import StringIO

else:
     unicode = str
     bytes = __builtins__['bytes']

     from io import StringIO


def to_unicode(text):
    if isinstance(text, bytes):
        return text.decode('utf-8')
    return text
