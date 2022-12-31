#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2023 by the NICOS contributors (see AUTHORS)
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
#   AÜC Hardal <umit.hardal@ess.eu>
#   Matt Clarke <matt.clarke@ess.eu>
#
# *****************************************************************************
"""NICOS GUI LoKI configuration."""

main_window = docked(
    tabbed(
        ('Experiment',
         panel('nicos_ess.gui.panels.exp_panel.ExpPanel', hide_sample=True)),
        ('Setup',
         panel('nicos.clients.flowui.panels.setup_panel.SetupsPanel')),
        ('Cell-holder Configuration',
         panel('nicos_ess.loki.gui.sample_holder_config.LokiSampleHolderPanel')
         ),
        ('  ', panel('nicos.clients.flowui.panels.empty.EmptyPanel')),
        (
            'Instrument interaction',
            hsplit(
                vbox(
                    panel(
                        'nicos.clients.flowui.panels.cmdbuilder.CommandPanel',
                        modules=['nicos.clients.gui.cmdlets'],
                    ),
                    tabbed(
                        ('Output',
                         panel(
                             'nicos.clients.flowui.panels.console.ConsolePanel',
                             hasinput=False)),
                        ('Scan Plot',
                         panel('nicos.clients.flowui.panels.scans.ScansPanel')
                         ),
                        ('Detector Image',
                         panel(
                             'nicos.clients.flowui.panels.live.MultiLiveDataPanel'
                         )),
                        ('Script Status',
                         panel(
                             'nicos.clients.flowui.panels.status.ScriptStatusPanel',
                             eta=True)),
                    ),
                ),  # vsplit
                panel(
                    'nicos.clients.flowui.panels.devices.DevicesPanel',
                    dockpos='right',
                    param_display={'Exp': ['lastpoint', 'lastscan']},
                    filters=[],
                ),
            ),  # hsplit
        ),
        (
            'Script Builder',
            panel('nicos_ess.loki.gui.scriptbuilder.LokiScriptBuilderPanel',
                  tools=None),
        ),
        (
            'Batch file generation',
            panel('nicos.clients.flowui.panels.editor.EditorPanel',
                  tools=None),
        ),
        (
            'History',
            panel('nicos.clients.flowui.panels.history.HistoryPanel'),
        ),
        (
            'Logs',
            tabbed(
                ('Errors',
                 panel('nicos.clients.gui.panels.errors.ErrorPanel')),
                ('Log files',
                 panel('nicos.clients.gui.panels.logviewer.LogViewerPanel')),
            ),
        ),
        position='left',
    ),  # tabbed
)  # docked

windows = []

tools = [
    tool('Report NICOS bug or request enhancement',
         'nicos.clients.gui.tools.bugreport.BugreportTool'),
]

options = {
    'facility': 'ess',
    'mainwindow_class': 'nicos.clients.flowui.mainwindow.MainWindow',
}
