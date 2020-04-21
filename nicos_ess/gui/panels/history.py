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

from nicos.clients.gui.panels.history import \
    HistoryPanel as DefaultHistoryPanel
from nicos.guisupport.qt import QActionGroup, QCheckBox, QComboBox, QFrame, \
    QHBoxLayout, QToolBar, QWidgetAction

from nicos_ess.gui.panels import get_icon


class HistoryPanel(DefaultHistoryPanel):

    def __init__(self, parent, client, options):
        DefaultHistoryPanel.__init__(self, parent, client, options)
        self.layout().setMenuBar(self.setPanelToolbar())
        self.set_icons()

    def setPanelToolbar(self):
        bar = QToolBar('History viewer')
        bar.addAction(self.actionNew)
        bar.addAction(self.actionEditView)
        bar.addSeparator()
        bar.addAction(self.actionSavePlot)
        bar.addAction(self.actionPrint)
        bar.addAction(self.actionSaveData)
        bar.addSeparator()
        bar.addAction(self.actionUnzoom)
        bar.addAction(self.actionLogScale)
        bar.addSeparator()
        bar.addAction(self.actionAutoScale)
        bar.addAction(self.actionScaleX)
        bar.addAction(self.actionScaleY)
        bar.addSeparator()
        bar.addAction(self.actionResetView)
        bar.addAction(self.actionDeleteView)
        bar.addSeparator()
        bar.addAction(self.actionFitPeak)
        wa = QWidgetAction(bar)
        self.fitPickCheckbox = QCheckBox(bar)
        self.fitPickCheckbox.setText('Pick')
        self.fitPickCheckbox.setChecked(True)
        self.actionPickInitial.setChecked(True)
        self.fitPickCheckbox.toggled.connect(self.actionPickInitial.setChecked)
        self.actionPickInitial.toggled.connect(self.fitPickCheckbox.setChecked)
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(self.fitPickCheckbox)
        frame = QFrame(bar)
        frame.setLayout(layout)
        wa.setDefaultWidget(frame)
        bar.addAction(wa)
        ag = QActionGroup(bar)
        ag.addAction(self.actionFitPeakGaussian)
        ag.addAction(self.actionFitPeakLorentzian)
        ag.addAction(self.actionFitPeakPV)
        ag.addAction(self.actionFitPeakPVII)
        ag.addAction(self.actionFitTc)
        ag.addAction(self.actionFitCosine)
        ag.addAction(self.actionFitSigmoid)
        ag.addAction(self.actionFitLinear)
        ag.addAction(self.actionFitExponential)
        wa = QWidgetAction(bar)
        self.fitComboBox = QComboBox(bar)
        for a in ag.actions():
            itemtext = a.text().replace('&', '')
            self.fitComboBox.addItem(itemtext)
            self.fitfuncmap[itemtext] = a
        self.fitComboBox.currentIndexChanged.connect(
            self.on__fitComboBox_currentIndexChanged)
        wa.setDefaultWidget(self.fitComboBox)
        bar.addAction(wa)
        bar.addSeparator()
        bar.addAction(self.actionFitArby)
        self.bar = bar
        self.actionFitLinear.trigger()
        return bar

    def set_icons(self):
        self.actionNew.setIcon(get_icon('add_circle_outline-24px.svg'))
        self.actionEditView.setIcon(get_icon('edit-24px.svg'))
        self.actionSavePlot.setIcon(get_icon('save-24px.svg'))
        self.actionPrint.setIcon(get_icon('print-24px.svg'))
        self.actionUnzoom.setIcon(get_icon('zoom_out-24px.svg'))
        self.actionSaveData.setIcon(get_icon('archive-24px.svg'))

    def getToolbars(self):
        return []
