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


from nicos.clients.gui.panels.scans import ScansPanel as DefaultScansPanel
from nicos.guisupport.qt import QActionGroup, QCheckBox, QComboBox, QFrame, \
    QHBoxLayout, QToolBar, QWidgetAction


class ScansPanel(DefaultScansPanel):
    def __init__(self, parent, client, options):
        DefaultScansPanel.__init__(self, parent, client, options)
        self.bars = self.createPanelToolbar()
        for index, bar in enumerate(self.bars):
            self.layout().insertWidget(index, bar)

    def createPanelToolbar(self):
        bar = QToolBar('Scans')
        bar.addAction(self.actionSavePlot)
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionXAxis)
        bar.addAction(self.actionYAxis)
        bar.addAction(self.actionNormalized)
        bar.addSeparator()
        bar.addAction(self.actionLogXScale)
        bar.addAction(self.actionLogScale)
        bar.addAction(self.actionUnzoom)
        bar.addSeparator()
        bar.addAction(self.actionAutoScale)
        bar.addAction(self.actionScaleX)
        bar.addAction(self.actionScaleY)
        bar.addAction(self.actionLegend)
        bar.addAction(self.actionErrors)
        bar.addAction(self.actionResetPlot)
        bar.addAction(self.actionDeletePlot)
        bar.addSeparator()
        bar.addAction(self.actionAutoDisplay)
        bar.addAction(self.actionCombine)

        fitbar = QToolBar('Scan fitting')
        fitbar.addAction(self.actionFitPeak)
        wa = QWidgetAction(fitbar)
        self.fitPickCheckbox = QCheckBox(fitbar)
        self.fitPickCheckbox.setText('Pick')
        self.fitPickCheckbox.setChecked(True)
        self.actionPickInitial.setChecked(True)
        self.fitPickCheckbox.toggled.connect(self.actionPickInitial.setChecked)
        self.actionPickInitial.toggled.connect(self.fitPickCheckbox.setChecked)
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 0, 10, 0)
        layout.addWidget(self.fitPickCheckbox)
        frame = QFrame(fitbar)
        frame.setLayout(layout)
        wa.setDefaultWidget(frame)
        fitbar.addAction(wa)
        ag = QActionGroup(fitbar)
        ag.addAction(self.actionFitPeakGaussian)
        ag.addAction(self.actionFitPeakLorentzian)
        ag.addAction(self.actionFitPeakPV)
        ag.addAction(self.actionFitPeakPVII)
        ag.addAction(self.actionFitTc)
        ag.addAction(self.actionFitCosine)
        ag.addAction(self.actionFitSigmoid)
        ag.addAction(self.actionFitLinear)
        ag.addAction(self.actionFitExponential)
        wa = QWidgetAction(fitbar)
        self.fitComboBox = QComboBox(fitbar)
        for a in ag.actions():
            itemtext = a.text().replace('&', '')
            self.fitComboBox.addItem(itemtext)
            self.fitfuncmap[itemtext] = a
        self.fitComboBox.currentIndexChanged.connect(
            self.on_fitComboBox_currentIndexChanged)
        wa.setDefaultWidget(self.fitComboBox)
        fitbar.addAction(wa)
        fitbar.addSeparator()
        fitbar.addAction(self.actionFitArby)

        bars = [bar, fitbar]

        return bars

    def getToolbars(self):
        return []
