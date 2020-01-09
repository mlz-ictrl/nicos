#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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
#   Alexander Steffens <a.steffens@fz-juelich.de>
#
# *****************************************************************************

"""JCNS instrument specific NICOS GUI experiment setup panels."""


from nicos.clients.gui.panels.setup_panel import GenericSamplePanel
from nicos.utils import findResource


class IFFSamplePanel(GenericSamplePanel):
    """Provides the sample ID required for the IFF sample database."""

    panelName = 'IFF sample setup'
    uiName = findResource('nicos_jcns/gui/setup_iffsample.ui')

    def getEditBoxes(self):
        return [self.samplenameEdit, self.sampleidEdit]
