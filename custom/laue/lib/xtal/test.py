

#  pylint: disable=relative-import
from symmetry import _test as symtest
from sxtalcell import _test as sxtaltest

def test_symmetry():
    symtest()

def test_cell():
    sxtaltest()

