from nicos import session
from test.utils import raises
from nicos.errors import NicosError, LimitError, ConfigurationError

def setup_module():
    session.loadSetup('switcher')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()

def test_switcher():
    switcher = session.getDevice('switcher_1')
    motor = session.getDevice('motor_1')

    switcher.doStart('10')
    motor.doWait()
    assert motor.doRead() == 10

    switcher.doStart('30')
    motor.doWait()
    assert motor.doRead() == 30

    switcher.doStart('0')
    motor.doWait()
    assert motor.doRead() == 0

    assert raises(NicosError, switcher.doStart, '#####')

    assert raises(LimitError, switcher.doStart, '1000')
    assert raises(LimitError, switcher.doStart, '-10')

    assert raises(ConfigurationError, session.getDevice, 'broken_switcher')
