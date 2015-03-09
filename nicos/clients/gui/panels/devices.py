#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the FRM-II
# Copyright (c) 2009-2015 by the NICOS contributors (see AUTHORS)
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

from logging import WARNING

from PyQt4.QtGui import QIcon, QBrush, QColor, QFont, QTreeWidgetItem, QMenu, \
    QInputDialog, QDialogButtonBox, QPalette, QTreeWidgetItemIterator, \
    QDialog, QMessageBox, QPushButton
from PyQt4.QtCore import SIGNAL, Qt, pyqtSignature as qtsig, QRegExp, \
    QByteArray

from nicos.core.status import OK, WARN, BUSY, ERROR, NOTREACHED, UNKNOWN
from nicos.guisupport.typedvalue import DeviceValueEdit, DeviceParamEdit, \
    DeviceComboWidget
from nicos.clients.gui.dialogs.error import ErrorDialog
from nicos.clients.gui.panels import Panel, showPanel
from nicos.clients.gui.utils import loadUi, dialogFromUi
from nicos.protocols.cache import cache_load, cache_dump, OP_TELL
from nicos.pycompat import iteritems


foregroundBrush = {
    OK:         QBrush(QColor('#00aa00')),
    WARN:       QBrush(Qt.black),
    BUSY:       QBrush(Qt.black),
    UNKNOWN:    QBrush(QColor('#cccccc')),
    ERROR:      QBrush(Qt.black),
    NOTREACHED: QBrush(Qt.black),
}

backgroundBrush = {
    OK:         QBrush(),
    WARN:       QBrush(QColor('#ffa500')),
    BUSY:       QBrush(Qt.yellow),
    UNKNOWN:    QBrush(),
    ERROR:      QBrush(QColor('#ff6655')),
    NOTREACHED: QBrush(QColor('#ff6655')),
}

statusIcon = {
    OK:         QIcon(':/leds/status_green'),
    WARN:       QIcon(':/leds/status_warn'),
    BUSY:       QIcon(':/leds/status_yellow'),
    UNKNOWN:    QIcon(':/leds/status_white'),
    ERROR:      QIcon(':/leds/status_red'),
    NOTREACHED: QIcon(':/leds/status_red'),
}

fixedBrush = {
    False:      QBrush(),
    True:       QBrush(Qt.blue),
}

expiredBrush = {
    False:      QBrush(Qt.black),
    True:       QBrush(QColor('#aaaaaa')),
}

lowlevelBrush = {
    False:      QBrush(Qt.black),
    True:       QBrush(QColor('#666666')),
}

