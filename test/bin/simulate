#!/usr/bin/env python

# This is copied to NICOS_TEST_ROOT/bin/nicos-simulate when the tests run.
# It is adapted from bin/nicos-simulate to run correctly in the test
# environment.

import sys
import signal
from os import path

# allow importing the "test" package; lib/ is already in PYTHONPATH
sys.path.insert(0, path.join(path.dirname(__file__), '..', '..', '..'))

from test.utils import runtime_root, selfDestructAfter

args = sys.argv[1:]
if len(args) != 5:
    raise SystemExit('Usage: nicos-simulate port prefix setups user code')
port = int(args[0])
prefix = args[1]
setups = args[2].split(',')
user = args[3]
code = args[4]

# kill forcibly after 10 seconds
if hasattr(signal, 'alarm'):
    signal.alarm(10)

from nicos import config
from nicos.core.sessions.simulation import SimulationSession
config.nicos_root = runtime_root
config.setup_subdirs = '../test'

selfDestructAfter(120)
SimulationSession.run(port, prefix, setups, user, code)
