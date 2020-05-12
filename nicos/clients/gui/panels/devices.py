#  -*- coding: utf-8 -*-
# *****************************************************************************
# NICOS, the Networked Instrument Control System of the MLZ
# Copyright (c) 2009-2020 by the NICOS contributors (see AUTHORS)
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

from __future__ import absolute_import, division, print_function

from logging import WARNING

from nicos.clients.gui.dialogs.error import ErrorDialog
from nicos.clients.gui.panels import Panel, showPanel
from nicos.clients.gui.utils import ScriptExecQuestion, dialogFromUi, loadUi
from nicos.core.status import BUSY, DISABLED, ERROR, NOTREACHED, OK, UNKNOWN, \
    WARN
from nicos.guisupport.qt import QBrush, QByteArray, QColor, QComboBox, \
    QCursor, QDialog, QDialogButtonBox, QFont, QIcon, QInputDialog, QMenu, \
    QMessageBox, QPalette, QPushButton, QRegExp, Qt, QTreeWidgetItem, \
    pyqtSignal, pyqtSlot, sip
from nicos.guisupport.typedvalue import DeviceParamEdit, DeviceValueEdit
from nicos.protocols.cache import OP_TELL, cache_dump, cache_load
from nicos.pycompat import iteritems, itervalues, srepr, string_types
from nicos.utils import AttrDict

foregroundBrush = {
    OK:         QBrush(QColor('#00aa00')),
    WARN:       QBrush(Qt.black),
    BUSY:       QBrush(Qt.black),
    NOTREACHED: QBrush(Qt.black),
    DISABLED:   QBrush(Qt.black),
    ERROR:      QBrush(Qt.black),
    UNKNOWN:    QBrush(QColor('#cccccc')),
}

backgroundBrush = {
    OK:         QBrush(),
    WARN:       QBrush(QColor('#ffa500')),
    BUSY:       QBrush(Qt.yellow),
    NOTREACHED: QBrush(QColor('#ff6655')),
    DISABLED:   QBrush(QColor('#bbbbbb')),
    ERROR:      QBrush(QColor('#ff6655')),
    UNKNOWN:    QBrush(),
}

# keys: (expired, fixed)
valueBrush = {
    (False, False):  QBrush(),
    (False, True):   QBrush(Qt.blue),
    (True, False):   QBrush(QColor('#aaaaaa')),
    (True, True):    QBrush(QColor('#aaaaaa')),
}

lowlevelBrush = {
    False:      QBrush(Qt.black),
    True:       QBrush(QColor('#666666')),
}

lowlevelFont = {
    False:      QFont(),
    True:       QFont(QFont().family(), -1, -1, True),
}

# QTreeWidgetItem types
SETUP_TYPE = QTreeWidgetItem.UserType
DEVICE_TYPE = SETUP_TYPE + 1
PARAM_TYPE = SETUP_TYPE + 2


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


class SetupTreeWidgetItem(QTreeWidgetItem):

    def __init__(self, setupname, display_order, representative):
        QTreeWidgetItem.__init__(self, [setupname, '', ''], SETUP_TYPE)
        self.sortkey = (display_order, setupname)
        self.representative = representative

    def __lt__(self, other):
        return self.sortkey < other.sortkey


class DevInfo(AttrDict):
    """Collects device infos."""

    def __init__(self, name, value='-', status=(OK, ''), fmtstr='%s', unit='',
                 expired=False, fixed=False, classes=None,
                 valtime=0, stattime=0):
        AttrDict.__init__(self, {
            'name': name,
            'value': value,
            'status': status,
            'fmtstr': fmtstr,
            'unit': unit,
            'expired': expired,
            'fixed': fixed,
            'classes': classes or [],
            'valtime': valtime,
            'stattime': stattime,
            'params': {},
        })

    def fmtValUnit(self):
        try:
            fmted = self.fmtstr % self.value
        except Exception:
            fmted = str(self.value)
        return fmted + ' ' + self.unit

    def fmtParam(self, param, value):
        info = self.params.get(param)
        if info:
            try:
                fmtvalue = info['fmtstr'] % value
            except Exception:
                fmtvalue = str(value)
            return fmtvalue + ' ' + (info['unit'] or '')
        return str(value)


