import sys


if sys.version < '3':

     unicode = __builtins__['unicode']
     from cStringIO import StringIO

else:
     unicode = str
     from io import StringIO
