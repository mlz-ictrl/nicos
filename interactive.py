#!/usr/bin/env python

import sys

from nicm.interface.interactive import start

# allow giving an initial setup name
if len(sys.argv) > 1:
    start(sys.argv[1])
else:
    start()
