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
#   Georg Brandl <georg.brandl@frm2.tum.de>
#
# *****************************************************************************

"""NICOS GUI panel with a list of all devices."""

from PyQt4.QtGui import QIcon, QBrush, QColor, QTreeWidgetItem, QMenu, \
     QInputDialog, QDialogButtonBox, QPalette, QTreeWidgetItemIterator, \
     QDialog, QMessageBox
from PyQt4.QtCore import SIGNAL, Qt, pyqtSignature as qtsig, QRegExp

from nicos.core.status import OK, BUSY, PAUSED, ERROR, NOTREACHED, UNKNOWN
from nicos.guisupport import typedvalue
from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import loadUi, dialogFromUi
from nicos.protocols.cache import cache_load, cache_dump, OP_TELL


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
    ERROR:      QBrush(QColor('#ff6655')),
    NOTREACHED: QBrush(QColor('#ff6655')),
}

statusIcon = {
    OK:         QIcon(':/leds/status_green'),
    BUSY:       QIcon(':/leds/status_yellow'),
    PAUSED:     QIcon(':/leds/status_yellow'),
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
        self.devmenu_ro.addAction(self.actionReset)
        self.devmenu_ro.addSeparator()
        self.devmenu_ro.addAction(self.actionPlotHistory)
        self.devmenu_ro.addSeparator()
        self.devmenu_ro.addAction(self.actionHelp)

        self._menu_dev = None   # device for which context menu is shown
        self._dev2setup = {}

        self._control_dialogs = {}

        if client.connected:
            self.on_client_connected()
        self.connect(client, SIGNAL('connected'), self.on_client_connected)
        self.connect(client, SIGNAL('cache'), self.on_client_cache)
        self.connect(client, SIGNAL('device'), self.on_client_device)

    def setOptions(self, options):
        self.useicons = bool(options.get('icons', True))

    def saveSettings(self, settings):
        settings.setValue('headers', self.tree.header().saveState())

    def loadSettings(self, settings):
        self._headerstate = settings.value('headers').toByteArray()

    def hideTitle(self):
        self.titleLbl.setVisible(False)

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
        setupinfo = self.client.eval('session.getSetupInfo()', {})
        for setupname, info in setupinfo.iteritems():
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
        if params.get('lowlevel'):
            return
        if 'nicos.core.data.DataSink' in params.get('classes', []):
            return

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

        # remove still-existing previous item for the same device name
        if ldevname in self._devitems:
            self.on_client_device(('destroy', [devname]))

        # create a tree node for the device
        devitem = QTreeWidgetItem(catitem, [devname, '', ''], 1001)
        if self.useicons:
            devitem.setIcon(0, statusIcon[OK])
        devitem.setToolTip(0, params.get('description', ''))
        self._devitems[ldevname] = devitem
        # fill the device info with dummy values, will be populated below
        self._devinfo[ldevname] = ['-', (OK, ''), '%s', '', '', [], None, None]

        # let the cache handler process all properties
        for key, value in params.iteritems():
            self.on_client_cache((None, ldevname + '/' + key, OP_TELL,
                                  cache_dump(value)))

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
            if (devinfo[6] is not None and devinfo[0] < devinfo[6]) or \
               (devinfo[7] is not None and devinfo[0] > devinfo[7]):
                devitem.setBackground(1, backgroundBrush[ERROR])
            else:
                devitem.setBackground(1, backgroundBrush[OK])
            devitem.setForeground(1, expiredBrush[op != OP_TELL])
        elif subkey == 'status':
            if not value:
                status = (UNKNOWN, '?')
            else:
                status = cache_load(value)
            devinfo[1] = status
            devitem.setText(2, status[1])
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
                dlg.movebtn.setEnabled(not devinfo[4])
                dlg.movebtn.setText(devinfo[4] and '(fixed)' or 'Move')
        elif subkey == 'warnlimits':
            if not value:
                value = "None"
            value = cache_load(value)
            st = OK
            if value:
                devinfo[6], devinfo[7] = value
                if (devinfo[6] is not None and devinfo[0] < devinfo[6]) or \
                   (devinfo[7] is not None and devinfo[0] > devinfo[7]):
                    st = ERROR
            devitem.setBackground(1, backgroundBrush[st])
        elif subkey == 'classes':
            if not value:
                value = "[]"
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

    @qtsig('')
    def on_actionPlotHistory_triggered(self):
        if self._menu_dev and self.mainwindow.history_wintype:
            win = self.mainwindow.createWindow(self.mainwindow.history_wintype)
            win.getPanel('History viewer').newView(self._menu_dev)

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
        devinfo = self._devinfo[ldevname]
        item = self._devitems[ldevname]
        dlg = ControlDialog(self, devname, devinfo, item, self.log)
        self._control_dialogs[ldevname] = dlg
        dlg.show()


class ControlDialog(QDialog):
    """Dialog opened to control and view details for one device."""

    def __init__(self, parent, devname, devinfo, devitem, log):
        QDialog.__init__(self, parent)
        loadUi(self, 'devices_one.ui', 'panels')
        self.log = log

        self.client = parent.client
        self.devname = devname
        self.paramItems = {}

        self.deviceName.setText('Device: %s' % devname)
        self.setWindowTitle('Control %s' % devname)

        # now get all cache keys pertaining to the device and set the
        # properties we want
        params = self.client.getDeviceParams(devname)
        self.paraminfo = self.client.getDeviceParamInfo(devname)
        self.paramvalues = dict(params)
        for key, value in sorted(params.iteritems()):
            if self.paraminfo.get(key) and self.paraminfo[key]['userparam']:
                self.paramItems[key] = \
                    QTreeWidgetItem(self.paramList, [key, str(value)])

        if params.get('description'):
            self.description.setText(params['description'])
        else:
            self.description.setVisible(False)

        if params.get('alias'):
            self.deviceName.setText(self.deviceName.text() +
                                    ' (alias for %s)' % params['alias'])

        if 'nicos.core.device.Readable' not in devinfo[5]:
            self.valueFrame.setVisible(False)
        else:
            self.valuelabel.setText(devitem.text(1))
            self.statuslabel.setText(devitem.text(2))
            self.statusimage.setPixmap(devitem.icon(0).pixmap(16, 16))
            setForegroundBrush(self.statuslabel, devitem.foreground(2))
            setBackgroundBrush(self.statuslabel, devitem.background(2))

        if 'nicos.core.device.Moveable' not in devinfo[5]:
            self.controlGroup.setVisible(False)
        else:
            if 'nicos.core.device.HasLimits' not in devinfo[5]:
                self.limitFrame.setVisible(False)
            else:
                self.limitMin.setText(str(params['userlimits'][0]))
                self.limitMax.setText(str(params['userlimits'][1]))
            valuetype = self.client.eval('session.getDevice(%r).valuetype' %
                                         devname)

            if 'value' in params:
                self.target = typedvalue.create(self, valuetype, params['value'],
                                                params.get('fmtstr', '%s'))
            else:
                self.target = typedvalue.create(self, valuetype, valuetype(),
                                                params.get('fmtstr', '%s'))
            self.targetLayout.insertWidget(1, self.target)
            self.targetUnit.setText(params['unit'])
            self.moveBtns.addButton('Reset', QDialogButtonBox.ResetRole)
            self.moveBtns.addButton('Stop', QDialogButtonBox.ResetRole)
            self.movebtn = self.moveBtns.addButton('Move',
                                                   QDialogButtonBox.AcceptRole)
            if params.get('fixed'):
                self.movebtn.setEnabled(False)
                self.movebtn.setText('(fixed)')
            def callback(button):
                if button.text() == 'Reset':
                    self.client.tell('queue', '', 'reset(%s)' % devname)
                elif button.text() == 'Stop':
                    self.client.tell('exec', 'stop(%s)' % devname)
                elif button.text() == 'Move':
                    try:
                        target = self.target.getValue()
                    except ValueError:
                        return
                    self.client.tell('queue', '',
                                     'move(%s, %r)' % (devname, target))
            self.moveBtns.clicked.connect(callback)

    def on_cache(self, subkey, value):
        if subkey not in self.paramItems:
            return
        value = cache_load(value)
        self.paramvalues[subkey] = value
        self.paramItems[subkey].setText(1, str(value))

    def on_paramList_itemClicked(self, item):
        pname = str(item.text(0))
        if not self.paraminfo[pname]['settable']:
            return
        ptype = self.paraminfo[pname]['type']
        mainunit = self.paramvalues.get('unit', 'main')
        punit = (self.paraminfo[pname]['unit'] or '').replace('main', mainunit)

        dlg = dialogFromUi(self, 'devices_param.ui', 'panels')
        dlg.target = typedvalue.create(self, ptype,
                                       self.paramvalues[pname], unit=punit)
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
        self.client.tell('queue', '', '%s.%s = %r' %
                         (self.devname, pname, new_value))
