from nicos import session
from test.utils import raises
from nicos.errors import NicosError, LimitError

switcher = None
motor = None

def setup_module():
    global switcher, motor
    session.loadSetup('switcher')
    session.setMode('master')
    switcher = session.getDevice('switch')
    motor = session.getDevice('motor_1')

def teardown_module():
    session.unloadSetup()


def test_switcher():
    switcher.doStart('10')
    motor.doWait()
    assert motor.doRead()==10

    switcher.doStart('30')
    motor.doWait()
    assert motor.doRead()==30

    switcher.doStart('0')
    motor.doWait()
    assert motor.doRead()==0

    assert raises(NicosError, switcher.doStart, '#####')

    assert raises(LimitError, switcher.doStart, '1000')
