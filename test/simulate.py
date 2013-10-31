#!/usr/bin/env python

# This is copied to test/root/bin/nicos-simulate when the tests run.
# It is adapted from bin/nicos-simulate to run correctly in the test
# environment.

import sys
import signal
from os import path

# allow importing the "test" package; lib/ is already in PYTHONPATH
sys.path.insert(0, path.join(path.dirname(__file__), '..', '..', '..'))

from test.utils import rootdir

args = sys.argv[1:]
if len(args) != 4:
    raise SystemExit('Usage: nicos-simulate port prefix setups code')
port = int(args[0])
prefix = args[1]
setups = args[2].split(',')
code = args[3]

# kill forcibly after 10 seconds
signal.alarm(10)

from nicos.core.sessions.simple import SimulationSession
SimulationSession.config.control_path = rootdir
SimulationSession.config.setups_path = path.join(rootdir, '..', 'setups')

SimulationSession.run(port, prefix, setups, code)