lowlevelFont = {
    False:      QFont(),
    True:       QFont(QFont().family(), -1, -1, True),
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
        self.useicons = True

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
        self.devmenu.addAction(self.actionPlotHistory)
        self.devmenu.addSeparator()
        self.devmenu.addAction(self.actionHelp)

        self.devmenu_ro = QMenu(self)
        self.devmenu_ro.addAction(self.actionMove)
        self.devmenu_ro.addAction(self.actionReset)
        self.devmenu_ro.addSeparator()
        self.devmenu_ro.addAction(self.actionPlotHistory)
        self.devmenu_ro.addSeparator()
        self.devmenu_ro.addAction(self.actionHelp)

        self._menu_dev = None   # device for which context menu is shown
        self._dev2setup = {}

        self._control_dialogs = {}
        self._show_lowlevel = self.mainwindow.expertmode

        # daemon request number of last command executed from this panel
        # (used to display messages from this command)
        self._exec_reqno = -1
        self._error_window = None

        if client.connected:
            self.on_client_connected()
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('disconnected'), self.on_client_disconnected)
        self.connect(client, SIGNAL('cache'), self.on_client_cache)
        self.connect(client, SIGNAL('device'), self.on_client_device)
        self.connect(client, SIGNAL('message'), self.on_client_message)

    def setOptions(self, options):
        self.useicons = bool(options.get('icons', True))

    def saveSettings(self, settings):
        settings.setValue('headers', self.tree.header().saveState())

    def loadSettings(self, settings):
        self._headerstate = settings.value('headers', b'', QByteArray)

    def hideTitle(self):
        self.titleLbl.setVisible(False)

    def setExpertMode(self, expert):
        self._show_lowlevel = expert
        self.on_client_connected()

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
        if not state:
            return
        devlist = state['devices']
        self._read_setup_info(state)

        for devname in devlist:
            self._create_device_item(devname)

        # add all toplevel items to the tree, sorted
        for cat in self._catitems:
            self.tree.addTopLevelItem(self._catitems[cat])
            self._catitems[cat].setExpanded(True)
        self.tree.sortItems(0, Qt.AscendingOrder)

    def on_client_disconnected(self):
        self.clear()

    def on_client_message(self, message):
        # show warnings and errors emitted by the current command in a window
        if len(message) < 7 or message[6] != self._exec_reqno or \
           message[2] < WARNING:
            return
        msg = '%s: %s' % (message[0], message[3].strip())
        if self._error_window is None:
            def reset_errorwindow():
                self._error_window = None
            self._error_window = ErrorDialog(self)
            self._error_window.accepted.connect(reset_errorwindow)
            self._error_window.addMessage(msg)
            self._error_window.show()
        else:
            self._error_window.addMessage(msg)
            self._error_window.activateWindow()

    def _read_setup_info(self, state=None):
        if state is None:
            state = self.client.ask('getstatus')
        loaded_setups = set(state['setups'][0])
        self._dev2setup = {}
        setupinfo = self.client.eval('session.getSetupInfo()', {})
        for setupname, info in iteritems(setupinfo):
            if info is None:
                continue
            if setupname not in loaded_setups:
                continue
            #setupname = key.split('/')[1]
            for devname in info['devices']:
                self._dev2setup[devname] = setupname

    def _create_device_item(self, devname, add_cat=False):
        ldevname = devname.lower()
        # get all cache keys pertaining to the device
        params = self.client.getDeviceParams(devname)
        if not params:
            return
        lowlevel_device = params.get('lowlevel') or False
        if lowlevel_device and not self._show_lowlevel:
            return
        if 'nicos.core.data.DataSink' in params.get('classes', []):
            return
        if 'nicos.core.image.ImageSink' in params.get('classes', []):
            return

        # remove still-existing previous item for the same device name
        if ldevname in self._devitems:
            self.on_client_device(('destroy', [devname]))

        cat = self._dev2setup.get(devname)
        if cat is None:   # device is not in any setup? reread setup info
            self._read_setup_info()
            cat = self._dev2setup.get(devname)
            if cat is None:  # still not there -> give up
                return

        if cat not in self._catitems:
            catitem = QTreeWidgetItem([cat, '', ''], 1000)
            f = catitem.font(0)
            f.setBold(True)
            catitem.setFont(0, f)
            catitem.setIcon(0, QIcon(':/setup'))
            self._catitems[cat] = catitem
            if add_cat:
                self.tree.addTopLevelItem(catitem)
                catitem.setExpanded(True)
        else:
            catitem = self._catitems[cat]

        # create a tree node for the device
        devitem = QTreeWidgetItem(catitem, [devname, '', ''], 1001)

        devitem.setForeground(0, lowlevelBrush[lowlevel_device])
        devitem.setFont(0, lowlevelFont[lowlevel_device])

        if self.useicons:
            devitem.setIcon(0, statusIcon[OK])
        devitem.setToolTip(0, params.get('description', ''))
        self._devitems[ldevname] = devitem
        # fill the device info with dummy values, will be populated below
        self._devinfo[ldevname] = ['-', (OK, ''), '%s', '', '', []]

        # let the cache handler process all properties
        for key, value in iteritems(params):
            self.on_client_cache((None, ldevname + '/' + key, OP_TELL,
                                  cache_dump(value)))

    def on_client_device(self, data):
        (action, devlist) = data
        if not devlist:
            return
        if action == 'create':
            for devname in devlist:
                self._create_device_item(devname, add_cat=True)
            self.tree.sortItems(0, Qt.AscendingOrder)
        elif action == 'destroy':
            for devname in devlist:
                if devname.lower() in self._devitems:
                    # remove device item...
                    item = self._devitems[devname.lower()]
                    del self._devitems[devname.lower()]
                    del self._devinfo[devname.lower()]
                    try:
                        catitem = item.parent()
                    except RuntimeError:
                        # Qt object has already been destroyed
                        pass
                    else:
                        catitem.removeChild(item)
                        # and remove category item if it has no further children
                        if catitem.childCount() == 0:
                            self.tree.takeTopLevelItem(
                                self.tree.indexOfTopLevelItem(catitem))
                            del self._catitems[catitem.text(0)]

    def on_client_cache(self, data):
        (_time, key, op, value) = data
        if '/' not in key:
            return
        ldevname, subkey = key.split('/')
        if ldevname not in self._devinfo:
            return
        if ldevname in self._control_dialogs:
            self._control_dialogs[ldevname].on_cache(subkey, value)
        devitem = self._devitems[ldevname]
        devinfo = self._devinfo[ldevname]
        if subkey == 'value':
            if not value:
                fvalue = ''
            else:
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
            devitem.setForeground(1, expiredBrush[op != OP_TELL])
        elif subkey == 'status':
            if not value:
                status = (UNKNOWN, '?')
            else:
                status = cache_load(value)
            devinfo[1] = status
            devitem.setText(2, status[1])
            if status[0] not in statusIcon:
                # old or wrong status constant
                return
            if self.useicons:
                devitem.setIcon(0, statusIcon[status[0]])
                devitem.setForeground(2, foregroundBrush[status[0]])
                devitem.setBackground(2, backgroundBrush[status[0]])
            else:
                devitem.setForeground(0, foregroundBrush[BUSY])
                devitem.setBackground(0, backgroundBrush[status[0]])
            if ldevname in self._control_dialogs:
                dlg = self._control_dialogs[ldevname]
                dlg.statuslabel.setText(status[1])
                dlg.statusimage.setPixmap(statusIcon[status[0]].pixmap(16, 16))
                setForegroundBrush(dlg.statuslabel, foregroundBrush[status[0]])
                setBackgroundBrush(dlg.statuslabel, backgroundBrush[status[0]])
        elif subkey == 'fmtstr':
            if not value:
                return
            devinfo[2] = cache_load(value)
            try:
                fmted = devinfo[2] % devinfo[0]
            except Exception:
                fmted = str(devinfo[0])
            devitem.setText(1, fmted + ' ' + devinfo[3])
        elif subkey == 'unit':
            if not value:
                value = "''"
            devinfo[3] = cache_load(value)
            try:
                fmted = devinfo[2] % devinfo[0]
            except Exception:
                fmted = str(devinfo[0])
            devitem.setText(1, fmted + ' ' + devinfo[3])
        elif subkey == 'fixed':
            if not value:
                value = "''"
            devinfo[4] = bool(cache_load(value))
            devitem.setForeground(1, fixedBrush[devinfo[4]])
            if ldevname in self._control_dialogs:
                dlg = self._control_dialogs[ldevname]
                if dlg.moveBtn:
                    dlg.moveBtn.setEnabled(not devinfo[4])
                    dlg.moveBtn.setText(devinfo[4] and '(fixed)' or 'Move')
        elif subkey == 'userlimits':
            if not value:
                return
            value = cache_load(value)
            if ldevname in self._control_dialogs:
                dlg = self._control_dialogs[ldevname]
                dlg.limitMin.setText(str(value[0]))
                dlg.limitMax.setText(str(value[1]))
        elif subkey == 'classes':
            if not value:
                value = "[]"
            devinfo[5] = set(cache_load(value))
        elif subkey == 'alias':
            if not value:
                return
            if ldevname in self._control_dialogs:
                dlg = self._control_dialogs[ldevname]
                dlg._reinit()

    def on_tree_customContextMenuRequested(self, point):
        item = self.tree.itemAt(point)
        if item is None:
            return
        if item.type() == 1001:
            self._menu_dev = item.text(0)
            ldevname = self._menu_dev.lower()
            if 'nicos.core.device.Moveable' in self._devinfo[ldevname][5]:
                self.devmenu.popup(self.tree.viewport().mapToGlobal(point))
            elif 'nicos.core.device.Readable' in self._devinfo[ldevname][5]:
                self.devmenu_ro.popup(self.tree.viewport().mapToGlobal(point))

    def on_filter_textChanged(self, text):
        rx = QRegExp(text)
        # QTreeWidgetItemIterator: an ugly Qt C++ API translated to an even
        # uglier Python API...
        it = QTreeWidgetItemIterator(self.tree,
                                     QTreeWidgetItemIterator.NoChildren)
        while it.value():
            it.value().setHidden(rx.indexIn(it.value().text(0)) == -1)
            it += 1
        it = QTreeWidgetItemIterator(self.tree,
                                     QTreeWidgetItemIterator.HasChildren)
        while it.value():
            item = it.value()
            item.setHidden(not any(not item.child(i).isHidden()
                                   for i in range(item.childCount())))
            it += 1

    @qtsig('')
    def on_actionReset_triggered(self):
        if self._menu_dev:
            self.exec_command('reset(%s)' % self._menu_dev, self._menu_dev)

    @qtsig('')
    def on_actionFix_triggered(self):
        if self._menu_dev:
            reason, ok = QInputDialog.getText(self, 'Fix',
                'Please enter the reason for fixing %s:' % self._menu_dev)
            if not ok:
                return
            self.exec_command('fix(%s, %r)' % (self._menu_dev, reason),
                              self._menu_dev)

    @qtsig('')
    def on_actionRelease_triggered(self):
        if self._menu_dev:
            self.exec_command('release(%s)' % self._menu_dev, self._menu_dev)

    @qtsig('')
    def on_actionStop_triggered(self):
        if self._menu_dev:
            self.exec_command('stop(%s)' % self._menu_dev, self._menu_dev,
                              immediate=True)

    @qtsig('')
    def on_actionMove_triggered(self):
        if self._menu_dev:
            self._open_control_dialog(self._menu_dev)

    @qtsig('')
    def on_actionHelp_triggered(self):
        if self._menu_dev:
            self.exec_command('help(%s)' % self._menu_dev, self._menu_dev,
                              immediate=True)

    @qtsig('')
    def on_actionPlotHistory_triggered(self):
        if self._menu_dev:
            self.plot_history(self._menu_dev)

    def on_tree_itemActivated(self, item, column):
        if item.type() != 1001:
            return
        devname = item.text(0)
        self._open_control_dialog(devname)

    def _open_control_dialog(self, devname):
        ldevname = devname.lower()
        if ldevname in self._control_dialogs:
            if self._control_dialogs[ldevname].isVisible():
                self._control_dialogs[ldevname].activateWindow()
                return
        devinfo = self._devinfo[ldevname]
        item = self._devitems[ldevname]
        dlg = ControlDialog(self, devname, devinfo, item, self.log)
        self.connect(dlg, SIGNAL('closed'), self._control_dialog_closed)
        self.connect(dlg, SIGNAL('rejected()'), dlg.close)
        self._control_dialogs[ldevname] = dlg
        dlg.show()

    def _control_dialog_closed(self, ldevname):
        dlg = self._control_dialogs.pop(ldevname)
        dlg.deleteLater()

    # API shared with ControlDialog

    def exec_command(self, command, needed_dev, immediate=False):
        if needed_dev not in self.client.getDeviceList():
            command = 'CreateDevice(%r)\n' % needed_dev + command
        if immediate:
            self.client.tell('exec', command)
            self._exec_reqno = -1  # no request assigned to this command
        else:
            self._exec_reqno = self.client.run(command)

    def plot_history(self, dev):
        if self.mainwindow.history_wintype:
            win = self.mainwindow.createWindow(self.mainwindow.history_wintype)
            panel = win.getPanel('History viewer')
            panel.newView(dev)
            showPanel(panel)


