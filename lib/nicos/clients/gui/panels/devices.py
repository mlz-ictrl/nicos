#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2012 by the NICOS contributors (see AUTHORS)
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

"""NICOS GUI panel with a list of all devices."""

from __future__ import with_statement

__version__ = "$Revision$"

from PyQt4.QtCore import SIGNAL, Qt, pyqtSignature as qtsig
from PyQt4.QtGui import QIcon, QBrush, QColor, QTreeWidgetItem, QMenu, \
     QInputDialog, QDialogButtonBox, QPalette, QDoubleValidator

from nicos.core.status import OK, BUSY, PAUSED, ERROR, NOTREACHED, UNKNOWN
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, dialogFromUi
from nicos.protocols.cache import cache_load, cache_dump


foregroundBrush = {
    OK:         QBrush(QColor('#00aa00')),
    BUSY:       QBrush(Qt.black),
    PAUSED:     QBrush(Qt.black),
    UNKNOWN:    QBrush(QColor('#cccccc')),
    ERROR:      QBrush(Qt.black),
    NOTREACHED: QBrush(Qt.black),
}

backgroundBrush = {
    OK:         QBrush(),
    BUSY:       QBrush(Qt.yellow),
    PAUSED:     QBrush(Qt.yellow),
    UNKNOWN:    QBrush(),
    ERROR:      QBrush(Qt.red),
    NOTREACHED: QBrush(Qt.red),
}

fixedBrush = {
    False:      QBrush(),
    True:       QBrush(Qt.blue),
}


def setBackgroundBrush(widget, color):
    palette = widget.palette()
    palette.setBrush(QPalette.Window, color)
    widget.setBackgroundRole(QPalette.Window)
    widget.setPalette(palette)


def setForegroundBrush(widget, color):
    palette = widget.palette()
    palette.setBrush(QPalette.WindowText, color)
    widget.setForegroundRole(QPalette.WindowText)
    widget.setPalette(palette)


