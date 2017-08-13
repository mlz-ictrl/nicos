#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI tools."""

from nicos.guisupport.qt import Qt, QTimer, QAction

from nicos.utils import importString, createSubprocess
from nicos.clients.gui.config import tool, cmdtool, menu


def runTool(window, tconfig):
    """Run a tool from *tconfig*

    If it is a tool dialog, use *window* as the parent.
    """
    if isinstance(tconfig, tool):
        try:
            toolclass = importString(tconfig.clsname)
        except ImportError:
            window.showError('Could not import class %r.' % tconfig.clsname)
        else:
            dialog = toolclass(window, window.client, **tconfig.options)
            dialog.setWindowModality(Qt.NonModal)
            dialog.setAttribute(Qt.WA_DeleteOnClose, True)
            dialog.show()
    elif isinstance(tconfig, cmdtool):
        try:
            createSubprocess(tconfig.cmdline)
        except Exception as err:
            window.showError('Could not execute command: %s' % err)


def createToolMenu(window, config, menuitem):
    """Create menu entries for tools in *config* under *menuitem*.

    Use *window* as the parent window for dialogs.
    """
    for tconfig in config:
        if isinstance(tconfig, menu):
            submenu = menuitem.addMenu(tconfig.name)
            createToolMenu(window, tconfig.items, submenu)
        else:
            def tool_callback(on, tconfig=tconfig):
                runTool(window, tconfig)
            action = QAction(tconfig.name, window)
            menuitem.addAction(action)
            action.triggered.connect(tool_callback)


def startStartupTools(window, config):
    """Start all tools that are set to *runatstartup* from *config*.

    Use *window* as the parent window for dialogs.
    """
    for tconfig in config:
        if isinstance(tconfig, menu):
            startStartupTools(window, tconfig.items)
        elif isinstance(tconfig, tool) and tconfig.options.get('runatstartup'):
            QTimer.singleShot(0, lambda tc=tconfig: runTool(window, tc))
