#!/usr/bin/env python

import sys

for pyver in ['2.4', '2.5', '2.6']:
    sys.path.append('/opt/taco/lib/python%s/site-packages' % pyver)

from nicm.interface.interactive import start

# allow giving an initial setup name
if len(sys.argv) > 1:
    start(sys.argv[1])
else:
    start()
