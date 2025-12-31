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

"""NICOS test lib: Test cmdlets."""

import pytest

from nicos.clients.gui.cmdlets import Center, Configure, ContScan, Count, \
    CScan, Move, NewSample, Scan, Sleep, TimeScan, WaitFor
from nicos.clients.gui.cmdlets.qscan import QScan
from nicos.clients.gui.cmdlets.tomo import Tomo
from nicos.guisupport.colors import colors
from nicos.guisupport.qt import Qt

pytest.importorskip('pytestqt')


session_setup = 'guitest'


def load_setup(client, setup):
    client.run_and_wait("NewSetup('%s')" % setup)


class CmdletTester:

    cls = None

    @pytest.fixture
    def widget(self, guiclient, qtbot, qapp, session):
        colors.init_palette(qapp.palette())
        load_setup(guiclient, 'guitest')
        widget = self.cls(None, guiclient, {})  # pylint: disable=not-callable

        qtbot.addWidget(widget)
        widget.show()

        with qtbot.waitExposed(widget):
            pass

        return widget


class TestCenter(CmdletTester):

    cls = Center

    def test_inited(self, widget):
        assert not widget.isValid()
        assert widget.getValues() == {
            'dev': 'gax',
            'preset': 0.0,
            'presetunit': 'seconds',
            'scancont': False,
            'scanpoints': 10,
            'scanstart': '',
            'scanstep': '',
        }
        assert widget.generate() == 'center(gax, , , 10, t=0.0)'

    def test_set_values(self, widget):
        widget.setValues({
            'dev': 'gax',
            'preset': 1.0,
            'presetunit': 'seconds',
            'scancont': False,
            'scanpoints': 10,
            'scanstart': '0',
            'scanstep': '0.1',
        })
        assert widget.isValid()
        assert widget.generate() == 'center(gax, 0, 0.1, 10, t=1.0)'

        widget.setValues({
            'scancont': True,
            'scanpoints': 2,
        })
        assert widget.isValid()
        assert widget.generate() == 'contscan(gax, -0.2, 0.2, 0.08, 1.0)'


class TestConfigure(CmdletTester):

    cls = Configure

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'dev': 'gax',
            'param': 'backlash',
            'paramvalue': 0.0,
        }
        assert widget.generate() == "set(gax, 'backlash', 0.0)"

    def test_set_values(self, widget):
        widget.setValues({
            'dev': 'gax',
            'param': 'precision',
            'paramvalue': 10.01,
        })
        assert widget.isValid()
        # TODO: The set values aren't not transferred correctly into the widget
        # elements !!! This has to be investigated
        assert widget.getValues() != {
            'dev': 'gax',
            'param': 'precision',
            'paramvalue': 0.01
        }
        assert widget.generate() != "set(gax, 'precision', 0.01)"


class TestContScan(CmdletTester):

    cls = ContScan

    def test_inited(self, widget):
        assert not widget.isValid()
        assert widget.getValues() == {
            'dev': 'gax',
            'scanstart': '',
            'scanend': '',
            'devspeed': '1',
            'preset': 1.0,
        }
        assert widget.generate() == 'contscan(gax, , , 1, 1.0)'

    def test_set_values(self, widget):
        widget.setValues({
            'dev': 'gax',
            'scanstart': '0',
            'scanend': '10',
            'devspeed': '0.1',
            'preset': 1.0,
        })
        assert widget.isValid()
        assert widget.generate() == 'contscan(gax, 0, 10, 0.1, 1.0)'


class TestCount(CmdletTester):

    cls = Count

    def test_inited(self, widget):
        assert not widget.isValid()
        assert widget.getValues() == {'preset': 0.0, 'presetunit': 'seconds'}
        assert widget.generate() == 'count(t=0.0)'

    def test_set_values(self, widget):
        widget.setValues({
            'preset': 1,
            'presetunit': 'minutes'
        })
        assert widget.isValid()
        assert widget.generate() == 'count(t=60.0)'


