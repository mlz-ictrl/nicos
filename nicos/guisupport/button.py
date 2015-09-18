#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

import ast

from PyQt4.QtCore import Qt

from nicos.guisupport.led import ClickableOutputLed, PropDef
from nicos.pycompat import string_types


class PushButton(ClickableOutputLed):

    designer_description = 'Simulation of a push button with a light'
    designer_icon = ':/leds/blue_on'

    def __init__(self, parent=None, designMode=False):
        ClickableOutputLed.__init__(self, parent, designMode)

    def on_keyChange(self, key, value, time, expired):
        if value == self._stateInactive:
            self.ledStatus = False
        else:
            self.ledStatus = True
        if self._goalval is not None:
            value = self._goalval
        self.current = value

    def mousePressEvent(self, event):

        ledColor = self.ledColor

        ClickableOutputLed.mousePressEvent(self, event)

        self.ledColor = ledColor


class SinglePushButton(PushButton):

    designer_description = 'Simulation of a push button with a light and only'\
                           ' one state to swith On or Off'
    designer_icon = ':/leds/yellow_on'

    properties = {
        'toState': PropDef(str, '1', 'Target for action'),
    }

    def __init__(self, parent=None, designMode=False):
        self._stateTo = 1
        PushButton.__init__(self, parent, designMode)

    def propertyUpdated(self, pname, value):
        PushButton.propertyUpdated(self, pname, value)

        if pname == 'toState':
            if isinstance(value, string_types):
                self._stateTo = value
            else:
                self._stateTo = ast.literal_eval(value) if value else 1

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self._client.run('move(%s, %r)' % (self.dev, self._stateTo))
        event.accept()
