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

import os

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.guisupport.qt import QPixmap, Qt
from nicos.protocols.daemon import STATUS_RUNNING

from nicos_ess.gui import uipath


def decolor_logo(pixmap, color):
    retpix = QPixmap(pixmap.size())
    retpix.fill(color)
    retpix.setMask(pixmap.createMaskFromColor(Qt.transparent))
    return retpix


class RunningScriptPanel(Panel):
    """Provides a panel that shows the command that is currently executed."""

    panelName = 'Script status'
    ui = '%s/panels/runningscript.ui' % uipath

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.ui)

        pxr = decolor_logo(QPixmap("resources/nicos-logo-high.png"), Qt.white)
        self.nicosLabel.setPixmap(pxr)

        self.runningCmdLabel.setIndent(10)
        self.idle_style = """QLabel { color: black; background: white;
        border-radius: 10px;};"""
        self.runningCmdLabel.setStyleSheet(self.idle_style)

        # if INSTRUMENT is defined add the logo/name of the instrument
        instrument = os.getenv('INSTRUMENT')
        if instrument:
            instrument = instrument.split('.')[-1]
            logo = decolor_logo(QPixmap('resources/%s-logo.png' % instrument),
                                Qt.white)
            if logo.isNull():
                self.instrumentLabel.setText(instrument.upper())
            else:
                self.instrumentLabel.setPixmap(logo.scaledToHeight(
                    self.instrumentLabel.height(), Qt.SmoothTransformation))
        else:
            self.instrumentLabel.setText('')

        self.current_script = []
        client.processing.connect(self.on_client_processing)
        client.status.connect(self.on_client_status)

    def on_client_processing(self, request):
        self.current_script = []
        if 'script' not in request:
            return
        self.current_script = [line.lstrip().rstrip() for line in request[
            'script'].splitlines()]

    def on_client_status(self, status):
        st, line = status
        if st != STATUS_RUNNING:
            self.runningCmdLabel.setText('')
            return
        if line == -1 or line >= len(self.current_script):
            self.runningCmdLabel.setText('')
            return
        self.runningCmdLabel.setText(self.current_script[line - 1])
