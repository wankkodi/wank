try:
    import html5lib
except ImportError:
    import Modules.html5lib as html5lib

# Internet tools
import sys
if sys.version_info >= (3, 0):
    from urllib.parse import urljoin, urlparse, parse_qs, parse_qsl, unquote, unquote_plus, quote, quote_plus, \
        urlencode
else:
    from urlparse import urljoin, urlparse, parse_qs, parse_qsl
    from urllib import unquote, unquote_plus, quote, quote_plus, urlencode

# Enum
if sys.version_info >= (3, 4):
    from enum import Enum
else:
    from Modules.enum34 import Enum
