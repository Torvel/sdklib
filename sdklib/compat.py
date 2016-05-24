import sys


_ver = sys.version_info

#: Python 2.x?
is_py2 = (_ver[0] == 2)

#: Python 3.x?
is_py3 = (_ver[0] == 3)

if is_py2:
    import Cookie as cookies
    from urllib import urlencode, quote_plus

    basestring = basestring
elif is_py3:
    from urllib.parse import urlencode, quote_plus
    from http import cookies

    basestring = (str, bytes)

