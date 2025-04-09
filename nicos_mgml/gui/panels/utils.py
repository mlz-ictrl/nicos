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
#   Petr Cermak <cermak@mag.mff.cuni.cz>
#
# *****************************************************************************

"""NICOS MGML GUI misc panels."""

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.panels.generic import GenericPanel
from nicos.guisupport.qt import QLabel, QPixmap, Qt, QVBoxLayout, pyqtSlot
from nicos.utils import findResource

from nicos_mgml.gui import uipath


class ImagePanel(Panel):
    """Simple panel showing image."""

    # this needs to be unique!
    panelName = 'Image panel'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        self.vBoxLayout = QVBoxLayout(self)
        # CustomButtonPanel.__init__(self, parent, client, options)
        image = options.get('image', None)
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


class CryoPanel(GenericPanel):
    """Cryostat panel allowing to fill the helium."""

    # this needs to be unique!
    panelName = 'Cryostat panel'

    def __init__(self, parent, client, options):
        options.update({'uifile': findResource(f'{uipath}/panels/cryostat.ui')})
        GenericPanel.__init__(self, parent, client, options)
        self._reinit()

    def on_client_connected(self):
        GenericPanel.on_client_connected(self)
        self._reinit()

    def _reinit(self, curvalue=None):
        if not self.client or not self.client.isconnected:
            self.startButton.hide()
            self.dataBox.hide()
            return
        if 'Cryostat' in self.client.getDeviceList():
            # check if cryostat is filling
            s = self.client.eval('Cryostat.fillstart', None)
            if s:  # filling
                self.startButton.hide()
                self.dataBox.show()
            else:
                self.startButton.show()
                self.dataBox.hide()

    def on_gasEdit_valueChosen(self, val):
        self.client.run('move("Gas", %r)' % val)

    @pyqtSlot()
    def on_startButton_clicked(self):
        self.gasEdit.valueChosen.emit(self.gasEdit.getValue())
        self.startButton.hide()
        self.dataBox.show()
        self.client.run('Cryostat.StartFill()')

    @pyqtSlot()
    def on_finishButton_clicked(self):
        self.gasEdit.valueChosen.emit(self.gasEdit.getValue())
        try:
            consumed = float(self.consumedHe.text())
        except ValueError:
            self.showError('You need to enter valid number of consumed litres.')
            return
        self.startButton.show()
        self.dataBox.hide()
        self.client.run(f'Cryostat.EndFill({consumed}, "{self.filledBy.text()}")')

    def on_modeOff_clicked(self):
        self.client.run('maw("opmode", "automatic mode")')
