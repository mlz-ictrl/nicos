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
#   Enrico Faulhaber <enrico.faulhaber@frm2.tum.de>
#   Alexander Lenz <alexander.lenz@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI experiment setup panel tab for SANS1 sample changer with *n*
positions.
"""

from __future__ import absolute_import, division, print_function

from nicos.clients.gui.panels import AuxiliaryWindow, Panel
from nicos.clients.gui.panels.tabwidget import DetachedWindow
from nicos.guisupport.qt import QAbstractButton, QAbstractItemView, \
    QDialogButtonBox, QEvent, QLabel, QLineEdit, QPixmap, QSize, QStyle, \
    QStyleOptionHeader, QStylePainter, Qt, QTableWidget, QVBoxLayout
from nicos.pycompat import from_maybe_utf8
from nicos.utils import findResource


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
            opt.initFrom(obj)

            opt.text = self._cornerText
            opt.rect = self._cornerButton.rect()

            painter = QStylePainter(obj)
            painter.drawControl(QStyle.CE_Header, opt)
            return True
        return False


class CustomButtonPanel(Panel):
    """Base class for custom instrument specific panels

    with a QDialogButtonBox at the lower right and some glue magic for
    fancy stuff...
    """
    buttons = QDialogButtonBox.Close | QDialogButtonBox.Apply

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)

        # make a vertical layout for 'ourself'
        self.vBoxLayout = QVBoxLayout(self)

        # make a buttonBox
        self.buttonBox = QDialogButtonBox(self.buttons, parent=self)
        self.buttonBox.setObjectName('buttonBox')

        # put buttonBox below main content
        self.vBoxLayout.addWidget(self.buttonBox)

        allButtons = 'Ok Open Save Cancel Close Discard Apply Reset '\
                     'RestoreDefaults Help SaveAll Yes YesToAll No NoToAll '\
                     'Abort Retry Ignore'.split()
        for btn_name in allButtons:
            btn = self.buttonBox.button(getattr(QDialogButtonBox, btn_name))
            if btn:
                handler = getattr(self, 'on_buttonBox_%s_clicked' % btn_name,
                                  None)
                if not handler:
                    # pylint: disable=function-redefined
                    def handler(self=self, n=btn_name):
                        self.showError('on_buttonBox_%s_clicked not '
                                       'implemented!' % n)
                btn.clicked.connect(handler)

    def panelState(self):
        """returns current window state as obtained from the stack of parents"""
        obj = self
        while hasattr(obj, 'parent'):
            if isinstance(obj, AuxiliaryWindow):
                return "tab"
            elif isinstance(obj, DetachedWindow):
                return "detached"
            obj = obj.parent()
        return "main"

    def on_buttonBox_Close_clicked(self):
        self.closeWindow()

    def on_buttonBox_Ok_clicked(self):
        """OK = Apply + Close"""
        if hasattr(self, 'on_buttonBox_Apply_clicked'):
            self.on_buttonBox_Apply_clicked()
        self.on_buttonBox_Close_clicked()


class SamplechangerSetupPanel(CustomButtonPanel):
    """Panel for samplechangers.

    Accept two keyword options in gui config:
    positions   - integer number of sample slots available, defaults to 11
    samplechanger - name of the main samplechanger device (must be Moveable or
                    DeviceAlias)
    """
    # this needs to be unique!
    panelName = 'Samplechanger setup'
    buttons = (QDialogButtonBox.Close | QDialogButtonBox.Apply | QDialogButtonBox.Ok)

    _numSamples = 0

    def __init__(self, parent, client, options):
        CustomButtonPanel.__init__(self, parent, client, options)
        # our content is a simple widget ...
        self._tableWidget = TableWidget(self)

        self._tableWidget.setColumnCount(1)
        self._tableWidget.setHorizontalHeaderLabels(['Sample name'])
        self._tableWidget.horizontalHeaderItem(0).setTextAlignment(
            Qt.AlignLeft | Qt.AlignVCenter)
        self._tableWidget.setSortingEnabled(False)
        self._tableWidget.setCornerLabel('Position')

        self.vBoxLayout.insertWidget(0, self._tableWidget)

        client.connected.connect(self.on_client_connected)
        client.setup.connect(self.on_client_connected)

        image = options.get('image', None)
        # insert the optional image at top...
        if image:
            l = QLabel(self)
            l.setText(image)
            # insert above scrollArea
            self.vBoxLayout.insertWidget(0, l, alignment=Qt.AlignHCenter)
            p = QPixmap()
            if p.load(findResource(image)):
                l.setPixmap(p)
            else:
                msg = 'Loading of Image %r failed:' % image
                msg += '\n\nCheck GUI config file for %r' % __file__
                self.showError(msg)

        self._numSamples = int(options.get('positions', 11))
        self._tableWidget.setRowCount(self._numSamples)
        # fill in widgets into grid
        for pos in range(self._numSamples):
            self._tableWidget.setCellWidget(pos, 0, QLineEdit(''))

        self._tableWidget.horizontalHeader().setStretchLastSection(100)
        # now fill in data
        self._update_sample_info()

    def _update_sample_info(self):
        names = self.client.eval('Exp.sample.samples', None)
        if names is None:
            return
        for i in range(self._numSamples):
            name = from_maybe_utf8(names.get(i + 1, {}).get('name', ''))
            self._tableWidget.cellWidget(i, 0).setText(name)

    def _applyChanges(self):
        code = ['ClearSamples()']

        for i in range(self._numSamples):
            name = self._tableWidget.cellWidget(i, 0).text().strip()
            if name:
                code.append('SetSample(%d, %r)' % (i + 1, name))

        self.client.run('\n'.join(code) + '\n')

        st = self.client.ask('getstatus')
        if st and st['requests']:
            self.showInfo('Name changes were queued and will be updated\n'
                          'after the currently executed script finished.')

    def on_client_connected(self):
        self._update_sample_info()

    def on_buttonBox_Apply_clicked(self):
        self._applyChanges()
