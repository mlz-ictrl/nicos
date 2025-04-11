#!/bin/python

import os

from nicos import config


# We're building the installer always with Qt 6.
os.environ['NICOS_QT'] = '6'

# this is needed since pathlib.Path.glob cannot recurse symlinked folders
# until python3.13, relevant to InstrSelectDialog.__init__
config.nicos_root = os.path.join(os.path.dirname(config.nicos_root), 'Resources')
