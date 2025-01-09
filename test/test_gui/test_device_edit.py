# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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

"""NICOS test lib: Test device and device parameter edit widgets."""

import pytest

from nicos.guisupport.qt import QWidget
from nicos.guisupport.typedvalue import DeviceParamEdit, DeviceValueEdit

pytest.importorskip('pytestqt')


session_setup = 'guitest'


def load_setup(client, setup):
    client.run_and_wait("NewSetup('%s')" % setup)


class TestDeviceEdit:

    @pytest.mark.parametrize(
        'value,result,kwargs',
        [
            (1, 1, dict(dev='gax', updateValue=True)),
            (1, 0, dict(dev='gax', initDefault=True)),
            (None, 0, dict(dev='gax', initDefault=True)),
            (None, 0, dict(dev='gax')),
            (1, '', dict(dev='', updateValue=True, initDefault=True)),
            ])
    def test_DeviceValueEdit(self, guiclient, qtbot, qapp, session,
                             value, result, kwargs):
        load_setup(guiclient, 'guitest')
        if device := kwargs.get('dev'):
            dev = session.getDevice(device)
            dev._setROParam('target', None)
        widget = QWidget()
        dve = DeviceValueEdit(widget, **kwargs)
        dve.setClient(guiclient)
        dve.registerKeys()

        qtbot.addWidget(widget)
        widget.show()
        dve.setValue(value)
        dve.setFocus()

        with qtbot.waitExposed(widget):
            pass

        assert dve.getValue() == result

    @pytest.mark.parametrize(
        'value,result,kwargs',
        [
            ('1', '', dict(dev='', param='precision', updateValue=True)),
            ('1', 1, dict(dev='gax', param='precision', updateValue=True)),
            ('1', '1', dict(dev='gax', param='blah', updateValue=True)),
         ])
    def test_DeviceParamEdit(self, guiclient, qtbot, qapp, session,
                             value, result, kwargs):
        load_setup(guiclient, 'guitest')
        widget = QWidget()
        dpe = DeviceParamEdit(widget, **kwargs)
        dpe.setClient(guiclient)
        dpe.registerKeys()

        qtbot.addWidget(widget)
        widget.show()
        dpe.setValue(value)
        dpe.setFocus()

        with qtbot.waitExposed(widget):
            pass

        assert dpe.getValue() == result
