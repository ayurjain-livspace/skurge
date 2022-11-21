from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import site

from .conf import rel

site.addpackage(rel(), "apps.pth", known_paths=set())

# Stop Requests module printing unnecessary info while connecting to any URL
logging.getLogger("requests").setLevel(logging.WARNING)
