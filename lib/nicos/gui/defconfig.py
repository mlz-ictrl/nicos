#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS-NG, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2011 by the NICOS-NG contributors (see AUTHORS)
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

"""NICOS GUI default configuration."""

__version__ = "$Revision$"

from nicos.gui.config import hsplit, vsplit, window, panel, tool

default_profile_uid = '07139e62-d244-11e0-b94b-00199991c245'
default_profile_config = ('Default', [
        vsplit(
            hsplit(
                panel('nicos.gui.panels.status.ScriptStatusPanel'),
                panel('nicos.gui.panels.watch.WatchPanel')),
                panel('nicos.gui.panels.console.ConsolePanel'),
            ),
        window('Errors/warnings', 'errors', True,
            panel('nicos.gui.panels.errors.ErrorPanel')),
        window('Editor', 'editor', False,
            panel('nicos.gui.panels.editor.EditorPanel')),
        window('Scans', 'plotter', True,
            panel('nicos.gui.panels.scans.ScansPanel')),
        window('History', 'find', True,
            panel('nicos.gui.panels.history.HistoryPanel')),
        window('Logbook', 'table', True,
            panel('nicos.gui.panels.elog.ELogPanel')),
    ], [
        tool('Calculator',
            'nicos.gui.tools.calculator.CalculatorTool'),
    ]
)
