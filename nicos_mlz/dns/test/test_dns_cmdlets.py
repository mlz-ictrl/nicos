# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2026 by the NICOS contributors (see AUTHORS)
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Module authors:
#   Jens Krüger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""DNS tests: Test cmdlets."""

from nicos.guisupport.qt import Qt

from nicos_mlz.dns.gui.cmdlets import PowderScan, SetTemperature, Shutter, \
    SingleCrystalScan, SlitScan

from test.test_gui.test_cmdlets import CmdletTester

session_setup = ''


class TestPowderScan(CmdletTester):

    cls = PowderScan

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'off': False,
            'zero_sf': False,
            'zero_nsf': False,
            'x_sf': False,
            'x_nsf': False,
            'y_sf': False,
            'y_nsf': False,
            'z_sf': False,
            'z_nsf': False,
            'time': True,
            'monitor': False,
            'min_per_mon': False,
            'bankpositions': 1,
            'lowest_2theta': -5.0,
            'omega_start': 100.0,
            'MonpMin': 80000,
            'SF': 1.0,
            'NSF': 1.0,
            'norm': 't',
            'open_before': True,
            'close_after': False,
        }
        assert widget.generate() == \
"""maw(expshutter, 'open')
scan([det_rot, sample_rot], [-5.0, 100.0], [0, 0], 1, t=1.0)"""

    def test_set_values(self, widget):
        assert not widget.close_after.isChecked()
        widget.close_after.setChecked(True)
        assert widget.close_after.isChecked()
        assert widget.generate() == \
"""maw(expshutter, 'open')
scan([det_rot, sample_rot], [-5.0, 100.0], [0, 0], 1, t=1.0)
maw(expshutter, 'closed')"""

        assert widget.RB_time.isChecked()
        widget.RB_monitor.setChecked(True)
        assert widget.RB_monitor.isChecked()
        assert widget.generate() == \
"""maw(expshutter, 'open')
scan([det_rot, sample_rot], [-5.0, 100.0], [0, 0], 1, mon1=1.0)
maw(expshutter, 'closed')"""

        widget.RB_min_per_mon.setChecked(True)
        assert widget.RB_min_per_mon.isChecked()
        assert widget.generate() == \
"""maw(expshutter, 'open')
mpm=80000
scan([det_rot, sample_rot], [-5.0, 100.0], [0, 0], 1, mon1=1.0*mpm)
maw(expshutter, 'closed')"""

        widget.lowest_2theta.setValue(-20)
        assert widget.generate() == \
"""maw(expshutter, 'open')
mpm=80000
scan([det_rot, sample_rot], [-20.0, 100.0], [0, 0], 1, mon1=1.0*mpm)
maw(expshutter, 'closed')"""

        widget.XSF.setChecked(Qt.Checked)
        assert widget.isValid()
        assert widget.generate() == \
"""maw(expshutter, 'open')
mpm=80000
scan([det_rot, sample_rot], [-20.0, 100.0], [0, 0], 1, field=['x20_sf'], mon1=1.0*mpm)
maw(expshutter, 'closed')"""

        widget.off.setChecked(Qt.Checked)
        assert widget.isValid()

        widget.deselect.click()
        assert widget.isValid()

        widget.RB_min_per_mon.setChecked(Qt.Checked)
        assert widget.isValid()

        widget.XYZ.click()
        assert widget.isValid()

        widget.bankpositions.setValue(2)
        assert widget.bankpositions.value() == 2
        assert not widget.isValid()


class TestSetTemperature(CmdletTester):

    cls = SetTemperature

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'temperature': 300.0,
            'command': 'maw',
        }
        assert widget.generate() == 'maw(T, 300.0)'

    def test_set_values(self, widget):
        assert widget.waitfor.isChecked()
        widget.waitfor.toggle()
        assert not widget.waitfor.isChecked()
        assert widget.generate() == 'move(T, 300.0)'


