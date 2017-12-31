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
#   Andreas Schulz <andreas.schulz@frm2.tum.de>
#
# *****************************************************************************
"""Classes to adding parameters."""

from os import path

from nicos.guisupport.qt import uic, Qt, QDialog, QListWidgetItem


class AddParameterDialog(QDialog):
    def __init__(self, parameters, existingParameters, parent=None):
        QDialog.__init__(self, parent)
        uic.loadUi(path.abspath(path.join(path.dirname(__file__),
                                          '..',
                                          'ui',
                                          'dialogs',
                                          'addparameterdialog.ui')), self)
        self.lineEditCustomParameter.setHidden(True)
        missingParameters = [key for key in parameters.keys()
                             if key not in existingParameters.keys() and
                             not key.startswith('_')]
        if missingParameters:
            for key in sorted(missingParameters):
                listItem = QListWidgetItem(key, self.listWidgetSelectParameter)
                listItem.setToolTip(parameters[key].description)
                self.listWidgetSelectParameter.addItem(listItem)
        else:
            self.checkBoxCustomParameter.setChecked(True)
            self.checkBoxCustomParameter.setEnabled(False)
            self.lineEditCustomParameter.setEnabled(True)

    def getValue(self):
        if self.checkBoxCustomParameter.checkState() == Qt.Checked:
            return self.lineEditCustomParameter.text()
        else:
            return self.listWidgetSelectParameter.currentItem().text()
