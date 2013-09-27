#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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

from nicos.clients.gui.config import hsplit, vsplit, window, panel, tool, tabbed

config = ('Default', [
        tabbed(('SANS acquisition', panel('nicos.demo.gui.sanspanel.SANSPanel')),
               ('Expert mode',
                vsplit(
                    hsplit(
                        panel('status.ScriptStatusPanel'),
                        panel('watch.WatchPanel'),
                        ),
                    panel('console.ConsolePanel'),
                )),
        ),
        window('Setup', 'setup', True,
            panel('setup_panel.SetupPanel')),
        window('Editor', 'editor', True,
            panel('editor.EditorPanel',
                  tools = [
                      tool('Scan', 'nicos.clients.gui.tools.scan.ScanTool')
                  ])),
        window('Scans', 'plotter', True,
            panel('scans.ScansPanel')),
        window('History', 'find', True,
            panel('history.HistoryPanel')),
        window('Logbook', 'table', True,
            panel('elog.ELogPanel')),
    ], [
        tool('Calculator',
             'nicos.clients.gui.tools.calculator.CalculatorTool'),
        tool('Neutron cross-sections',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='http://www.ncnr.nist.gov/resources/n-lengths/'),
        tool('Neutron activation',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='http://www.frm2.tum.de/intranet/activation/'),
    ]
)
