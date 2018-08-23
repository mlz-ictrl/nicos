#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2018 by the NICOS contributors (see AUTHORS)
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

main_window = tabbed(
    ('Commands',
     docked(
        vsplit(
            hsplit(
                panel('nicos.clients.gui.panels.console.ConsolePanel',
                      hasinput=False, hasmenu=False,
                      watermark='nicos_sinq/watermark.png'),
            ),
            hsplit(
                panel('nicos.clients.gui.panels.status.ScriptStatusPanel'),
            ),
            hsplit(
                panel('nicos.clients.gui.panels.commandline.CommandLinePanel'),
            ),
        ),
        ('Control Panel',
         panel('nicos_sinq.amor.gui.panels.controlpanel.AmorControlPanel',
               uifile='nicos_sinq/amor/gui/panels/controlpanel.ui',
               dockpos='right',)),
        ('AMOR',
         panel('nicos_sinq.amor.gui.panels.expinfo.AmorExpPanel',
               uifile='nicos_sinq/amor/gui/panels/expinfo.ui',
               dockpos='left')))),
    ('Errors/Warnings', panel('nicos.clients.gui.panels.errors.ErrorPanel')),
)

windows = [
    window('Script Builder', 'editor',
        vsplit(
            panel('nicos.clients.gui.panels.scriptbuilder.CommandsPanel'),
            panel('nicos.clients.gui.panels.editor.EditorPanel',
              tools = [
                  tool('Scan Generator',
                       'nicos.clients.gui.tools.scan.ScanTool')
              ]))),
    window('Device List', 'paused',
           panel('nicos.clients.gui.panels.devices.DevicesPanel', icons=True)),
    window('Device History', 'find',
           panel('nicos.clients.gui.panels.history.HistoryPanel')),
    window('Live View', 'live',
           panel('nicos_sinq.amor.gui.panels.live.LiveDataPanel')),
    window('Scan View', 'plotter',
           panel('nicos.clients.gui.panels.scans.ScansPanel')),
    window('Logbook', 'table',
           panel('nicos.clients.gui.panels.elog.ELogPanel')),
]

tools = [
    tool('Calculator', 'nicos.clients.gui.tools.calculator.CalculatorTool'),
    tool('Neutron cross-sections',
         'nicos.clients.gui.tools.website.WebsiteTool',
         url='http://www.ncnr.nist.gov/resources/n-lengths/'),
]
