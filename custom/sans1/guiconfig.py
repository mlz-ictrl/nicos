#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2014 by the NICOS contributors (see AUTHORS)
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

"""SANS1 GUI default configuration."""

from nicos.clients.gui.config import hsplit, vsplit, window, panel, tool, tabbed, docked, setups  # pylint: disable=W0611

# evaluated by code in : nicos.clients.gui.panels.__init__.createWindowItem

# vsplit( content1, content2, ... )
# hsplit( content1, content2, ... )
# tapped( (tabname1, content1), (tabname2, content2),... )
# docked( content1, (tabname, content2), ... )
## if with tabname, content panels can be stacked, then a tabbar is displayed with the tabnames..

# window( <Button/WindowName>, <icon-name>, bool, content )
# icons are defined in resources/nicos-gui.qrc
## known icons: setup, editor, plotter, find, table, errors, live

# tool( Menu-entry-str, <modulepath>, [, kwargs ] )
## options for all: runatstartup=True/False
## known <modulepaths> below nicos.clients.gui.tools:
# 'calculator.CalculatorTool'
# 'website.WebsiteTool'
# 'estop.EmergencyStopTool'
# 'scan.ScanTool'
# 'commands.CommandsTool'

# panel( <modulepath> [, kwargs ] )
## known <modulepath> below nicos.clients.gui.panels:
# 'cmdbuilder.CommandPanel'
# 'commandline.CommandLinePanel'
# 'console.ConsolePanel'
# 'devices.DevicesPanel' icons = True/False: Show/hide status icons
# 'editor.EditorPanel'
# 'elog.ELogPanel'
# 'errors.ErrorPanel'
# 'expinfo.ExpInfoPanel'
# 'generic.GenericPanel'  loads an uifile='path-to-uifile.ui' from dir='directory-containing-ui-file', also connects to cache....
# 'history.HistoryPanel'
# 'live.LiveDataPanel'
# 'logviewer.LogViewerPanel'
# 'scans.ScansPanel'
# 'scriptbuilder.CommandsPanel'
# 'setup_panel.SetupPanel'
# 'status.ScriptStatusPanel'
# 'watch.WatchPanel'



# config = (ignored, [Mainwindow + N*window(...)], [tools])
config = ('Default', [
        docked(
            vsplit(
                panel('status.ScriptStatusPanel'),
#                panel('watch.WatchPanel'),
                panel('console.ConsolePanel'),
            ),
            #~ ('Watch Expressions',panel('watch.WatchPanel')),
            ('NICOS devices',
             panel('devices.DevicesPanel',
                   icons=True, dockpos='right',
                  )
            ),
            ('Experiment info', panel('expinfo.ExpInfoPanel')),
        ),
        window('Setup', 'setup', True,
            tabbed(
                ('Experiment',
                    panel('setup_panel.ExpPanel')),
                ('Setups',
                    panel('setup_panel.SetupsPanel')),
                ('Detectors/Environment',
                    panel('setup_panel.DetEnvPanel')),
                #~ ('Samples',
                    #~ panel('nicos.sans1.gui.samplechanger.SamplechangerSetupPanel',
                        #~ image='custom/sans1/lib/gui/sampleChanger11.png',
                        #~ positions = 11), setups('!setup22')),
                ('Samples',
                    panel('nicos.sans1.gui.samplechanger.SamplechangerSetupPanel',
                        image='custom/sans1/lib/gui/sampleChanger22.png',
                        positions = 22), setups('sc1')),
            )
        ),
        window('Editor', 'editor', True,
            vsplit(
                panel('scriptbuilder.CommandsPanel'),
                panel('editor.EditorPanel',
                    tools = [
                            tool('Scan', 'scan.ScanTool')
                            ]
                    )
                )
        ),
        window('Watches', 'leds/blue_on', True,
            panel('watch.WatchPanel')),
        window('Scans', 'plotter', True,
            panel('scans.ScansPanel')),
        window('History', 'find', True,
            panel('history.HistoryPanel')),
        window('Logbook', 'table', True,
            panel('elog.ELogPanel')),
        window('Log files', 'table', True,
            panel('logviewer.LogViewerPanel')),
        window('Errors', 'errors', True,
            panel('errors.ErrorPanel')),
    ], [
        tool('Downtime report', 'downtime.DownTimeTool',
             receiver='f.carsughi@fz-juelich.de',
             mailserver='smtp.frm2.tum.de',
             sender='sans1@frm2.tum.de',
            ),
        tool('Calculator', 'calculator.CalculatorTool'),
        tool('Neutron cross-sections', 'website.WebsiteTool',
             url='http://www.ncnr.nist.gov/resources/n-lengths/'),
        tool('Neutron activation', 'website.WebsiteTool',
             url='http://www.frm2.tum.de/intranet/activation/'),
        tool('Neutron calculations', 'website.WebsiteTool',
             url='http://www.frm2.tum.de/intranet/neutroncalc/'),
        tool('Report NICOS bug', 'website.WebsiteTool',
             url='http://trac.frm2.tum.de/redmine/projects/nicos/issues/new'),
        tool('Emergency stop button', 'estop.EmergencyStopTool',
             runatstartup=False),
        tool('Maintenance commands',
             'nicos.clients.gui.tools.commands.CommandsTool',
             commands=[
                 ('TACO server control panel (beta)',
                  'SSH_ASKPASS=/usr/bin/ssh-askpass setsid /usr/bin/ssh -XY '
                  'maint@sans1hw.sans1.frm2 "source /etc/tacoenv.sh && '
                  'sudo /usr/bin/python /opt/tacocp/tacocp.py '
                  'sans1srv.sans1.frm2" && exit',
                 ),
             ]),
    ]
)
