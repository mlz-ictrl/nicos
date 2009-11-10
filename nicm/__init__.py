# -*- coding: utf-8 -*-
"""
    nicm package
    ~~~~~~~~~~~~

    The nicm package contains all standard NICOS commands and devices.
"""

__version__ = '2.0a1'

import sys

# Check for Python version 2.5+.
if sys.version_info[:2] < (2, 5):
    raise ImportError('NICOS requires Python 2.5 or higher')

# Create the NICOS class singleton.
from nicm.nicos import NICOS
nicos = NICOS()

# NICOS user commands and devices will be placed in the globals of the
# execution frame that first imports this package.
nicos.set_namespace(sys._getframe(1).f_globals)

# Create the initial instrument setup.
nicos.log.info('--- loading startup setup')
nicos.load_setup('startup')
nicos.log.info('--- done')

# Fire up an interactive console (XXX this call needs to be done from outside).
nicos.console()
