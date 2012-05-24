import sys
import os
import subprocess
from os import path
import signal

from test.scriptSessionTest import ScriptSessionTest
from test.utils import raises

def setup_module(module):
    rootdir = path.join(os.path.dirname(__file__), 'root')
    module.daemon = subprocess.Popen([sys.executable, path.join(rootdir, '..', 'daemonTest.py')])


def teardown_module(module):
    print 'Killing daemon server...'
    os.kill(module.daemon.pid, signal.SIGTERM)
    os.waitpid(module.daemon.pid, 0)
    print '-' * 70

def testSimple():
    code = 'print "Test"'
    setup = 'startup'
    session = ScriptSessionTest('TestScriptSession')
    session.run(setup, code)

def testRaiseSimple():
    code = 'raise Exception("testing")'
    setup = 'startup'
    session = ScriptSessionTest('TestScriptSession')
    assert raises(Exception, session.run, setup, code)