class ControlDialog(QDialog):
    """Dialog opened to control and view details for one device."""

    def __init__(self, parent, devname, devinfo, devitem, log):
        QDialog.__init__(self, parent)
        loadUi(self, 'devices_one.ui', 'panels')
        self.log = log

        self.device_panel = parent
        self.client = parent.client
        self.devname = devname
        self.devinfo = devinfo
        self.devitem = devitem
        self.paramItems = {}

        self._reinit()

    def _reinit(self):
        classes = self.devinfo[5]

        self.deviceName.setText('Device: %s' % self.devname)
        self.setWindowTitle('Control %s' % self.devname)
        self.buttonBox.clear()
        self.buttonBox.setStandardButtons(QDialogButtonBox.Close)

        # now get all cache keys pertaining to the device and set the
        # properties we want
        params = self.client.getDeviceParams(self.devname)
        self.paraminfo = self.client.getDeviceParamInfo(self.devname)
        self.paramvalues = dict(params)

        # put parameter values in the list widget
        self.paramList.clear()
        for key, value in sorted(iteritems(params)):
            if self.paraminfo.get(key):
                # normally, show only userparams, except in expert mode
                is_userparam = self.paraminfo[key]['userparam']
                if is_userparam or self.device_panel._show_lowlevel:
                    self.paramItems[key] = item = \
                        QTreeWidgetItem(self.paramList, [key, str(value)])
                    # display non-userparams in grey italics, like lowlevel
                    # devices in the device list
                    if not is_userparam:
                        item.setFont(0, lowlevelFont[True])
                        item.setForeground(0, lowlevelBrush[True])

        # set description label
        if params.get('description'):
            self.description.setText(params['description'])
        else:
            self.description.setVisible(False)

        # show "Set alias" group box if it is an alias device
        if 'alias' in params:
            if params['alias']:
                self.deviceName.setText(self.deviceName.text() +
                                        ' (alias for %s)' % params['alias'])

            needs_class = params.get('devclass', 'nicos.core.device.Device')
            # backwards compatibility
            if needs_class == 'nicos.core.Device':
                needs_class = 'nicos.core.device.Device'
            self.aliasTarget = DeviceComboWidget(
                self, params['alias'] or '', self.client, needs_class)
            self.targetLayoutAlias.takeAt(1).widget().deleteLater()
            self.targetLayoutAlias.insertWidget(1, self.aliasTarget)
        else:
            self.aliasGroup.setVisible(False)

        # show current value/status if it is readable
        if 'nicos.core.device.Readable' not in classes:
            self.valueFrame.setVisible(False)
        else:
            self.valuelabel.setText(self.devitem.text(1))
            self.statuslabel.setText(self.devitem.text(2))
            self.statusimage.setPixmap(self.devitem.icon(0).pixmap(16, 16))
            setForegroundBrush(self.statuslabel, self.devitem.foreground(2))
            setBackgroundBrush(self.statuslabel, self.devitem.background(2))

            # add a button to the bottom button-box
            historyBtn = QPushButton(QIcon(':/find'), 'Plot history...', self)
            self.buttonBox.addButton(historyBtn, QDialogButtonBox.ResetRole)
            historyBtn.clicked.connect(self.on_historyBtn_clicked)

        # show a "Control" group box if it is moveable
        if 'nicos.core.device.Moveable' not in classes:
            self.controlGroup.setVisible(False)
        else:
            if 'nicos.core.mixins.HasLimits' not in classes:
                self.limitFrame.setVisible(False)
            else:
                self.limitMin.setText(str(params['userlimits'][0]))
                self.limitMax.setText(str(params['userlimits'][1]))

            # insert a widget to enter a new device value
            self.target = DeviceValueEdit(self, dev=self.devname, useButtons=True)
            self.target.setClient(self.client)
            def btn_callback(target):
                self.device_panel.exec_command(
                    'move(%s, %r)' % (self.devname, target), self.devname)
            self.connect(self.target, SIGNAL('valueChosen'), btn_callback)
            self.targetLayout.takeAt(1).widget().deleteLater()
            self.targetLayout.insertWidget(1, self.target)

            # add a menu for the "More" button
            menu = QMenu(self)
            if 'nicos.core.mixins.HasLimits' in classes:
                menu.addAction(self.actionSetLimits)
            if 'nicos.core.mixins.HasOffset' in classes:
                menu.addAction(self.actionAdjustOffset)
            if 'nicos.devices.abstract.CanReference' in classes:
                menu.addAction(self.actionReference)
            menu.addAction(self.actionFix)
            menu.addAction(self.actionRelease)
            menuBtn = QPushButton('More', self)
            menuBtn.setMenu(menu)
            self.moveBtns.clear()
            self.moveBtns.addButton(menuBtn, QDialogButtonBox.ResetRole)

            self.moveBtns.addButton('Reset', QDialogButtonBox.ResetRole)
            self.moveBtns.addButton('Stop', QDialogButtonBox.ResetRole)
            if self.target.getValue() is not None:  # it's None for button widget
                self.moveBtn = self.moveBtns.addButton(
                    'Move', QDialogButtonBox.AcceptRole)
            else:
                self.moveBtn = None

            if params.get('fixed') and self.moveBtn:
                self.moveBtn.setEnabled(False)
                self.moveBtn.setText('(fixed)')

            def callback(button):
                if button.text() == 'Reset':
                    self.device_panel.exec_command('reset(%s)' % self.devname,
                                                   self.devname)
                elif button.text() == 'Stop':
                    self.device_panel.exec_command('stop(%s)' % self.devname,
                                                   self.devname, immediate=True)
                elif button.text() == 'Move':
                    try:
                        target = self.target.getValue()
                    except ValueError:
                        return
                    self.device_panel.exec_command(
                        'move(%s, %r)' % (self.devname, target), self.devname)
            self.moveBtns.clicked.connect(callback)

    @qtsig('')
    def on_actionSetLimits_triggered(self):
        dlg = QDialog(self)
        loadUi(dlg, 'devices_limits.ui', 'panels')
        dlg.descLabel.setText('Adjust user limits of %s:' % self.devname)
        dlg.limitMin.setText(self.limitMin.text())
        dlg.limitMax.setText(self.limitMax.text())
        abslimits = self.client.getDeviceParam(self.devname, 'abslimits')
        offset = self.client.getDeviceParam(self.devname, 'offset')
        if offset is not None:
            abslimits = abslimits[0] - offset, abslimits[1] - offset
        dlg.limitMinAbs.setText(str(abslimits[0]))
        dlg.limitMaxAbs.setText(str(abslimits[1]))
        target = DeviceParamEdit(dlg, dev=self.devname, param='userlimits')
        target.setClient(self.client)
        btn = dlg.buttonBox.addButton('Reset to maximum range',
                                      QDialogButtonBox.ResetRole)
        def callback():
            self.device_panel.exec_command(
                'resetlimits(%s)' % self.devname, self.devname)
            dlg.reject()
        btn.clicked.connect(callback)
        dlg.targetLayout.addWidget(target)
        res = dlg.exec_()
        if res != QDialog.Accepted:
            return
        newlimits = target.getValue()
        if newlimits[0] < abslimits[0] or newlimits[1] > abslimits[1]:
            QMessageBox.warning(self, 'Error', 'The entered limits are not '
                                'within the absolute limits for the device.')
            # retry
            self.on_actionSetLimits_triggered()
            return
        self.device_panel.exec_command('%s.userlimits = %s' %
                                       (self.devname, newlimits), self.devname)

    @qtsig('')
    def on_actionAdjustOffset_triggered(self):
        dlg = QDialog(self)
        loadUi(dlg, 'devices_adjust.ui', 'panels')
        dlg.descLabel.setText('Adjust offset of %s:' % self.devname)
        dlg.oldValue.setText(self.valuelabel.text())
        target = DeviceValueEdit(dlg, dev=self.devname)
        target.setClient(self.client)
        dlg.targetLayout.addWidget(target)
        res = dlg.exec_()
        if res != QDialog.Accepted:
            return
        self.device_panel.exec_command(
            'adjust(%s, %r)' % (self.devname, target.getValue()), self.devname)

    @qtsig('')
    def on_actionReference_triggered(self):
        self.client.run('reference(%s)' % self.devname)

    @qtsig('')
    def on_actionFix_triggered(self):
        reason, ok = QInputDialog.getText(self, 'Fix',
            'Please enter the reason for fixing %s:' % self.devname)
        if not ok:
            return
        self.device_panel.exec_command('fix(%s, %r)' % (self.devname, reason),
                                       self.devname)

    @qtsig('')
    def on_actionRelease_triggered(self):
        self.device_panel.exec_command('release(%s)' % self.devname,
                                       self.devname)

    @qtsig('')
    def on_setAliasBtn_clicked(self):
        self.device_panel.exec_command(
            '%s.alias = %r' % (self.devname, self.aliasTarget.getValue()),
            self.devname)

    def closeEvent(self, event):
        event.accept()
        self.emit(SIGNAL('closed'), self.devname.lower())

    def on_cache(self, subkey, value):
        if subkey not in self.paramItems:
            return
        if not value:
            return
        value = cache_load(value)
        self.paramvalues[subkey] = value
        self.paramItems[subkey].setText(1, str(value))

    def on_paramList_itemClicked(self, item):
        pname = item.text(0)
        if not self.paraminfo[pname]['settable']:
            return
        mainunit = self.paramvalues.get('unit', 'main')
        punit = (self.paraminfo[pname]['unit'] or '').replace('main', mainunit)

        dlg = dialogFromUi(self, 'devices_param.ui', 'panels')
        dlg.target = DeviceParamEdit(self, dev=self.devname, param=pname)
        dlg.target.setClient(self.client)
        dlg.paramName.setText('Parameter: %s.%s' % (self.devname, pname))
        dlg.paramDesc.setText(self.paraminfo[pname]['description'])
        dlg.paramValue.setText(str(self.paramvalues[pname]) + ' ' + punit)
        dlg.targetLayout.addWidget(dlg.target)
        dlg.resize(dlg.sizeHint())
        dlg.target.setFocus()
        if dlg.exec_() != QDialog.Accepted:
            return
        try:
            new_value = dlg.target.getValue()
        except ValueError:
            self.log.exception('invalid value for typed value')
            # shouldn't happen, but if it does, at least give an indication that
            # something went wrong
            QMessageBox.warning(self, 'Error', 'The entered value is invalid '
                                'for this parameter.')
            return
        self.device_panel.exec_command(
            '%s.%s = %r' % (self.devname, pname, new_value), self.devname)

    def on_historyBtn_clicked(self):
        self.device_panel.plot_history(self.devname)
