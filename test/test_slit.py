from nicos import session
from test.utils import raises
from nicos.errors import NicosError, LimitError, ConfigurationError

def setup_module():
    session.loadSetup('slit')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()

def test_slit():
    slit = session.getDevice('slit_1')
    motor_right = session.getDevice('motor_right')
    motor_left = session.getDevice('motor_left')
    motor_bottom = session.getDevice('motor_bottom')
    motor_top = session.getDevice('motor_top')

    slit.opmode = '4blades'
    slit.doStart((1, 2, 3, 4))
    slit.doWait()
    assert motor_right.doRead() == 1
    assert motor_left.doRead() == 2
    assert motor_bottom.doRead() == 3
    assert motor_top.doRead() == 4
    assert slit.doRead() == (motor_right.doRead(),
                             motor_left.doRead(),
                             motor_bottom.doRead(),
                             motor_top.doRead())

    slit.doStart((8, 7, 6, 5))
    slit.doWait()
    assert slit.doRead() == (8, 7, 6, 5)

    assert raises(LimitError, slit.doStart, (8000, 7, 6, 5))


    slit.doStart((8, 4, 3, 5))
    slit.doWait()
    assert slit.doRead() == (8, 4, 3, 5)

    slit.opmode = 'centered'
    assert slit.doRead() == (-4, 2)

    slit.opmode = 'offcentered'
    assert slit.doRead() == (6, 4, -4, 2)

    slit.doStart((4, 2, 3, 5))
    slit.doWait()
    assert slit.doRead() == (4, 2, 3, 5)
    slit.opmode = '4blades'
    assert slit.doRead() == (2.5, 5.5, -0.5, 4.5)