class TestShutter(CmdletTester):

    cls = Shutter

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'shutter': 'open',
        }
        assert widget.generate() == "maw(expshutter, 'open')"

    def test_set_values(self, widget):
        widget.shutter.setCurrentText('closed')
        assert widget.isValid()
        assert widget.generate() == "maw(expshutter, 'closed')"


class TestSingleCrystalScan(CmdletTester):

    cls = SingleCrystalScan

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'off': False,
            'zero_sf': False,
            'zero_nsf': False,
            'x_sf': False,
            'x_nsf': False,
            'y_sf': False,
            'y_nsf': False,
            'z_sf': False,
            'z_nsf': False,
            'time': True,
            'monitor': False,
            'min_per_mon': False,
            'bankpositions': 1,
            'lowest_2theta': -5.0,
            'omega_start': 100.0,
            'MonpMin': 80000,
            'SF': 1.0,
            'NSF': 1.0,
            'norm': 't',
            'open_before': True,
            'close_after': False,
            'omega_step': 1.0,
            'omega_nos': 10,
        }
        assert widget.generate() == \
"""maw(expshutter, 'open')
scan([det_rot, sample_rot], [  -5.000,  100.000], [0, 1.0], 10, t=1.0)"""

    def test_set_values(self, widget):
        widget.close_after.setChecked(True)
        assert widget.isValid()
        assert widget.generate() == \
"""maw(expshutter, 'open')
scan([det_rot, sample_rot], [  -5.000,  100.000], [0, 1.0], 10, t=1.0)
maw(expshutter, 'closed')"""
        widget.close_after.setChecked(False)
        assert widget.isValid()
        assert widget.generate() == \
"""maw(expshutter, 'open')
scan([det_rot, sample_rot], [  -5.000,  100.000], [0, 1.0], 10, t=1.0)"""

        widget.open_before.setChecked(False)
        assert widget.isValid()
        assert widget.generate() == \
           'scan([det_rot, sample_rot], [  -5.000,  100.000], [0, 1.0], 10, t=1.0)'


class TestSlitScan(CmdletTester):

    cls = SlitScan

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'y_lower': True,
            'y_lower_from': -30.0,
            'y_lower_stepsize': 2.0,
            'y_lower_number_of_steps': 20,
            'y_upper': True,
            'y_upper_from': 30.0,
            'y_upper_stepsize': -2.0,
            'y_upper_number_of_steps': 20,
            'x_left': True,
            'x_left_from': -15.0,
            'x_left_stepsize': 2.0,
            'x_left_number_of_steps': 10,
            'x_right': True,
            'x_right_from': 15.0,
            'x_right_stepsize': -2.0,
            'x_right_number_of_steps': 10,
            'time': 5.0,
            'slittype': 'ap_sam',
            'open_begin': True,
        }
        assert widget.generate() == \
"""maw(expshutter, 'open')
maw(sample_slit, (0.0, 0.0, 30, 60))
scan(ap_sam_y_lower, -30, 2, 20, 5)
maw(ap_sam_y_lower, -30)\nscan(ap_sam_y_upper, 30, -2, 20, 5)
maw(ap_sam_y_upper, 30)
scan(ap_sam_x_left, -15, 2, 10, 5)
maw(ap_sam_x_left, -15)
scan(ap_sam_x_right, 15, -2, 10, 5)
maw(ap_sam_x_right, 15)"""

    def test_set_values(self, widget):
        assert widget.RB_sample.isChecked()
        widget.RB_polarizer.click()
        assert not widget.RB_sample.isChecked()
        assert widget.generate() == \
"""maw(expshutter, 'open')
maw(pol_slit, (0.0, 0.0, 120, 120))
scan(pol_y_lower, -60, 3, 25, 5)
maw(pol_y_lower, -60)
scan(pol_y_upper, 60, -3, 25, 5)
maw(pol_y_upper, 60)
scan(pol_x_left, -60, 3, 25, 5)
maw(pol_x_left, -60)
scan(pol_x_right, 60, -3, 25, 5)
maw(pol_x_right, 60)"""