class DevicesPanel(Panel):
    """Provides a graphical list of NICOS devices and their current values.

    The user can operate basic device functions (move, stop, reset) by
    selecting an item from the list, which opens a control dialog.

    Options:

    * ``useicons`` (default True) -- if set to False, the list widget does not
      display status icons for the devices.

    * ``param_display`` (default {}) -- a dictionary containing the device name
      as key and a parameter name or a list of the parameter names which should
      be displayed in the device tree as subitems of the device item, for
      example::

         param_display = {
             'tas': 'scanmode',
             'Exp': ['lastpoint', 'lastscan']
         }

    * ``filters`` (default []) -- a list of tuples containing the name of the
      filter and the regular expression to filter out the devices.
      example::

          filters = [
              ('All', ''),
              ('Default', 'T|UBahn'),
              ('Foo', 'bar$'),
          ]

    """

    panelName = 'Devices'
    ui = 'panels/devices.ui'

    @classmethod
    def _createIcons(cls):
        # hack to make non-Qt usage as in checksetups work
        if not hasattr(cls, 'statusIcon'):
            cls.statusIcon = {
                OK: QIcon(':/leds/status_green'),
                WARN: QIcon(':/leds/status_warn'),
                BUSY: QIcon(':/leds/status_yellow'),
                NOTREACHED: QIcon(':/leds/status_red'),
                DISABLED: QIcon(':/leds/status_white'),
                ERROR: QIcon(':/leds/status_red'),
                UNKNOWN: QIcon(':/leds/status_unknown'),
            }

    def __init__(self, parent, client, options):
        DevicesPanel._createIcons()
        Panel.__init__(self, parent, client, options)
        loadUi(self, self.ui)
        self.useicons = bool(options.get('icons', True))
        self.param_display = {}
        param_display = options.get('param_display', {})
        for (key, value) in param_display.items():
            value = [value] if isinstance(value, string_types) else list(value)
            self.param_display[key.lower()] = value

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
        if self.mainwindow.history_wintype is not None:
            self.devmenu.addAction(self.actionPlotHistory)
            self.devmenu.addSeparator()
        self.devmenu.addAction(self.actionShutDown)
        self.devmenu.addAction(self.actionHelp)

        self.devmenu_ro = QMenu(self)
        self.devmenu_ro.addAction(self.actionMove)
        self.devmenu_ro.addAction(self.actionReset)
        self.devmenu_ro.addSeparator()
        if self.mainwindow.history_wintype is not None:
            self.devmenu_ro.addAction(self.actionPlotHistory)
            self.devmenu_ro.addSeparator()
        self.devmenu_ro.addAction(self.actionShutDown)
        self.devmenu_ro.addAction(self.actionHelp)

        self._menu_dev = None   # device for which context menu is shown
        self._dev2setup = {}
        self._setupinfo = {}

        self._control_dialogs = {}
        self._show_lowlevel = self.mainwindow.expertmode

        # daemon request ID of last command executed from this panel
        # (used to display messages from this command)
        self._current_status = 'idle'
        self._exec_reqid = None
        self._error_window = None

        client.connected.connect(self.on_client_connected)
        client.disconnected.connect(self.on_client_disconnected)
        client.cache.connect(self.on_client_cache)
        client.device.connect(self.on_client_device)
        client.setup.connect(self.on_client_setup)
        client.message.connect(self.on_client_message)

        self.filters = options.get('filters', [])
        self.filter.addItem('')
        for text, rx in self.filters:
            self.filter.addItem('Filter: %s' % text, rx)
        self.filter.lineEdit().setPlaceholderText('Enter search expression')

    def updateStatus(self, status, exception=False):
        self._current_status = status

    def saveSettings(self, settings):
        settings.setValue('headers', self.tree.header().saveState())

    def loadSettings(self, settings):
        self._headerstate = settings.value('headers', '', QByteArray)

    def _update_view(self):
        with self.sgroup as settings:
            for i in range(self.tree.topLevelItemCount()):
                v = settings.value('%s/expanded' %
                                   self.tree.topLevelItem(i).text(0),
                                   True, bool)
                self.tree.topLevelItem(i).setExpanded(v)

    def _store_view(self):
        with self.sgroup as settings:
            for i in range(self.tree.topLevelItemCount()):
                settings.setValue('%s/expanded' %
                                  self.tree.topLevelItem(i).text(0),
                                  self.tree.topLevelItem(i).isExpanded())

    def hideTitle(self):
        self.titleLbl.setVisible(False)

    def setExpertMode(self, expert):
        self._show_lowlevel = expert
        self.on_client_connected()

    def clear(self):
        if self.tree:
            self._store_view()
        self._catitems = {}
        # map lowercased devname -> tree widget item
        self._devitems = {}
        self._devparamitems = {}
        # map lowercased devname -> DevInfo instance
        self._devinfo = {}
        self.tree.clear()

    def on_client_connected(self):
        self.clear()

        state = self.client.ask('getstatus')
        if not state:
            return
        devlist = state['devices']
        self._read_setup_info(state['setups'])

        for devname in devlist:
            self._create_device_item(devname)

        # close all control dialogs for now nonexisting devices
        for ldevname in list(self._control_dialogs):
            if ldevname not in self._devitems:
                self._control_dialogs[ldevname].close()

        # add all toplevel items to the tree, sorted
        for cat in self._catitems:
            self.tree.addTopLevelItem(self._catitems[cat])
            self._catitems[cat].setExpanded(True)
        for devitem in itervalues(self._devitems):
            devitem.setExpanded(True)
        self.tree.sortItems(0, Qt.AscendingOrder)
        self._update_view()

    def on_client_disconnected(self):
        self.clear()

    def on_client_message(self, message):
        # show warnings and errors emitted by the current command in a window
        if message[5] != self._exec_reqid or message[2] < WARNING:
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

    def _read_setup_info(self, setuplists=None):
        if setuplists is None:
            allstatus = self.client.ask('getstatus')
            if allstatus is None:
                return
            setuplists = allstatus['setups']
        loaded_setups = set(setuplists[0])
        self._dev2setup = {}
        self._setupinfo = self.client.eval('session.getSetupInfo()', {})
        if self._setupinfo is None:
            self.log.warning('session.getSetupInfo() returned None instead '
                             'of {}')
            return
        for setupname, info in iteritems(self._setupinfo):
            if info is None:
                continue
            if setupname not in loaded_setups:
                continue
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
        if 'nicos.core.data.sink.DataSink' in params.get('classes', []) and \
           not self._show_lowlevel:
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
            display_order = self._setupinfo[cat].get('display_order', 50)
            representative = self._setupinfo[cat].get(
                'extended', {}).get('representative', '').lower()
            catitem = SetupTreeWidgetItem(cat, display_order, representative)
            catitem.setToolTip(0, self._setupinfo[cat].get('description', ''))
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
        devitem = QTreeWidgetItem(catitem, [devname, '', ''], DEVICE_TYPE)

        devitem.setForeground(0, lowlevelBrush[lowlevel_device])
        devitem.setFont(0, lowlevelFont[lowlevel_device])

        if self.useicons:
            devitem.setIcon(0, self.statusIcon[OK])
        devitem.setToolTip(0, params.get('description', ''))
        self._devitems[ldevname] = devitem
        # fill the device info with dummy values, will be populated below
        self._devinfo[ldevname] = DevInfo(devname)

        # let the cache handler process all properties
        for key, value in iteritems(params):
            self.on_client_cache((0, ldevname + '/' + key, OP_TELL,
                                  cache_dump(value)))

    def on_client_setup(self, setuplists):
        # update setup tooltips
        self._read_setup_info(setuplists)
        for i in range(self.tree.topLevelItemCount()):
            catitem = self.tree.topLevelItem(i)
            cat = catitem.text(0)
            catitem.setToolTip(0, self._setupinfo[cat].get('description', ''))

    def on_client_device(self, data):
        (action, devlist) = data
        if not devlist:
            return
        if action == 'create':
            for devname in devlist:
                self._create_device_item(devname, add_cat=True)
            self.tree.sortItems(0, Qt.AscendingOrder)
            self._update_view()
        elif action == 'destroy':
            self._store_view()
            for devname in devlist:
                ldevname = devname.lower()
                if ldevname in self._devitems:
                    # remove device item and cached info...
                    item = self._devitems[ldevname]
                    del self._devitems[ldevname]
                    del self._devinfo[ldevname]
                    self._devparamitems.pop(ldevname, None)
                    try:
                        catitem = item.parent()
                    except RuntimeError:
                        # Qt object has already been destroyed
                        pass
                    else:
                        catitem.removeChild(item)
                        # remove category item if it has no further children
                        if catitem.childCount() == 0:
                            self.tree.takeTopLevelItem(
                                self.tree.indexOfTopLevelItem(catitem))
                            del self._catitems[catitem.text(0)]
            self._update_view()

    def on_client_cache(self, data):
        (time, key, op, value) = data
        if '/' not in key:
            return
        ldevname, subkey = key.rsplit('/', 1)
        if ldevname not in self._devinfo:
            return
        if ldevname in self._control_dialogs:
            self._control_dialogs[ldevname].on_cache(subkey, value)
        devitem = self._devitems[ldevname]
        devinfo = self._devinfo[ldevname]
        if subkey == 'value':
            if time < devinfo.valtime:
                return
            if not value:
                fvalue = ''
            else:
                fvalue = cache_load(value)
                if isinstance(fvalue, list):
                    fvalue = tuple(fvalue)
            devinfo.value = fvalue
            devinfo.expired = op != OP_TELL
            devinfo.valtime = time
            fmted = devinfo.fmtValUnit()
            devitem.setText(1, fmted)
            if ldevname in self._control_dialogs:
                self._control_dialogs[ldevname].valuelabel.setText(fmted)
            devitem.setForeground(1, valueBrush[devinfo.expired, devinfo.fixed])
            if not devitem.parent().isExpanded():
                if ldevname == devitem.parent().representative:
                    devitem.parent().setText(1, fmted)
        elif subkey == 'status':
            if time < devinfo.stattime:
                return
            if not value:
                status = (UNKNOWN, '?')
            else:
                status = cache_load(value)
            devinfo.status = status
            devinfo.stattime = time
            devitem.setText(2, str(status[1]))
            if status[0] not in self.statusIcon:
                # old or wrong status constant
                return
            if self.useicons:
                devitem.setIcon(0, self.statusIcon[status[0]])
                devitem.setForeground(2, foregroundBrush[status[0]])
                devitem.setBackground(2, backgroundBrush[status[0]])
            else:
                devitem.setForeground(0, foregroundBrush[BUSY])
                devitem.setBackground(0, backgroundBrush[status[0]])
            if not devitem.parent().isExpanded():
                item = devitem.parent()
                item.setBackground(0, backgroundBrush[
                    self._getHighestStatus(item)])
            else:
                devitem.parent().setBackground(0, backgroundBrush[OK])
            if ldevname in self._control_dialogs:
                dlg = self._control_dialogs[ldevname]
                dlg.statuslabel.setText(status[1])
                dlg.statusimage.setPixmap(self.statusIcon[status[0]].pixmap(16, 16))
                setForegroundBrush(dlg.statuslabel, foregroundBrush[status[0]])
                setBackgroundBrush(dlg.statuslabel, backgroundBrush[status[0]])
        elif subkey == 'fmtstr':
            if not value:
                return
            devinfo.fmtstr = cache_load(value)
            devitem.setText(1, devinfo.fmtValUnit())
        elif subkey == 'unit':
            if not value:
                value = "''"
            devinfo.unit = cache_load(value)
            devitem.setText(1, devinfo.fmtValUnit())
        elif subkey == 'fixed':
            if not value:
                value = "''"
            devinfo.fixed = bool(cache_load(value))
            devitem.setForeground(1, valueBrush[devinfo.expired, devinfo.fixed])
            if ldevname in self._control_dialogs:
                dlg = self._control_dialogs[ldevname]
                if dlg.moveBtn:
                    dlg.moveBtn.setEnabled(not devinfo.fixed)
                    dlg.moveBtn.setText(devinfo.fixed and '(fixed)' or 'Move')
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
            devinfo.classes = set(cache_load(value))
        elif subkey == 'alias':
            if not value:
                return
            if ldevname in self._control_dialogs:
                dlg = self._control_dialogs[ldevname]
                dlg._reinit()
        elif subkey == 'description':
            devitem.setToolTip(0, cache_load(value or "''"))
        if subkey in self.param_display.get(ldevname, ()):
            if not devinfo.params:
                devinfo.params = self.client.getDeviceParamInfo(devinfo.name)
            value = devinfo.fmtParam(subkey, cache_load(value))
            if subkey not in self._devparamitems.setdefault(ldevname, {}):
                devitem = self._devitems[ldevname]
                self._devparamitems[ldevname][subkey] = \
                    QTreeWidgetItem(devitem, [subkey, value, ''], PARAM_TYPE)
                devitem.setExpanded(True)
            else:
                self._devparamitems[ldevname][subkey].setText(1, value)

    def on_tree_itemExpanded(self, item):
        if item.type() == SETUP_TYPE:
            item.setText(1, '')
        item.setBackground(0, backgroundBrush[OK])

    def _getHighestStatus(self, item):
        retval = OK
        for i in range(item.childCount()):
            lstatus = self._devinfo[item.child(i).text(0).lower()].status[0]
            if retval < lstatus:
                retval = lstatus
        return retval

    def on_tree_itemCollapsed(self, item):
        if item.type() == SETUP_TYPE:
            item.setBackground(0, backgroundBrush[self._getHighestStatus(item)])
            if item.representative:
                item.setText(1, self._devitems[item.representative].text(1))

    def on_tree_customContextMenuRequested(self, point):
        item = self.tree.itemAt(point)
        if item is None:
            return
        if item.type() == DEVICE_TYPE:
            self._menu_dev = item.text(0)
            ldevname = self._menu_dev.lower()
            if 'nicos.core.device.Moveable' in self._devinfo[ldevname].classes and \
               not self.client.viewonly:
                self.devmenu.popup(self.tree.viewport().mapToGlobal(point))
            elif 'nicos.core.device.Readable' in self._devinfo[ldevname].classes:
                self.devmenu_ro.popup(self.tree.viewport().mapToGlobal(point))

    def on_filter_editTextChanged(self, text):
        for i in range(self.filter.count()):
            if text == self.filter.itemText(i):
                rx = QRegExp(self.filter.itemData(i))
                break
        else:
            rx = QRegExp(text)
        for i in range(self.tree.topLevelItemCount()):
            setupitem = self.tree.topLevelItem(i)
            all_children_hidden = True
            for j in range(setupitem.childCount()):
                devitem = setupitem.child(j)
                if rx.indexIn(devitem.text(0)) == -1:
                    devitem.setHidden(True)
                else:
                    devitem.setHidden(False)
                    all_children_hidden = False
            setupitem.setHidden(all_children_hidden)

    @pyqtSlot()
    def on_actionShutDown_triggered(self):
        if self._menu_dev:
            if self.askQuestion('This will unload the device until the setup '
                                'is loaded again. Proceed?'):
                self.exec_command('RemoveDevice(%s)' % srepr(self._menu_dev),
                                  ask_queue=False)

    @pyqtSlot()
    def on_actionReset_triggered(self):
        if self._menu_dev:
            self.exec_command('reset(%s)' % srepr(self._menu_dev))

    @pyqtSlot()
    def on_actionFix_triggered(self):
        if self._menu_dev:
            reason, ok = QInputDialog.getText(
                self, 'Fix',
                'Please enter the reason for fixing %s:' % self._menu_dev)
            if not ok:
                return
            self.exec_command('fix(%s, %r)' % (srepr(self._menu_dev), reason))

    @pyqtSlot()
    def on_actionRelease_triggered(self):
        if self._menu_dev:
            self.exec_command('release(%s)' % srepr(self._menu_dev))

    @pyqtSlot()
    def on_actionStop_triggered(self):
        if self._menu_dev:
            self.exec_command('stop(%s)' % srepr(self._menu_dev),
                              immediate=True)

    @pyqtSlot()
    def on_actionMove_triggered(self):
        if self._menu_dev:
            self._open_control_dialog(self._menu_dev)

    @pyqtSlot()
    def on_actionHelp_triggered(self):
        if self._menu_dev:
            self.client.eval('session.showHelp(session.devices[%r])' %
                             self._menu_dev)

    @pyqtSlot()
    def on_actionPlotHistory_triggered(self):
        if self._menu_dev:
            self.plot_history(self._menu_dev)

    def on_tree_itemActivated(self, item, column):
        if item.type() == DEVICE_TYPE:
            devname = item.text(0)
            self._open_control_dialog(devname)
        elif item.type() == PARAM_TYPE:
            devname = item.parent().text(0)
            dlg = self._open_control_dialog(devname)
            dlg.editParam(item.text(0))

    def _open_control_dialog(self, devname):
        ldevname = devname.lower()
        if ldevname in self._control_dialogs:
            dlg = self._control_dialogs[ldevname]
            if dlg.isVisible():
                dlg.activateWindow()
                return dlg
        devinfo = self._devinfo[ldevname]
        item = self._devitems[ldevname]
        dlg = ControlDialog(self, devname, devinfo, item, self.log,
                            self._show_lowlevel)
        dlg.closed.connect(self._control_dialog_closed)
        dlg.rejected.connect(dlg.close)
        self._control_dialogs[ldevname] = dlg
        dlg.show()
        return dlg

    def _control_dialog_closed(self, ldevname):
        dlg = self._control_dialogs.pop(ldevname, None)
        if dlg:
            dlg.deleteLater()

    # API shared with ControlDialog

    def exec_command(self, command, ask_queue=True, immediate=False):
        if ask_queue and not immediate and self._current_status != 'idle':
            qwindow = ScriptExecQuestion()
            result = qwindow.exec_()
            if result == QMessageBox.Cancel:
                return
            elif result == QMessageBox.Apply:
                immediate = True
        if immediate:
            self.client.tell('exec', command)
            self._exec_reqid = None  # no request assigned to this command
        else:
            self._exec_reqid = self.client.run(command)

    def plot_history(self, dev):
        if self.mainwindow.history_wintype is not None:
            win = self.mainwindow.createWindow(self.mainwindow.history_wintype)
            if win:
                panel = win.getPanel('History viewer')
                panel.newView(dev)
                showPanel(panel)


