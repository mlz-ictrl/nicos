from nicos import session
from test.utils import raises
from nicos.errors import NicosError, LimitError, ConfigurationError

def setup_module():
    session.loadSetup('system')
    session.setMode('master')

def teardown_module():
    session.unloadSetup()


def test_tas():
    tas = session.getDevice('Tas')
