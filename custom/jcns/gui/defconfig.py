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

from nicos.clients.gui.config import hsplit, vsplit, window, panel, tool, \
        tabbed, docked

default_profile_uid = '07139e62-d244-11e0-b94b-00199991c245'
default_profile_config = ('Default', [
        tabbed(
               ('JCNS instrument',
                docked(
                    vsplit(
                        hsplit(
                            panel('expinfo.ExpInfoPanel'),
                            vsplit(
                                panel('cmdbuilder.CommandPanel'),
                                panel('status.ScriptStatusPanel'),
                            ),
                        ),
                    tabbed(
                         ('All output',
                          panel('console.ConsolePanel',
                          hasinput=False, hasmenu=False,
                          ),
                         ),
                         ('Errors/Warnings',
                           panel('errors.ErrorPanel'),
                         ),
                         ),
                        ),
                        ('NICOS devices',
                         panel('devices.DevicesPanel',
                               icons=True,
                               dockpos='right',
                              ),
                        ),
                    ),
               ),
#              panel('watch.WatchPanel'),
               ('Editor',
                vsplit(
                    panel('scriptbuilder.CommandsPanel'),
                    panel('editor.EditorPanel',
                       tools = [
                          tool('Scan', 'nicos.clients.gui.tools.scan.ScanTool')
                    ]),
                ),
               ),
        ),
        window('Setup', 'setup', True,
            panel('setup.SetupPanel')),
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
             url='http://www.wise-uranium.org/rnac.html'),
        tool('Report NICOS bug',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='http://trac.frm2.tum.de/redmine/projects/nicos/issues/new'),
    ]
)
