#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI configuration for ANTARES."""

from nicos.clients.gui.config import hsplit, vsplit, window, panel, tool, tabbed

config = ('Default', [
        hsplit(
            vsplit(
                panel('status.ScriptStatusPanel'),
#                panel('watch.WatchPanel'),
                panel('console.ConsolePanel'),
            ),
            vsplit(
                panel('expinfo.ExpInfoPanel'),
                panel('devices.DevicesPanel'),
            ),
        ),
        window('Setup', 'setup', True,
            tabbed(('Experiment', panel('setup_panel.ExpPanel')),
                   ('Setups',     panel('setup_panel.SetupsPanel')),
                   ('Detectors/Environment', panel('setup_panel.DetEnvPanel')),
            )),
        window('Editor', 'editor', True,
            vsplit(
                panel('scriptbuilder.CommandsPanel'),
                panel('editor.EditorPanel'))),
        window('Scans', 'plotter', True,
            panel('scans.ScansPanel')),
        window('History', 'find', True,
            panel('history.HistoryPanel')),
        window('Logbook', 'table', True,
            panel('elog.ELogPanel')),
        window('Errors', 'errors', True,
            panel('errors.ErrorPanel')),
        window('Live data', 'live', True,
            panel('live.LiveDataPanel',
                  instrument = 'imaging')),
    ], [
        tool('Downtime report', 'downtime.DownTimeTool',
             receiver='f.carsughi@fz-juelich.de',
             mailserver='smtp.frm2.tum.de',
             sender='antares@frm2.tum.de',
            ),
        tool('Calculator',
             'nicos.clients.gui.tools.calculator.CalculatorTool'),
        tool('Neutron cross-sections',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='http://www.ncnr.nist.gov/resources/n-lengths/'),
        tool('Neutron activation',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='https://webapps.frm2.tum.de/intranet/activation/'),
        tool('Neutron calculations',
             'nicos.clients.gui.tools.website.WebsiteTool',
             url='https://webapps.frm2.tum.de/intranet/neutroncalc/'),
        tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
        tool('Maintenance commands',
             'nicos.clients.gui.tools.commands.CommandsTool',
             commands=[
                 ('TACO server control panel (beta)', 'SSH_ASKPASS=/usr/bin/ssh-askpass setsid /usr/bin/ssh -XY maint@antareshw.antares.frm2 "source /etc/tacoenv.sh && sudo /usr/bin/python /opt/tacocp/tacocp.py antaressrv.antares.frm2" && exit'),
             ]),
    ]
)