class TestCScan(CmdletTester):

    cls = CScan

    def test_inited(self, widget):
        assert not widget.isValid()
        assert widget.getValues() == {
           'dev': 'gax',
           'scanstart': '',
           'scanstep': '',
           'scanpoints': 10,
           'scancont': False,
           'preset': 0.0,
           'presetunit': 'seconds',
        }
        assert widget.generate() == 'cscan(gax, , , 10, t=0.0)'

    def test_set_values(self, widget):
        widget.setValues({
           'dev': 'gax',
           'scanstart': '0',
           'scanstep': '0.1',
           'scanpoints': 10,
           'scancont': False,
           'preset': 1.0,
           'presetunit': 'seconds',
        })
        assert widget.isValid()
        assert widget.generate() == 'cscan(gax, 0, 0.1, 10, t=1.0)'

        widget.setValues({'scancont': True, 'scanpoints': 2})
        assert widget.generate() == 'contscan(gax, -0.2, 0.2, 0.08, 1.0)'


class TestMove(CmdletTester):

    cls = Move

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.generate() == 'maw(gax, 0.0)'
        assert widget.getValues() == {'dev': 'gax', 'moveto': 0.0}

    def test_maw(self, widget):
        widget.waitBox.setCheckState(Qt.Unchecked)
        assert widget.generate() == 'move(gax, 0.0)'

    def test_change_dev(self, widget):
        widget.multiList.entry(0).device.setCurrentText('gm1')
        assert widget.isValid()
        assert widget.generate() == 'maw(gm1, 0.0)'

    def test_change_target(self, widget):
        widget.multiList.entry(0).target.setValue(10)
        assert widget.isValid()
        assert widget.generate() == 'maw(gax, 10.0)'

    def test_set_values(self, widget):
        widget.setValues({'dev': 'gax', 'moveto': 2})
        assert widget.isValid()
        assert widget.generate() == 'maw(gax, 2.0)'


class TestNewSample(CmdletTester):

    cls = NewSample

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {'samplename': ''}
        assert widget.generate() == "NewSample('')"

    def test_set_values(self, widget):
        widget.setValues({'samplename': 'Gd3CdB7'})
        assert widget.isValid()
        assert widget.generate() == "NewSample('Gd3CdB7')"


class TestQScan(CmdletTester):

    cls = QScan

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'scanpoints': 10,
            'preset': 1.0,
            'presetunit': 'seconds',
        }
        assert widget.generate() == \
            'qscan((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), 10, t=1.0)'

    def test_set_values(self, widget):
        widget.centerBox.setChecked(True)
        assert widget.isValid()
        assert widget.generate() == \
            'qcscan((0.0, 0.0, 0.0, 0.0), (0.0, 0.0, 0.0, 0.0), 10, t=1.0)'
        widget.centerBox.setChecked(False)
        assert widget.isValid()


class TestScan(CmdletTester):

    cls = Scan

    def test_inited(self, widget):
        assert widget.getValues() == {'dev': 'gax',
                                      'scanstart': '',
                                      'scanstep': '',
                                      'scanpoints': 10,
                                      'scancont': False,
                                      'preset': 0.0,
                                      'presetunit': 'seconds',
                                      }
        assert not widget.isValid()
        assert widget.generate() == 'scan(gax, , , 10, t=0.0)'

    def test_set_values(self, widget):
        widget.setValues({
            'dev': 'gax',
            'scanstart': '0',
            'scanstep': '0.1',
            'scanpoints': 10,
            'scancont': False,
            'preset': 1.0,
            'presetunit': 'seconds',
            })
        assert widget.isValid()
        assert widget.generate() == 'scan(gax, 0, 0.1, 10, t=1.0)'

    def test_continue_scan(self, widget):
        widget.setValues({
            'dev': 'gax',
            'scanstart': '0',
            'scanstep': '0.1',
            'scanpoints': 10,
            'scancont': True,
            'preset': 1.0,
            'presetunit': 'seconds',
            })
        assert widget.isValid()
        assert widget.generate() == 'contscan(gax, 0.0, 0.9, 0.09, 1.0)'


class TestSleep(CmdletTester):

    cls = Sleep

    def test_inited(self, widget):
        assert not widget.isValid()
        assert widget.getValues() == {'sleeptime': 0.0}
        assert widget.generate() == 'sleep(0.0)'

    def test_set_values(self, widget):
        widget.setValues({'sleeptime': 60})
        assert widget.generate() == 'sleep(60.0)'


