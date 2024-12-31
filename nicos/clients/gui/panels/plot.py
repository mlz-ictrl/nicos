# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2025 by the NICOS contributors (see AUTHORS)
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
#   Christian Felder <c.felder@fz-juelich.de>
#
# *****************************************************************************

"""NICOS GUI common plot codebase"""

import os
from os import path

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import dialogFromUi
from nicos.guisupport.qt import QDialog


class PlotPanel(Panel):

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        # current plot object
        self.currentPlot = None

    def attachElogDialogExec(self, filename):
        """Opens an attach to elog dialog and executes attach to elog on accept.
        """
        newdlg = dialogFromUi(self, 'panels/plot_attach.ui')
        newdlg.filename.setText(filename)
        ret = newdlg.exec()
        if ret != QDialog.DialogCode.Accepted:
            return
        descr = newdlg.description.text()
        fname = path.splitext(newdlg.filename.text())[0]

        fnames, remotefns, extensions = [], [], []
        for pathname, ext in self.currentPlot.saveQuietly():
            try:
                with open(pathname, 'rb') as fp:
                    remotefn = self.client.ask('transfer', fp.read())
                    if remotefn is not None:
                        remotefns.append(remotefn)
                        extensions.append(ext)
                        fnames.append(fname + ext)
            finally:
                os.unlink(pathname)
        if remotefns:
            self.client.eval(
                '_LogAttachImage(%r, %r, %r, %r)' % (descr, remotefns,
                                                     extensions, fnames)
            )
