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

"""NICOS GUI default configuration."""

from nicos.clients.gui.config import hsplit, vsplit, window, panel, tool, \
    tabbed, setups

main_window = tabbed(
    ('SANS acquisition',
     panel('nicos.demo.gui.sanspanel.SANSPanel'), setups('sans')),
    ('Expert mode',
     vsplit(
         hsplit(
             panel('status.ScriptStatusPanel'),
             panel('watch.WatchPanel'),
         ),
         panel('console.ConsolePanel'),
     )),
    ('SampleChanger', panel('nicos.sans1.gui.samplechanger.SamplechangerSetupPanel',
                            image = 'custom/sans1/lib/gui/sampleChanger11.png',
                            positions = 11), setups('sans')),
    ('Setup',
     tabbed(('Experiment', panel('setup_panel.ExpPanel')),
            ('Setups',     panel('setup_panel.SetupsPanel')),
            ('Detectors/Environment', panel('setup_panel.DetEnvPanel')),
        )),
)

windows = [
    window('Editor', 'editor', True,
        panel('editor.EditorPanel',
              tools = [
                  tool('Scan', 'nicos.clients.gui.tools.scan.ScanTool')
              ])),
    #window('Scans', 'plotter', True,
    #    panel('scans.ScansPanel')),
    window('Device History', 'find', True,
           panel('history.HistoryPanel')),
    window('Logbook', 'table', True,
           panel('elog.ELogPanel')),
]

tools = [
    tool('Calculator', 'calculator.CalculatorTool'),
    tool('Neutron cross-sections', 'website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
    tool('Neutron activation', 'website.WebsiteTool',
         url='http://www.frm2.tum.de/intranet/activation/'),
    tool('Report NICOS bug or request enhancement', 'bugreport.BugreportTool'),
]