class TestTimeScan(CmdletTester):

    cls = TimeScan

    def test_inited(self, widget):
        assert not widget.isValid()
        assert widget.getValues() == {
            'scanpoints': 10,
            'countinf': False,
            'preset': 0.0,
            'presetunit': 'seconds'
        }
        assert widget.generate() == 'timescan(10, t=0.0)'

    def test_set_values(self, widget):
        widget.setValues({
            'preset': 1,
            'presetunit': 'minutes',
            'countinf': False,
            'scanpoints': 11,
        })
        assert widget.generate() == 'timescan(11, t=60.0)'

        widget.setValues({'countinf': True})
        assert widget.generate() == 'timescan(-1, t=60.0)'


class TestTomo(CmdletTester):

    cls = Tomo

    def test_inited(self, widget):
        assert not widget.isValid()
        assert widget.getValues() == {
            'dev': '',
            'nangles': 360,
            'imgsperangle': 1,
            'preset': 1.0,
            'presetunit': 'seconds',
            'reffirst': True,
            'detlist': '',
            'start': 0.0,
        }
        assert widget.generate() == \
            'tomo(360, None, imgsperangle=1, ref_first=True, startpoint=0.0, t=1.0)'

    def test_set_values(self, widget):
        # widget.setValues({
        #     'dev': 'gax',
        #     'detlist': 'cam',
        # })
        widget.device.setCurrentText('gax')
        assert widget.isValid()
        assert widget.generate() == \
            'tomo(360, gax, imgsperangle=1, ref_first=True, startpoint=0.0, t=1.0)'

        widget.refFirst.click()
        assert widget.isValid()
        assert widget.generate() == \
            'tomo(360, gax, imgsperangle=1, ref_first=False, startpoint=0.0, t=1.0)'
        widget.refFirst.click()
        assert widget.generate() == \
            'tomo(360, gax, imgsperangle=1, ref_first=True, startpoint=0.0, t=1.0)'

        assert not widget.contBox.isChecked()
        widget.contBox.click()
        assert widget.contBox.isChecked()
        assert widget.isValid()
        assert widget.generate() == \
            'tomo(360, gax, imgsperangle=1, ref_first=False, startpoint=0.0, t=1.0)'

        widget.start.setValue(10)
        assert widget.start.value() == 10
        assert widget.isValid()
        assert widget.generate() == \
            'tomo(360, gax, imgsperangle=1, ref_first=False, startpoint=10.0, t=1.0)'

        widget.detectors.clear()
        widget.detectors.addItems(['cam'])
        assert widget.isValid()
        assert widget.generate() == 'tomo(360, gax, 1, False, 10.0, cam, t=1.0)'
        widget.contBox.click()
        assert not widget.contBox.isChecked()


class TestWaitFor(CmdletTester):

    cls = WaitFor

    def test_inited(self, widget):
        assert widget.isValid()
        assert widget.getValues() == {
            'dev': 'gax',
            'usecond': True,
            'timeout': 1.0,
            'timeoutunit': 'hours',
            'condop': '==',
            'condtarget': 0.0,
            'stabletarget': 0.0,
            'stableacc': 0.0,
            'stabletime': 30.0,
            'stabletimeunit': 'seconds',
        }
        assert widget.generate() == \
            'waitfor(\'gax\', "== 0.0", timeout=3600.0)'

    def test_set_values(self, widget):
        widget.setValues({
            'dev': 'gax',
            'usecond': True,
            'timeout': 1.0,
            'timeoutunit': 'hours',
            'condop': '<=',
            'condtarget': 0.0,
            'stabletarget': 0.0,
            'stableacc': 0.0,
            'stabletime': 30.0,
            'stabletimeunit': 'seconds',
        })
        assert widget.isValid()
        assert widget.generate() == \
            'waitfor(\'gax\', "<= 0.0", timeout=3600.0)'

        widget.setValues({'usecond': False})
        assert widget.isValid()
        assert widget.generate() == \
            "waitfor_stable('gax', 0.0, 0.0, time_stable=30.0, timeout=3600.0)"
