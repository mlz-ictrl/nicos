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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI user editor window."""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels.editor import EditorPanel as DefaultEditorPanel
from nicos.clients.gui.utils import showToolText
from nicos.guisupport.qt import QToolBar


class EditorPanel(DefaultEditorPanel):

    def __init__(self, parent, client, options):
        if not 'show_browser' in options:
            options['show_browser'] = False
        DefaultEditorPanel.__init__(self, parent, client, options)
        self.layout().setMenuBar(self.createPanelToolbar())

    def createPanelToolbar(self):
        bar = QToolBar('Editor')
        bar.addAction(self.actionNew)
        bar.addAction(self.actionOpen)
        bar.addAction(self.actionSave)
        bar.addSeparator()
        bar.addAction(self.actionPrint)
        bar.addSeparator()
        bar.addAction(self.actionUndo)
        bar.addAction(self.actionRedo)
        bar.addSeparator()
        bar.addAction(self.actionCut)
        bar.addAction(self.actionCopy)
        bar.addAction(self.actionPaste)
        bar.addSeparator()
        bar.addAction(self.actionRun)
        bar.addAction(self.actionSimulate)
        bar.addAction(self.actionGet)
        bar.addAction(self.actionUpdate)
        showToolText(bar, self.actionRun)
        showToolText(bar, self.actionSimulate)
        showToolText(bar, self.actionGet)
        showToolText(bar, self.actionUpdate)
        return bar

    def getToolbars(self):
        return []
