from nicos.devices.sxtal.xtal.symmetry import _test as symtest
from nicos.devices.sxtal.xtal.sxtalcell import _test as sxtaltest

def test_symmetry():
    for t in symtest():
        yield t

def test_cell():
    sxtaltest()

