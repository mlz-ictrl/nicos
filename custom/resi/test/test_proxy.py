#

from __future__ import print_function

from nicos.pycompat import cPickle as pickle

from test.utils import SkipTest

try:
    from nicos.resi import residevice
except ImportError:
    # running without resi specific Nonius libs
    raise SkipTest


def test_pickable():
    store = {'phi': 3.1415926535897931, 'type': 'e', 'dx': 400, 'chi': 0.0,
             'theta':-0.17453292519943295, 'omega': 0.0}
    hw = None
    pos = residevice.position.PositionFromStorage(hw, store)
    proxied = residevice.ResiPositionProxy(pos)
    res = pickle.dumps(proxied, protocol=0)
    restored = pickle.loads(res)
    print(store)
    print(restored.storable())
    assert restored.storable() == store
