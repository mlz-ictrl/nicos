#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2017 by the NICOS contributors (see AUTHORS)
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

"""NICOS filesystem dialog classes"""

import fnmatch
from os import path

from PyQt4.QtGui import QFileDialog, QLineEdit, QSortFilterProxyModel

from nicos.core.errors import NicosError


class FileFilterProxyModel(QSortFilterProxyModel):

    _wildcard = None

    def setFilterWildcard(self, wildcard):
        self._wildcard = wildcard


    def filterAcceptsRow(self, row, parent):
        fileModel = self.sourceModel()
        idx = fileModel.index(row, 0, parent)
        if not fileModel or fileModel.isDir(idx):
            return True
        if self._wildcard:
            fname = fileModel.fileName(idx)
            return fnmatch.fnmatch(fname, self._wildcard)
        return True


class FileFilterDialog(QFileDialog):
    """File open dialog supporting using Unix shell-style wildcards."""

    def __init__(self, *args):
        QFileDialog.__init__(self, *args)
        self.setAcceptMode(QFileDialog.AcceptOpen)
        self.setFileMode(QFileDialog.ExistingFiles)
        self.setOption(QFileDialog.DontUseNativeDialog)
        filterproxy = FileFilterProxyModel(self)
        self.setProxyModel(filterproxy)
        child = None  # make pylint happy
        for child in self.children():
            if isinstance(child, QLineEdit):
                break
        else:
            raise NicosError("QLineEdit not found in QFileDialog")
        child.textChanged.connect(filterproxy.setFilterWildcard)
        child.returnPressed.disconnect(self.accept)
        child.returnPressed.connect(self.on_returnPressed)

    def refresh(self):
        self.selectNameFilter(self.selectedNameFilter())  # force update

    def on_returnPressed(self):
        if any(path.isfile(fn) for fn in self.selectedFiles()):
            self.accept()
        else:
            self.refresh()  # apply wildcard filter
