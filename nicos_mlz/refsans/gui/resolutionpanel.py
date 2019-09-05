#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2019 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi
from nicos.core.errors import NicosError
from nicos.guisupport.qt import QDialogButtonBox, QDoubleValidator, \
    QMessageBox, pyqtSlot
from nicos.guisupport.widget import NicosWidget
from nicos.utils import findResource

from nicos_mlz.refsans.gui.timedistancewidget import TimeDistanceWidget
from nicos_mlz.refsans.lib.calculations import chopper_config


class ResolutionPanel(NicosWidget, Panel):

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        self.setClient(client)
        NicosWidget.__init__(self)
        client.connected.connect(self.on_client_connected)
        self.destroyed.connect(self.on_destroyed)
        if parent:
            self.buttonBox.rejected.connect(parent.close)
        else:
            self.buttonBox.rejected.connect(self.close)

        self.wLmin.valueChanged['double'].connect(self.recalculate)
        self.wLmax.valueChanged['double'].connect(self.recalculate)
        self.gap.valueChanged['double'].connect(self.recalculate)
        self.D.valueChanged['double'].connect(self.recalculate)
        self.disc2_pos.valueChanged['int'].connect(self.recalculate)
        self.SC2_mode.currentIndexChanged.connect(self.recalculate)
        self.periods.valueChanged['int'].connect(self.recalculate)
        self.buttonBox.clicked.connect(self.createScript)

        self.ttd = TimeDistanceWidget()
        self.ttdPlot.layout().addWidget(self.ttd)

    def on_destroyed(self):
        pass

    def initUi(self):
        loadUi(self, findResource('nicos_mlz/refsans/gui/resolutionpanel.ui'))

        valid = QDoubleValidator()

        for f in (self.chSpeed, self.phase2, self.phase3, self.phase4,
                  self.phase5, self.phase6):
            f.setValidator(valid)
            f.setReadOnly(True)

    def registerKeys(self):
        pass

    def on_client_connected(self):
        missed_devices = []
        for d in ('chSpeed', 'chRatio', 'chWL', 'chST'):
            try:
                self.client.eval('%s.pollParam()', None)
                params = self.client.getDeviceParams(d)
                for p, v in params.items():
                    self._update_key('%s/%s' % (d, p), v)
            except (NicosError, NameError):
                missed_devices += [d]
        if not missed_devices:
            self.recalculate()
        else:
            QMessageBox.warning(self.parent().parent(), 'Error',
                                'The following devices are not available:<br>'
                                "'%s'" % ', '.join(missed_devices))
            self.buttonBox.removeButton(
                self.buttonBox.button(QDialogButtonBox.Apply))

    def _update_key(self, key, value):
        pass

    @pyqtSlot()
    def recalculate(self):
        wlmin = self.wLmin.value()
        wlmax = self.wLmax.value()
        D = self.D.value()
        disk2 = self.disc2_pos.value()
        gap = self.gap.value() / 100.
        speed, angles = chopper_config(wlmin, wlmax, D, disk2, gap=gap)

        self.chSpeed.setText('%d rpm' % speed)
        self.phase2.setText('%.2f deg' % angles[1])
        self.phase3.setText('%.2f deg' % angles[2])
        self.phase4.setText('%.2f deg' % angles[3])
        self.phase5.setText('%.2f deg' % angles[4])
        self.phase6.setText('%.2f deg' % angles[5])

        nperiods = self.periods.value()
        self.ttd.plot(speed, angles, nperiods, disk2, D)

    @pyqtSlot('QAbstractButton *')
    def createScript(self, button):
        if self.buttonBox.standardButton(button) == QDialogButtonBox.Apply:
            pass
