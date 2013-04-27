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
#   Jens Krueger <jens.krueger@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI default configuration."""

__version__ = "$Revision$"

from nicos.clients.gui.config import hsplit, vsplit, window, panel, tool, tabbed

default_profile_uid = '07139e62-d244-11e0-b94b-00199991c245'
default_profile_config = ('Default', [
        tabbed(
#              ('SANS acquisition', panel('nicos.demo.gui.sanspanel.SANSPanel')),
               ('Demo instrument',
                vsplit(
                    hsplit(
                        panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel'),
#                       panel('nicos.clients.gui.panels.watch.WatchPanel'),
                        vsplit(
                            panel('nicos.clients.gui.panels.commandline.CommandLinePanel'),
                            panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
                        ),
                        panel('nicos.clients.gui.panels.devices.DevicesPanel'),
                    ),
#                   panel('nicos.clients.gui.panels.cmdinput.CommandsPanel'),
                    panel('nicos.clients.gui.panels.console.ConsolePanel',
                          hasinput=False,
                         ),
                ),
               ),
               ('Editor',
                vsplit(
                    panel('nicos.clients.gui.panels.cmdinput.CommandsPanel'),
                    panel('nicos.clients.gui.panels.editor.EditorPanel',
                       tools = [
                          tool('Scan', 'nicos.clients.gui.tools.scan.ScanTool')
                    ]),
                ),
               ),
        ),
        window('Setup', 'setup', True,
            panel('nicos.clients.gui.panels.setup.SetupPanel')),
        window('Scans', 'plotter', True,
            panel('nicos.clients.gui.panels.scans.ScansPanel')),
        window('Errors', 'errors', True,
            panel('nicos.clients.gui.panels.errors.ErrorPanel')),
        window('History', 'find', True,
            panel('nicos.clients.gui.panels.history.HistoryPanel')),
        window('Logbook', 'table', True,
            panel('nicos.clients.gui.panels.elog.ELogPanel')),
    ], [
        tool('Calculator',
             'nicos.clients.gui.tools.calculator.CalculatorTool'),
        tool('Neutron cross-sections',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='http://www.ncnr.nist.gov/resources/n-lengths/'),
        tool('Neutron activation',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='http://www.wise-uranium.org/rnac.html'),
        tool('Report NICOS bug',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='http://trac.frm2.tum.de/redmine/projects/nicos/issues/new'),
    ]
)