class ControlDialog(QDialog):
    """Dialog opened to control and view details for one device."""

    closed = pyqtSignal(object)

    def __init__(self, parent, devname, devinfo, devitem, log, expert):
        QDialog.__init__(self, parent)
        loadUi(self, 'panels/devices_one.ui')
        self.log = log

        self.device_panel = parent
        self.client = parent.client
        self.devname = devname
        self.devinfo = devinfo
        self.devitem = devitem
        self.paramItems = {}
        self.moveBtn = None
        self.target = None

        self._reinit()
        self._show_extension(expert)

        if self.target:
            self.target.setFocus()

    def _reinit(self):
        classes = self.devinfo.classes

        if sip.isdeleted(self.devitem):
            # The item we're controlling has been removed from the list (e.g.
            # due to client reconnect), get it again.
            self.devitem = self.device_panel._devitems.get(self.devname.lower())
            # No such device anymore...
            if self.devitem is None:
                self.close()
                return

        self.deviceName.setText('Device: %s' % self.devname)
        self.setWindowTitle('Control %s' % self.devname)

        self.settingsBtn = self.buttonBox.button(QDialogButtonBox.RestoreDefaults)
        self.settingsBtn.clicked.connect(self.on_settingsBtn_clicked)

        # trigger parameter poll
        self.client.eval('%s.pollParams()' % self.devname, None)

        # now get all cache keys pertaining to the device and set the
        # properties we want
        params = self.client.getDeviceParams(self.devname)
        self.paraminfo = self.client.getDeviceParamInfo(self.devname)
        self.paramvalues = dict(params)

        # put parameter values in the list widget
        self.paramItems.clear()
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

        # check how to refer to the device in commands: if it is lowlevel,
        # we need to use quotes
        self.devrepr = srepr(self.devname) if params.get('lowlevel', True) \
            else self.devname

        # show "Set alias" group box if it is an alias device
        if 'alias' in params:
            if params['alias']:
                self.deviceName.setText(self.deviceName.text() +
                                        ' (alias for %s)' % params['alias'])
            alias_config = self.client.eval('session.alias_config', {})
            self.aliasTarget = QComboBox(self)
            self.aliasTarget.setEditable(True)
            if self.devname in alias_config:
                items = [t[0] for t in alias_config[self.devname]]
                self.aliasTarget.addItems(items)
                if params['alias'] in items:
                    self.aliasTarget.setCurrentIndex(items.index(params['alias']))
            self.targetLayoutAlias.takeAt(1).widget().deleteLater()
            self.targetLayoutAlias.insertWidget(1, self.aliasTarget)
            if self.client.viewonly:
                self.setAliasBtn.setEnabled(False)
        else:
            self.aliasGroup.setVisible(False)

        historyBtn = self.buttonBox.button(QDialogButtonBox.Reset)
        # show current value/status if it is readable
        if 'nicos.core.device.Readable' not in classes:
            self.valueFrame.setVisible(False)
            self.buttonBox.removeButton(historyBtn)
        else:
            self.valuelabel.setText(self.devitem.text(1))
            self.statuslabel.setText(self.devitem.text(2))
            self.statusimage.setPixmap(self.devitem.icon(0).pixmap(16, 16))
            setForegroundBrush(self.statuslabel, self.devitem.foreground(2))
            setBackgroundBrush(self.statuslabel, self.devitem.background(2))

            # modify history button: add icon and set text
            historyBtn.setIcon(QIcon(':/find'))
            historyBtn.setText('Plot history...')
            historyBtn.clicked.connect(self.on_historyBtn_clicked)

        if self.client.viewonly:
            self.limitFrame.setVisible(False)
            self.targetFrame.setVisible(False)
            return

        # add a menu for the "More" button
        self.moveBtns.clear()
        menu = QMenu(self)
        if 'nicos.core.mixins.HasLimits' in classes:
            menu.addAction(self.actionSetLimits)
        if 'nicos.core.mixins.HasOffset' in classes:
            menu.addAction(self.actionAdjustOffset)
        if 'nicos.devices.abstract.CanReference' in classes:
            menu.addAction(self.actionReference)
        if 'nicos.devices.abstract.Coder' in classes:
            menu.addAction(self.actionSetPosition)
        if 'nicos.core.device.Moveable' in classes:
            if not menu.isEmpty():
                menu.addSeparator()
            menu.addAction(self.actionFix)
            menu.addAction(self.actionRelease)
        if 'nicos.core.mixins.CanDisable' in classes:
            if not menu.isEmpty():
                menu.addSeparator()
            menu.addAction(self.actionEnable)
            menu.addAction(self.actionDisable)
        if not menu.isEmpty():
            menuBtn = QPushButton('More', self)
            menuBtn.setMenu(menu)
            self.moveBtns.addButton(menuBtn, QDialogButtonBox.ResetRole)

        def reset(checked):
            self.device_panel.exec_command('reset(%s)' % self.devrepr)

        def stop(checked):
            self.device_panel.exec_command('stop(%s)' % self.devrepr,
                                           immediate=True)

        self.moveBtns.addButton('Reset', QDialogButtonBox.ResetRole)\
                     .clicked.connect(reset)

        if 'nicos.core.device.Moveable' in classes or \
           'nicos.core.device.Measurable' in classes:
            self.moveBtns.addButton('Stop', QDialogButtonBox.ResetRole)\
                         .clicked.connect(stop)

        # show target and limits if the device is Moveable
        if 'nicos.core.device.Moveable' not in classes:
            self.limitFrame.setVisible(False)
            self.targetFrame.setVisible(False)
        else:
            if 'nicos.core.mixins.HasLimits' not in classes:
                self.limitFrame.setVisible(False)
            else:
                self.limitMin.setText(str(params['userlimits'][0]))
                self.limitMax.setText(str(params['userlimits'][1]))

            # insert a widget to enter a new device value
            # allowEnter=False because we catch pressing Enter ourselves
            self.target = DeviceValueEdit(self, dev=self.devname,
                                          useButtons=True, allowEnter=False)
            self.target.setClient(self.client)

            def btn_callback(target):
                self.device_panel.exec_command('move(%s, %s)' %
                                               (self.devrepr, srepr(target)))
            self.target.valueChosen.connect(btn_callback)
            self.targetFrame.layout().takeAt(1).widget().deleteLater()
            self.targetFrame.layout().insertWidget(1, self.target)

            def move(checked):
                try:
                    target = self.target.getValue()
                except ValueError:
                    return
                self.device_panel.exec_command(
                    'move(%s, %s)' % (self.devrepr, srepr(target)))

            if self.target.getValue() is not Ellipsis:  # (button widget)
                self.moveBtn = self.moveBtns.addButton(
                    'Move', QDialogButtonBox.AcceptRole)
                self.moveBtn.clicked.connect(move)
            else:
                self.moveBtn = None

            if params.get('fixed') and self.moveBtn:
                self.moveBtn.setEnabled(False)
                self.moveBtn.setText('(fixed)')

    def on_paramList_customContextMenuRequested(self, pos):
        item = self.paramList.itemAt(pos)
        if not item:
            return

        menu = QMenu(self)
        refreshAction = menu.addAction('Refresh')
        menu.addAction('Refresh all')

        # QCursor.pos is more reliable then the given pos
        action = menu.exec_(QCursor.pos())

        if action:
            cmd = 'session.getDevice(%r).pollParams(volatile_only=False%s)' \
                  % (self.devname, ', param_list=[%r]' % item.text(0)
                     if action == refreshAction else '')
            # poll even non volatile parameter as requested explicitely
            self.client.eval(cmd, None)

    @pyqtSlot()
    def on_settingsBtn_clicked(self):
        self._show_extension(self.extension.isHidden())

    def _show_extension(self, show):
        if show:
            # make "settings shown" permanent
            self.settingsBtn.hide()
        self.extension.setVisible(show)
        self.settingsBtn.setText('Settings %s' % ('<<<' if show else '>>>'))
        sz = self.size()
        sz.setHeight(self.sizeHint().height())
        self.resize(sz)

    @pyqtSlot()
    def on_actionSetLimits_triggered(self):
        dlg = dialogFromUi(self, 'panels/devices_limits.ui')
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
            self.device_panel.exec_command('resetlimits(%s)' % self.devrepr)
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
        self.device_panel.exec_command('set(%s, "userlimits", %s)' %
                                       (self.devrepr, newlimits))

    def _get_new_value(self, window_title, desc):
        dlg = dialogFromUi(self, 'panels/devices_newpos.ui')
        dlg.setWindowTitle(window_title)
        dlg.descLabel.setText(desc)
        dlg.oldValue.setText(self.valuelabel.text())
        target = DeviceValueEdit(dlg, dev=self.devname)
        target.setClient(self.client)
        dlg.targetLayout.addWidget(target)
        target.setFocus()
        res = dlg.exec_()
        if res != QDialog.Accepted:
            return None
        return target.getValue()

    @pyqtSlot()
    def on_actionAdjustOffset_triggered(self):
        val = self._get_new_value('Adjust NICOS offset',
                                  'Adjust NICOS offset of %s:' % self.devname)
        if val is not None:
            self.device_panel.exec_command(
                'adjust(%s, %r)' % (self.devrepr, val))

    @pyqtSlot()
    def on_actionSetPosition_triggered(self):
        val = self._get_new_value('Set hardware position',
                                  'Set hardware position of %s:' % self.devname)
        if val is not None:
            if self.devrepr != self.devname:
                cmd = 'CreateDevice(%s); %s.setPosition(%r)' % \
                      (self.devrepr, self.devname, val)
            else:
                cmd = '%s.setPosition(%r)' % (self.devname, val)
            self.device_panel.exec_command(cmd)

    @pyqtSlot()
    def on_actionReference_triggered(self):
        self.device_panel.exec_command('reference(%s)' % self.devrepr)

    @pyqtSlot()
    def on_actionFix_triggered(self):
        reason, ok = QInputDialog.getText(
            self, 'Fix',
            'Please enter the reason for fixing %s:' % self.devname)
        if not ok:
            return
        self.device_panel.exec_command('fix(%s, %r)' % (self.devrepr, reason))

    @pyqtSlot()
    def on_actionRelease_triggered(self):
        self.device_panel.exec_command('release(%s)' % self.devrepr)

    @pyqtSlot()
    def on_actionEnable_triggered(self):
        self.device_panel.exec_command('enable(%s)' % self.devrepr)

    @pyqtSlot()
    def on_actionDisable_triggered(self):
        self.device_panel.exec_command('disable(%s)' % self.devrepr)

    @pyqtSlot()
    def on_setAliasBtn_clicked(self):
        self.device_panel.exec_command(
            'set(%s, "alias", %s)' %
            (self.devrepr, srepr(self.aliasTarget.currentText())))

    def closeEvent(self, event):
        event.accept()
        self.closed.emit(self.devname.lower())

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
        self.editParam(pname)

    def editParam(self, pname):
        if not self.paraminfo[pname]['settable'] or self.client.viewonly:
            return
        mainunit = self.paramvalues.get('unit', 'main')
        punit = (self.paraminfo[pname]['unit'] or '').replace('main', mainunit)

        dlg = dialogFromUi(self, 'panels/devices_param.ui')
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
        if self.devrepr == self.devname:
            self.device_panel.exec_command(
                '%s.%s = %r' % (self.devname, pname, new_value))
        else:
            self.device_panel.exec_command(
                'set(%s, %s, %r)' % (self.devrepr, srepr(pname), new_value))

    def on_historyBtn_clicked(self):
        self.device_panel.plot_history(self.devname)
