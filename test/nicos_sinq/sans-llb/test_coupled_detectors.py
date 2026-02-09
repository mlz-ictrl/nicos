import pytest

from nicos.core import status

session_setup = 'sinq_sansllb'

class TestCoupledDetectors:
    detz = None
    dtlz = None
    dtlx = None
    dthz = None
    dthx = None
    dthy = None

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        """
        Initialize the devices if they are not already initialized
        """
        if not self.dtlz:
            self.dtlz = session.getDevice('dtlz')
        if not self.dtlx:
            self.dtlx = session.getDevice('dtlx')
        if not self.dthz:
            self.dthz = session.getDevice('dthz')
        if not self.dthx:
            self.dthx = session.getDevice('dthx')
        if not self.dthy:
            self.dthy = session.getDevice('dthy')
        if not self.detz:
            self.detz = session.getDevice('detz')

    def test_status(self):
        """Test that moving one of the individual axes changes status of coupled device."""
        self.detz.move(4000)
        assert self.detz.status()[0]==status.OK
        self.dthz.move(3000)
        assert self.detz.status()[0]==status.NOTREACHED

    def test_ratio_z(self):
        """Test that movement along the beam is following the given ratio value"""
        for ratio in [1.2, 1.5, 1.8, 2.0, 2.5, 3.0]:
            self.detz.low_high_ratio=ratio
            for dest in [5000., 8000., 12000., 18000.]:
                self.detz.move(dest)
                assert self.dtlz()==dest
                assert self.dthz()==min(max(dest/ratio, self.dthz.abslimits[0]), self.dthz.abslimits[1])

    def test_ratio_xmove(self):
        """Test that horizontal movement of high angle detector corresponds to ratio of low angle movement"""
        self.detz.low_high_ratio=2.0
        self.dthx(0.)
        self.detz(10000.)
        xstart = self.dthx()
        assert xstart==(self.detz.low_angle_frame_x/2.0-self.detz.high_angle_opening_x)
        self.dtlx(-50.)
        self.detz(10000.)
        assert self.dthx()==xstart+50./2.

    def test_ratio_y(self):
        """Test that horizontal movement of high angle detector corresponds to ratio of low angle movement"""
        self.detz.low_high_ratio=2.0
        self.detz(10000.)
        assert self.dthy()==(-self.detz.low_angle_frame_y/2.0+self.detz.high_angle_opening_y)
