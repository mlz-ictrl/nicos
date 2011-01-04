#  -*- coding: utf-8 -*-
# *****************************************************************************
# Module:
#   $Id$
#
# Description:
#   NICM GUI tools
#
# Author:
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
#   The basic NICOS methods for the NICOS daemon (http://nicos.sf.net)
#
#   Copyright (C) 2009 Jens Krüger <jens.krueger@frm2.tum.de>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# *****************************************************************************

"""NICM GUI tools."""

__author__  = "$Author$"
__date__    = "$Date$"
__version__ = "$Revision$"

from subprocess import Popen, PIPE

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from nicm.gui.tools.proposal import proposal
from nicm.gui.tools.scan import scaninput
from nicm.gui.tools.commands import cmdtool
try:
    from nicm.gui.tools.logviewer import logviewer
except ImportError:
    logviewer = None
try:
    from nicm.gui.tools.calc import calc
except ImportError:
    calc = None

main_tools = [
    logviewer and ('Logfile viewer', 'dialog', logviewer.LogViewer),
    ('Proposal management', 'dialog', proposal.ProposalInput),
    ('Data conversion', 'command',
     '"/data/Mira intern/Instrument/Software/dconv/dconvgui"'),
    calc and ('Calculation helpers', 'dialog', calc.CalcTool),
    ('Maintenance', 'dialog', cmdtool.CmdTool),
]

editor_tools = [
    ('Scan', 'dialog', scaninput.ScanInputDlg),
]


class HasTools(object):
    def addTools(self, toollist, menu, callback):
        for entry in toollist:
            if not entry:
                continue
            name, type, item = entry
            action = QAction(self)
            action.setText(name)
            if type == 'command':
                def slot(cmd=item):
                    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
                    out, err = p.communicate()
                    if p.returncode != 0:
                        QMessageBox.warning(
                            self, self.tr('Tool command'),
                            self.tr('Command failed: %1').arg(err))
                    elif out:
                        callback(out)
            else:
                def slot(cls=item):
                    dlg = cls(self)
                    self.connect(dlg, SIGNAL('commandCreated'), callback)
                    dlg.show()
            self.connect(action, SIGNAL('triggered()'), slot)
            menu.addAction(action)
    
