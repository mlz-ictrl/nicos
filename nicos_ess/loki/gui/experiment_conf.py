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
#   AÜC Hardal <umit.hardal@ess.eu>
#
# *****************************************************************************

"""LoKI Experiment Configuration dialog."""

from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QFrame
from nicos.utils import findResource

from nicos_ess.loki.gui.loki_panel import LokiPanelBase


class LokiExperimentPanel(LokiPanelBase):
    panelName = 'LoKI Instrument Setup'

    def __init__(self, parent, client, options):
        LokiPanelBase.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_ess/loki/gui/ui_files/exp_config.ui'))
        
        self.experiment_frame = QFrame(self)

        self.holder_info = options.get('holder_info', [])
        self.instrument = options.get('instrument', 'loki')
        self.initialise_connection_status_listeners()

    def setViewOnly(self, viewonly):
        pass
