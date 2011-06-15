from nicos import session
from test.utils import raises
from nicos.errors import NicosError, LimitError, ConfigurationError

tas = None

def setup_module():
    global tas

    session.loadSetup('system')
    session.setMode('master')
    tas = session.getDevice('Tas')

def teardown_module():
    session.unloadSetup()


def test_tas():
    pass
