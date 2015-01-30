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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI configuration for PANDA."""

from nicos.clients.gui.config import vsplit, window, panel, tool, docked, \
    tabbed, setups

main_window = docked(
    vsplit(
        panel('status.ScriptStatusPanel'),
        # panel('watch.WatchPanel'),
        panel('console.ConsolePanel'),
    ),
    ('NICOS devices',
     panel('nicos.clients.gui.panels.devices.DevicesPanel',
           icons=True, dockpos='right',
          )
    ),
    ('Experiment Information and Setup',
     panel('nicos.clients.gui.panels.expinfo.ExpInfoPanel',
           sample_panel=panel('nicos.clients.gui.panels.setup_panel.TasSamplePanel'),
          )
    ),
)

windows = [
    window('Editor', 'editor',
        vsplit(
            panel('scriptbuilder.CommandsPanel'),
            panel('editor.EditorPanel',
              tools = [
                  tool('Scan Generator', 'nicos.clients.gui.tools.scan.ScanTool')
              ]))),
    window('Scans', 'plotter', panel('scans.ScansPanel')),
    window('History', 'find', panel('history.HistoryPanel')),
    window('Logbook', 'table', panel('elog.ELogPanel')),
    window('Log files', 'table', panel('logviewer.LogViewerPanel')),
    window('Errors', 'errors', panel('errors.ErrorPanel')),
    #window('Live data', 'live', panel('live.LiveDataPanel')),
]

tools = [
    tool('Downtime report', 'downtime.DownTimeTool',
         receiver='f.carsughi@fz-juelich.de',
         mailserver='smtp.frm2.tum.de',
         sender='panda@frm2.tum.de',
        ),
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'website.WebsiteTool',
         url='http://www.frm2.tum.de/intranet/activation/'),
    tool('Neutron calculations',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.frm2.tum.de/intranet/neutroncalc/'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
    tool('Emergency stop button', 'estop.EmergencyStopTool',
         runatstartup=False),
    tool('Maintenance commands',
         'nicos.clients.gui.tools.commands.CommandsTool',
         commands=[
             ('TACO server control @PANDA21 (beta)', 'SSH_ASKPASS=/usr/bin/ssh-askpass setsid /usr/bin/ssh -XY maint@panda21.panda.frm2 "source /etc/tacoenv.sh && XAUTHORITY=/home/maint/.Xauthority sudo -E /usr/bin/python /opt/tacocp/tacocp.py pandasrv.panda.frm2" && exit'),
         ]),
]
