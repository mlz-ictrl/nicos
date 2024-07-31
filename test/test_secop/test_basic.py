import pytest

pytest.importorskip('frappy')

session_setup = 'empty'


def test_autoscan(secnode, session):
    session.loadSetup('secop_autoscan')
    sn = session.getDevice('secnode')
    session.getDevice('enumvalue')
    sn.doShutdown()


def test_static_device(secnode, session):
    session.loadSetup('secop_manual')
    session.getDevice('enumvalue')
    sn = session.getDevice('secnode')
    sn.doShutdown()
