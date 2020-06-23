# -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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
#   Michele Brambilla <michele.brambilla@psi.ch>
#
# *****************************************************************************

from nicos.clients.gui.panels.status import \
    ScriptStatusPanel as DefaultScriptStatusPanel

from nicos_ess.gui.panels import get_icon


class ScriptStatusPanel(DefaultScriptStatusPanel):
    def __init__(self, parent, client, options):
        DefaultScriptStatusPanel.__init__(self, parent, client, options)
        self.set_icons()
        self.layout().setMenuBar(self.bar)

    def set_icons(self):
        self.actionBreak.setIcon(get_icon('pause-24px.svg'))
        self.actionBreak2.setIcon(get_icon('pause-24px.svg'))
        self.actionBreakCount.setIcon(get_icon('pause_red-24px.svg'))
        self.actionContinue.setIcon(get_icon('play_arrow-24px.svg'))
        self.actionEmergencyStop.setIcon(get_icon('cancel_red-24px.svg'))
        self.actionFinish.setIcon(get_icon('done-24px.svg'))
        self.actionFinishEarly.setIcon(get_icon('finish_early-24px.svg'))
        self.actionFinishEarlyAndStop.setIcon(get_icon('skip_next-24px.svg'))
        self.actionStop.setIcon(get_icon('stop-24px.svg'))
        self.actionStop2.setIcon(get_icon('stop-24px.svg'))

    def getToolbars(self):
        return []