class DevicesPanel(Panel):
    panelName = 'Devices'

    def __init__(self, parent, client):
        Panel.__init__(self, parent, client)
        loadUi(self, 'devices.ui', 'panels')

        self.tree.header().restoreState(self._headerstate)
        self.clear()

        self.devmenu = QMenu(self)
        self.devmenu.addAction(self.actionMove)
        self.devmenu.addAction(self.actionStop)
        self.devmenu.addAction(self.actionReset)
        self.devmenu.addSeparator()
        self.devmenu.addAction(self.actionFix)
        self.devmenu.addAction(self.actionRelease)
        self.devmenu.addSeparator()
        self.devmenu.addAction(self.actionHelp)

        self.devmenu_ro = QMenu(self)
        self.devmenu_ro.addAction(self.actionReset)
        self.devmenu_ro.addSeparator()
        self.devmenu_ro.addAction(self.actionHelp)

        self.parmenu = QMenu(self)
        self.parmenu.addAction(self.actionChangePar)

        self._menu_dev = None   # device for which context menu is shown
        self._menu_par = None

        self._control_dialogs = {}

        if client.connected:
            self.on_client_connected()
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('cache'), self.on_client_cache)
        self.connect(client, SIGNAL('device'), self.on_client_device)

    def saveSettings(self, settings):
        settings.setValue('headers', self.tree.header().saveState())

    def loadSettings(self, settings):
        self._headerstate = settings.value('headers').toByteArray()

    def clear(self):
        self._catitems = {}
        # map lowercased devname -> tree widget item
        self._devitems = {}
        # map lowercased devname -> [value, status, fmtstr, unit, fixed]
        self._devinfo = {}
        self.tree.clear()

    def on_client_connected(self):
        self.clear()

        state = self.client.ask('getstatus')
        devlist = sorted(state['devices'])
        self._read_setup_info(state)

        for devname in devlist:
            self._create_device_item(devname)

        # add all toplevel items to the tree, sorted
        for cat in sorted(self._catitems):
            self.tree.addTopLevelItem(self._catitems[cat])
            self._catitems[cat].setExpanded(True)

    def _read_setup_info(self, state=None):
        if state is None:
            state = self.client.ask('getstatus')
        loaded_setups = set(state['setups'][0])
        self._dev2setup = {}
        #setupinfo = self.client.ask('getcachekeys', '_setupinfo_/')
        setupinfo = self.client.eval('session.getSetupInfo()', {})
        for setupname, value in setupinfo.iteritems():
            if setupname not in loaded_setups:
                continue
            #setupname = key.split('/')[1]
            for devname in value['devices']:
                self._dev2setup[devname] = setupname

    def _create_device_item(self, devname, add_cat=False):
        ldevname = devname.lower()
        # get all cache keys pertaining to the device
        devkeys = dict(self.client.ask('getcachekeys', ldevname + '/'))
        if devkeys.get(ldevname + '/lowlevel'):
            return

        cat = self._dev2setup.get(devname)
        if cat is None:   # device is not in any setup? reread setup info
            self._read_setup_info()
            cat = self._dev2setup.get(devname)
            if cat is None:  # still not there -> give up
                return

        if cat not in self._catitems:
            catitem = QTreeWidgetItem([cat, '', ''], 1000)
            catitem.setIcon(0, QIcon(':/setup'))
            self._catitems[cat] = catitem
            if add_cat:
                self.tree.addTopLevelItem(catitem)
                catitem.setExpanded(True)
        else:
            catitem = self._catitems[cat]

        # create a tree node for the device
        devitem = QTreeWidgetItem(catitem, [devname, '', ''], 1001)
        devitem.setIcon(0, QIcon(':/sunny'))
        self._devitems[ldevname] = devitem
        # fill the device info with dummy values, will be populated below
        self._devinfo[ldevname] = ['-', (OK, ''), '%s', '', '', []]

        # let the cache handler process all properties
        for key, value in devkeys.iteritems():
            self.on_client_cache((None, key, None, cache_dump(value)))

    def on_client_device(self, (action, devlist)):
        if action == 'create':
            for devname in devlist:
                self._create_device_item(devname, add_cat=True)
            # XXX somehow the device list should be sorted again after
            # inserting elements
        elif action == 'destroy':
            for devname in devlist:
                if devname.lower() in self._devitems:
                    # remove device item...
                    item = self._devitems[devname.lower()]
                    catitem = item.parent()
                    catitem.removeChild(item)
                    del self._devitems[devname.lower()]
                    del self._devinfo[devname.lower()]
                    # and remove category item if it has no further children
                    if catitem.childCount() == 0:
                        self.tree.takeTopLevelItem(
                            self.tree.indexOfTopLevelItem(catitem))
                        del self._catitems[str(catitem.text(0))]

    def on_client_cache(self, (time, key, op, value)):
        ldevname, subkey = key.split('/')
        if ldevname not in self._devinfo:
            return
        devitem = self._devitems[ldevname]
        devinfo = self._devinfo[ldevname]
        if subkey == 'value':
            fvalue = cache_load(value)
            if isinstance(fvalue, list):
                fvalue = tuple(fvalue)
            devinfo[0] = fvalue
            try:
                fmted = devinfo[2] % fvalue
            except Exception:
                fmted = str(fvalue)
            devitem.setText(1, fmted + ' ' + devinfo[3])
            if ldevname in self._control_dialogs:
                self._control_dialogs[ldevname].valuelabel.setText(
                    fmted + ' ' + devinfo[3])
        elif subkey == 'status':
            status = cache_load(value)
            devinfo[1] = status
            devitem.setText(2, status[1])
            devitem.setForeground(2, foregroundBrush[status[0]])
            devitem.setBackground(2, backgroundBrush[status[0]])
            if ldevname in self._control_dialogs:
                dlg = self._control_dialogs[ldevname]
                dlg.statuslabel.setText(status[1])
                setForegroundBrush(dlg.statuslabel, foregroundBrush[status[0]])
                setBackgroundBrush(dlg.statuslabel, backgroundBrush[status[0]])
        elif subkey == 'fmtstr':
            devinfo[2] = cache_load(value)
            try:
                fmted = devinfo[2] % devinfo[0]
            except Exception:
                fmted = str(devinfo[0])
            devitem.setText(1, fmted + ' ' + devinfo[3])
        elif subkey == 'unit':
            devinfo[3] = cache_load(value)
            try:
                fmted = devinfo[2] % devinfo[0]
            except Exception:
                fmted = str(devinfo[0])
            devitem.setText(1, fmted + ' ' + devinfo[3])
        elif subkey == 'fixed':
            devinfo[4] = bool(cache_load(value))
            devitem.setForeground(1, fixedBrush[devinfo[4]])
        elif subkey == 'classes':
            devinfo[5] = set(cache_load(value))

    def on_tree_customContextMenuRequested(self, point):
        item = self.tree.itemAt(point)
        if item is None:
            return
        if item.type() == 1001:
            self._menu_dev = str(item.text(0))
            ldevname = self._menu_dev.lower()
            if 'nicos.core.device.Moveable' in self._devinfo[ldevname][5]:
                self.devmenu.popup(self.tree.viewport().mapToGlobal(point))
            elif 'nicos.core.device.Readable' in self._devinfo[ldevname][5]:
                self.devmenu_ro.popup(self.tree.viewport().mapToGlobal(point))

    @qtsig('')
    def on_actionReset_triggered(self):
        if self._menu_dev:
            self.client.tell('queue', '', 'reset(%s)' % self._menu_dev)

    @qtsig('')
    def on_actionFix_triggered(self):
        if self._menu_dev:
            reason, ok = QInputDialog.getText(self, 'Fix',
                'Please enter the reason for fixing %s:' % self._menu_dev)
            if not ok:
                return
            self.client.tell('queue', '', 'fix(%s, %r)' %
                             (self._menu_dev, unicode(reason)))

    @qtsig('')
    def on_actionRelease_triggered(self):
        if self._menu_dev:
            self.client.tell('queue', '', 'release(%s)' % self._menu_dev)

    @qtsig('')
    def on_actionStop_triggered(self):
        if self._menu_dev:
            self.client.tell('exec', 'stop(%s)' % self._menu_dev)

    @qtsig('')
    def on_actionMove_triggered(self):
        if self._menu_dev:
            self._open_control_dialog(self._menu_dev)

    @qtsig('')
    def on_actionHelp_triggered(self):
        if self._menu_dev:
            self.client.tell('exec', 'help(%s)' % self._menu_dev)

    def on_tree_itemActivated(self, item, column):
        if item.type() != 1001:
            return
        devname = str(item.text(0))
        self._open_control_dialog(devname)

    def _open_control_dialog(self, devname):
        ldevname = devname.lower()
        if ldevname in self._control_dialogs:
            if self._control_dialogs[ldevname].isVisible():
                self._control_dialogs[ldevname].activateWindow()
                return

        dlg = dialogFromUi(self, 'devices_one.ui', 'panels')
        self._control_dialogs[ldevname] = dlg
        devinfo = self._devinfo[ldevname]
        dlg.devname.setText('Device: %s' % devname)
        dlg.setWindowTitle('Control %s' % devname)

        # now get all cache keys pertaining to the device and set the
        # properties we want
        params = {}
        devkeys = self.client.ask('getcachekeys', ldevname + '/')
        for key, value in sorted(devkeys):
            param = key.split('/')[1]
            QTreeWidgetItem(dlg.paramList, [param, str(value)])
            params[param] = value

        if 'nicos.core.device.Readable' not in devinfo[5]:
            dlg.valueFrame.setVisible(False)
        else:
            item = self._devitems[ldevname]
            dlg.valuelabel.setText(item.text(1))
            dlg.statuslabel.setText(item.text(2))
            setForegroundBrush(dlg.statuslabel, item.foreground(2))
            setBackgroundBrush(dlg.statuslabel, item.background(2))

        if 'nicos.core.device.Moveable' not in devinfo[5]:
            dlg.controlGroup.setVisible(False)
        else:
            if 'nicos.core.device.HasLimits' not in devinfo[5]:
                dlg.limitFrame.setVisible(False)
            else:
                dlg.limitMin.setText(str(params['userlimits'][0]))
                dlg.limitMax.setText(str(params['userlimits'][1]))
            if 'states' in params:
                dlg.target.setVisible(False)
                dlg.targetUnit.setVisible(False)
                dlg.targetBox.addItems(params['states'])
                is_switcher = True
            elif 'mapping' in params:
                dlg.target.setVisible(False)
                dlg.targetUnit.setVisible(False)
                dlg.targetBox.addItems(params['mapping'].values())
                is_switcher = True
            else:
                dlg.targetBox.setVisible(False)
                dlg.target.setValidator(QDoubleValidator(dlg.target))
                dlg.target.setText(str(params.get('value', '')))
                dlg.targetUnit.setText(params['unit'])
                is_switcher = False
            dlg.moveBtns.addButton('Reset', QDialogButtonBox.ResetRole)
            dlg.moveBtns.addButton('Stop', QDialogButtonBox.ResetRole)
            dlg.moveBtns.addButton('Move', QDialogButtonBox.AcceptRole)
            def callback(button):
                if button.text() == 'Reset':
                    self.client.tell('queue', '', 'reset(%s)' % devname)
                elif button.text() == 'Stop':
                    self.client.tell('exec', 'stop(%s)' % devname)
                elif button.text() == 'Move':
                    if is_switcher:
                        target = '"' + dlg.targetBox.currentText() + '"'
                    else:
                        target = dlg.target.text()
                        if not target:
                            return
                    self.client.tell('queue', '',
                                     'move(%s, %s)' % (devname, target))
            dlg.moveBtns.clicked.connect(callback)

        dlg.show()
