#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2013 by the NICOS contributors (see AUTHORS)
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
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI experiment setup panel tab for SANS1-samplechanger with n positions."""

from PyQt4.QtGui import QDialogButtonBox, QLabel, QPixmap, QTableWidget, \
        QAbstractButton, QStylePainter, QStyleOptionHeader, QStyle, QLineEdit,\
        QAbstractItemView
from PyQt4.QtCore import SIGNAL, QString, Qt, QSize, QEvent

from nicos.core import ProgrammingError
from nicos.clients.gui.utils import decodeAny
from nicos.clients.gui.panels import CustomButtonPanel

class TableWidget(QTableWidget):
    """Fancy QTableWidget with settable CornerButtonWidget by AL"""
    def __init__(self, parent=None):
        QTableWidget.__init__(self, parent)

        self._cornerText = ''

        self._cornerButton = self.findChildren(QAbstractButton)[0]
        self._cornerButton.installEventFilter(self)

        self.setSelectionMode(QAbstractItemView.NoSelection)

    def setCornerLabel(self, text):
        self._cornerText = text

        opt = QStyleOptionHeader()
        opt.text = text
        size = self._cornerButton.style().sizeFromContents(
            QStyle.CT_HeaderSection, opt, QSize(), self._cornerButton)
        self.verticalHeader().setMinimumWidth(size.width())

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Paint and obj == self._cornerButton:
            opt = QStyleOptionHeader()
            opt.init(obj)

            opt.text = self._cornerText
            opt.rect = self._cornerButton.rect()

            painter = QStylePainter(obj)
            painter.drawControl(QStyle.CE_Header, opt)
            return True
        return False


class SamplechangerSetupPanel(CustomButtonPanel):
    """Panel for samplechangers.

    Accept two keyword options in defconfig.py:
    positions   - integer number of sample slots available, defaults to 11
    samplechanger - name of the main samplechanger device (must be Moveable or
                    DeviceAlias)
    """
    # this needs to be unique!
    panelName = 'Samplechanger setup'

    _numSamples = 0

    def __init__(self, parent, client):
        CustomButtonPanel.__init__(self, parent, client,
                                     buttons=QDialogButtonBox.Close | \
                                             QDialogButtonBox.Apply | \
                                             QDialogButtonBox.Ok)
        # our content is a simple widget ...
        self._tableWidget = TableWidget(self.scrollArea)

        self._tableWidget.setColumnCount(1)
        self._tableWidget.setHorizontalHeaderLabels(['Sample name'])
        self._tableWidget.horizontalHeaderItem(0).setTextAlignment(
                            Qt.AlignLeft | Qt.AlignVCenter)
        self._tableWidget.setSortingEnabled(False)
        self._tableWidget.setCornerLabel('Position')

        self.scrollArea.setWidget(self._tableWidget)  # needed!

        if self.client.connected:
            self.on_client_connected()
        self.connect(self.client, SIGNAL('connected'), self.on_client_connected)

    def setOptions(self, options):
        # this should be called only once!
        if self._numSamples:
            raise ProgrammingError('setOptions is supposed to be called ONCE!')

        # self._changerDeviceName = options.get('samplechanger', 'SampleChanger')

        image = options.get('image', None)
        # insert the optional image at top...
        if image:
            l = QLabel(self)
            l.setText(QString(image))
            # insert above scrollArea
            self.vBoxLayout.insertWidget(0, l, alignment=Qt.AlignHCenter)
            p = QPixmap()
            if p.load(image):
                l.setPixmap(p)
            else:
                self.showError('Loading of Image %r failed:' % image)


        self._numSamples = int(options.get('positions', 11))
        self._tableWidget.setRowCount(self._numSamples)
        # fill in widgets into grid
        for pos in range(self._numSamples):
            self._tableWidget.setCellWidget(pos, 0, QLineEdit(QString('')))

        self._tableWidget.horizontalHeader().setStretchLastSection(100)
        # now fill in data
        self._update_sample_info()

    def _update_sample_info(self):
        samplenames = self.client.eval('session.experiment.sample.samplenames')
        if not isinstance(samplenames, dict):
            return
        for i in range(self._numSamples):
            samplename = decodeAny(samplenames.get(i + 1, ''))
            self._tableWidget.cellWidget(i, 0).setText(samplename)

    def _applyChanges(self):
        code = ['ClearSamples()']

        for i in range(self._numSamples):
            name = self._tableWidget.cellWidget(i, 0).text().trimmed().toUtf8()
            if not name.isEmpty():
                code.append('SetSample(%d, %r)' % (i + 1, str(name)))

        self.client.tell('queue', '', '\n'.join(code) + '\n')

        if self.client.ask('getstatus')['requests']:
            self.showInfo('Name changes were queued and will be updated\n'
                          'after the currently executed script finished.')

    def on_client_connected(self):
        self._update_sample_info()

    def on_buttonBox_Apply_clicked(self):
        self._applyChanges()
