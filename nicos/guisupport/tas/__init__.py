#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2021 by the NICOS contributors (see AUTHORS)
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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""TAS specific display widgets."""

from nicos.guisupport.qt import QSize
from nicos.guisupport.tas.widgets import TasView
from nicos.guisupport.widget import NicosWidget, PropDef


class TasWidget(NicosWidget, TasView):
    """Display of the TAS table configuration."""

    designer_description = __doc__

    mthdev = PropDef('mthdev', str, '', 'Monochromator rocking angle device')
    mttdev = PropDef('mttdev', str, '', 'Monochromator scattering angle device')
    sthdev = PropDef('sthdev', str, '', 'Sample rotation device')
    sttdev = PropDef('sttdev', str, '', 'Sample scattering angle device')
    athdev = PropDef('athdev', str, '', 'Analyzer rocking angle device')
    attdev = PropDef('attdev', str, '', 'Analyzer scattering angle device')
    Lmsdev = PropDef('Lmsdev', str, '', 'Distance monochromator->sample device')
    Lsadev = PropDef('Lsadev', str, '', 'Distance sample->analyzer device')
    Laddev = PropDef('Laddev', str, '', 'Distance analyzer->detector device')
    height = PropDef('height', int, 30, 'Widget height in characters')
    width = PropDef('width', int, 40, 'Widget width in characters')

    def __init__(self, parent, designMode=False):

        self._keymap = {}
        self._statuskeymap = {}
        self._targetkeymap = {}

        TasView.__init__(self, parent, designMode)
        NicosWidget.__init__(self)

    def initUi(self):
        TasView.initUi(self)

    def registerKeys(self):
        for dev in self.values:
            devname = str(self.props[dev + 'dev'])
            if devname:
                self._keymap[
                    self._source.register(self, devname + '/value')] = dev
                self._statuskeymap[
                    self._source.register(self, devname + '/status')] = dev
                self._targetkeymap[
                    self._source.register(self, devname + '/target')] = dev

    def on_keyChange(self, key, value, time, expired):
        if not expired:
            if key in self._keymap:
                # Scale the distances
                if self._keymap[key] in ('Lms', 'Lsa', 'Lad'):
                    value /= 10
                self.values[self._keymap[key]] = value
            elif key in self._statuskeymap:
                self.status[self._statuskeymap[key]] = value[0]
            elif key in self._targetkeymap:
                self.targets[self._targetkeymap[key]] = value
            else:
                return
            self.update()

    def sizeHint(self):
        return QSize(self.props['width'] * self._scale + 2,
                     self.props['height'] * self._scale + 2)
