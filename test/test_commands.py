from nicos import session
from nicos.commands import scan, measure

motor = None

def setup_module():
    global motor
    session.loadSetup('axis')
    session.setMode('master')
    motor = session.getDevice('motor')

def teardown_module():
    session.unloadSetup()


def test_scan():
    scan(motor, [0, 1, 2, 10])

def test_measure():
    pass
