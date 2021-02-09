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
#   Georg Brandl <g.brandl@fz-juelich.de>
#   Artem Feoktystov <a.feoktystov@fz-juelich.de>
#
# *****************************************************************************

"""LoKI sample configuration dialog."""

import builtins
import math
import time

from nicos.clients.gui.panels import Panel
from nicos.clients.gui.utils import dialogFromUi, loadUi
from nicos.guisupport import typedvalue
from nicos.guisupport.qt import QDialog, QDialogButtonBox, QFileDialog, \
    QFrame, QLineEdit, QListWidgetItem, QMenu, QMessageBox, QRadioButton, \
    QTableWidgetItem, QVBoxLayout, pyqtSlot
from nicos.guisupport.utils import DoubleValidator
from nicos.utils import findResource


SAMPLE_KEYS = ('aperture', 'position', 'thickness', 'detoffset', 'comment')


def configToFrame(frame, config):
    frame.nameBox.setText(config['name'])
    frame.commentBox.setText(config['comment'])
    frame.offsetBox.setText(str(config['detoffset']))
    frame.thickBox.setText(str(config['thickness']))
    frame.posTbl.setRowCount(len(config['position']))
    frame.apXBox.setText(str(config['aperture'][0]))
    frame.apYBox.setText(str(config['aperture'][1]))
    frame.apWBox.setText(str(config['aperture'][2]))
    frame.apHBox.setText(str(config['aperture'][3]))
    for i, (dev_name, position) in enumerate(config['position'].items()):
        frame.posTbl.setItem(i, 0, QTableWidgetItem(dev_name))
        frame.posTbl.setItem(i, 1, QTableWidgetItem(str(position)))
    frame.posTbl.resizeRowsToContents()
    frame.posTbl.resizeColumnsToContents()


def configFromFrame(frame):
    position = {}
    for i in range(frame.posTbl.rowCount()):
        dev_name = frame.posTbl.item(i, 0).text()
        dev_pos = float(frame.posTbl.item(i, 1).text())
        position[dev_name] = dev_pos
    return {
        'name': frame.nameBox.text(),
        'comment': frame.commentBox.text(),
        'detoffset': float(frame.offsetBox.text()),
        'thickness': float(frame.thickBox.text()),
        'aperture': (float(frame.apXBox.text()),
                     float(frame.apYBox.text()),
                     float(frame.apWBox.text()),
                     float(frame.apHBox.text())),
        'position': position,
    }


ConfigEditDialog_QSS = """
/* give dialog buttons a border when tabbing through them */
QPushButton:focus {
    border: 3px solid #6d93c9;
}
"""


class ConfigEditDialog(QDialog):

    def __init__(self, parent, client, instrument, configs, config=None):
        QDialog.__init__(self, parent)
        self.instrument = instrument
        self.configs = configs
        self.client = client
        self.setWindowTitle('Sample configuration')
        layout = QVBoxLayout()
        self.frm = QFrame(self)
        loadUi(self.frm, findResource(
            'nicos_ess/loki/gui/ui_files/sampleconf_one.ui'))
        self.frm.addDevBtn.clicked.connect(self.on_addDevBtn_clicked)
        self.frm.delDevBtn.clicked.connect(self.on_delDevBtn_clicked)
        self.frm.readDevsBtn.clicked.connect(self.on_readDevsBtn_clicked)
        box = QDialogButtonBox(self)
        box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box.accepted.connect(self.maybeAccept)
        box.rejected.connect(self.reject)
        layout.addWidget(self.frm)
        layout.addWidget(box)
        self.setLayout(layout)
        for box in [self.frm.offsetBox, self.frm.thickBox, self.frm.apXBox,
                    self.frm.apYBox, self.frm.apWBox, self.frm.apHBox]:
            box.setValidator(DoubleValidator(self))
        # List of properties that are going to be enabled in-place for edit,
        # thus should not be visible here.
        relevant_list = [self.frm.offsetBox, self.frm.apXBox, self.frm.apYBox,
                         self.frm.apWBox, self.frm.apHBox]
        for box in relevant_list:
            box.setVisible(False)
        if config is not None:
            configToFrame(self.frm, config)

        # Apply local customisations to the stylesheet
        self.setStyleSheet(ConfigEditDialog_QSS)

        if not config:
            self.frm.whatLbl.setText('New sample configuration')

    def maybeAccept(self):
        if not self.frm.nameBox.text():
            QMessageBox.warning(self, 'Error', 'Please enter a sample name.')
            self.frm.nameBox.setFocus()
            return
        name = self.frm.nameBox.text()
        if name in [config['name'] for config in self.configs]:
            QMessageBox.warning(self, 'Error', 'This sample name is already '
                                               'used, please use a different '
                                               'one.')
            self.frm.nameBox.setFocus()
            return
        if float(self.frm.thickBox.text()) == 0:
            QMessageBox.warning(self, 'Error', 'Thickness cannot be zero.')
            self.frm.thickBox.setFocus()
            return
        for box in [self.frm.offsetBox, self.frm.thickBox, self.frm.apXBox,
                    self.frm.apYBox, self.frm.apWBox, self.frm.apHBox]:
            if not box.text():
                QMessageBox.warning(self, 'Error', 'Please enter valid values '
                                                   'for all input fields.')
                return
        for i in range(self.frm.posTbl.rowCount()):
            dev_name = self.frm.posTbl.item(i, 0).text()
            dev_pos = self.frm.posTbl.item(i, 1).text()
            if not dev_name or dev_name.startswith('<'):
                QMessageBox.warning(
                    self, 'Error', f'{dev_name} is not a valid device name.')
                return
            try:
                dev_pos = float(dev_pos)
            except ValueError:
                QMessageBox.warning(
                    self, 'Error', f'{dev_pos} is not a valid '
                                   f'position for device {dev_name}.')
                return
        self.accept()

    def _addRow(self, name, value):
        rc = self.frm.posTbl.rowCount()
        self.frm.posTbl.setRowCount(rc + 1)
        self.frm.posTbl.setItem(rc, 0, QTableWidgetItem(name))
        self.frm.posTbl.setItem(rc, 1, QTableWidgetItem(value))
        self.frm.posTbl.resizeColumnsToContents()
        self.frm.posTbl.resizeRowsToContents()

    def on_addDevBtn_clicked(self):
        dev_list = self.client.getDeviceList(
            'nicos.core.device.Moveable', only_explicit=False)
        # Only get the sample changer related motors
        dev_list = [item for item in dev_list
                    if item.startswith('sc_') and 'motor' in item]
        dlg = dialogFromUi(self, findResource(
            'nicos_ess/loki/gui/ui_files/sampleconf_adddev.ui'))
        dlg.widget = None

        def callback(index):
            dev_name = dev_list[index]
            if dlg.widget:
                dlg.widget.deleteLater()
                dlg.valueFrame.layout().takeAt(0)
            dlg.widget = typedvalue.DeviceValueEdit(dlg, dev=dev_name)
            dlg.widget.setClient(self.client)
            dlg.valueFrame.layout().insertWidget(0, dlg.widget)

        dlg.devBox.currentIndexChanged.connect(callback)
        dlg.devBox.addItems(dev_list)
        if not dlg.exec_():
            return
        if dlg.widget is not None:
            self._addRow(dlg.devBox.currentText(), str(dlg.widget.getValue()))

    def on_delDevBtn_clicked(self):
        sample_row = self.frm.posTbl.currentRow()
        if sample_row < 0:
            return
        self.frm.posTbl.removeRow(sample_row)

    def _readDev(self, name):
        rv = self.client.eval('%s.format(%s.read())' % (name, name), None)
        if rv is None:
            QMessageBox.warning(
                self, 'Error', f'Could not read device {name}!')
            return '0'
        return rv

    def on_readDevsBtn_clicked(self):
        dlg = dialogFromUi(self, findResource(
            'nicos_ess/loki/gui/ui_files/sampleconf_readpos.ui'))
        if self.instrument == 'kws1':
            dlg.kws3Box.hide()
        elif self.instrument == 'kws2':
            dlg.kws3Box.hide()
            dlg.hexaBox.hide()
        elif self.instrument == 'kws3':
            dlg.rotBox.hide()
            dlg.transBox.hide()
            dlg.hexaBox.hide()
            dlg.kws3Box.setChecked(True)
        if not dlg.exec_():
            return
        if dlg.rotBox.isChecked():
            self._addRow('sam_rot', self._readDev('sam_rot'))
        if dlg.transBox.isChecked():
            self._addRow('sam_trans_x', self._readDev('sam_trans_x'))
            self._addRow('sam_trans_y', self._readDev('sam_trans_y'))
        if dlg.hexaBox.isChecked():
            for axis in ('dt', 'tx', 'ty', 'tz', 'rx', 'ry', 'rz'):
                self._addRow('hexapod_' + axis,
                             self._readDev('hexapod_' + axis))
        if dlg.kws3Box.isChecked():
            self._addRow('sam_x', self._readDev('sam_x'))
            self._addRow('sam_y', self._readDev('sam_y'))


class LokiSamplePanel(Panel):
    panelName = 'LoKI sample setup'

    def __init__(self, parent, client, options):
        Panel.__init__(self, parent, client, options)
        loadUi(self, findResource('nicos_ess/loki/gui/ui_files/sampleconf.ui'))
        self.sampleGroup.setEnabled(False)
        self.frame.setLayout(QVBoxLayout())

        menu = QMenu(self)
        menu.addAction(self.actionEmpty)
        menu.addAction(self.actionGenerate)
        self.createBtn.setMenu(menu)

        self.configs = []
        self.holder_info = options.get('holder_info', [])
        self.instrument = options.get('instrument', 'loki')
        self.applyBtn_was_enabled = False
        self.applyBtn.setEnabled(False)
        self.initialise_connection_status_listeners()

    def initialise_connection_status_listeners(self):
        if self.client.isconnected:
            self.on_client_connected()
        else:
            self.on_client_disconnected()
        self.client.connected.connect(self.on_client_connected)
        self.client.disconnected.connect(self.on_client_disconnected)

    def on_client_connected(self):
        self.setViewOnly(self.client.viewonly)

    def on_client_disconnected(self):
        self.setViewOnly(True)

    def setViewOnly(self, viewonly):
        for control in [
            self.createBtn, self.retrieveBtn, self.openFileBtn,
            self.saveBtn, self.newBtn, self.editBtn, self.delBtn, self.frame,
            self.list
        ]:
            control.setEnabled(not viewonly)
        # Handle apply button separately.
        if viewonly:
            self.applyBtn_was_enabled = self.applyBtn.isEnabled()
            self.applyBtn.setEnabled(False)
        # If one toggles view only mode without applying changes, upon exiting
        # view-only mode, following ensures apply button is enabled.
        elif self.applyBtn_was_enabled:
            self.applyBtn.setEnabled(True)

    @pyqtSlot()
    def on_actionEmpty_triggered(self):
        self._clear_samples()
        self._clearDisplay()
        self.sampleGroup.setEnabled(True)

    @pyqtSlot()
    def on_actionGenerate_triggered(self):
        def read_axes():
            ax1, ax2 = dlg._info[2], dlg._info[4]
            for (ax, box) in [(ax1, dlg.ax1Box), (ax2, dlg.ax2Box)]:
                if not ax:
                    continue
                x = self.client.eval('%s.read()' % ax, None)
                if x is None:
                    QMessageBox.warning(dlg, 'Error',
                                        f'Could not read {ax}.')
                    return
                box.setText(f'x:.1f')

        def btn_toggled(checked):
            if checked:
                dlg._info = dlg.sender()._info
                ax1, ax2 = dlg._info[2], dlg._info[4]
                for ax, lbl, box, revbox in [
                    (ax1, dlg.ax1Lbl, dlg.ax1Box, dlg.ax1RevBox),
                    (ax2, dlg.ax2Lbl, dlg.ax2Box, None)
                ]:
                    if ax:
                        lbl.setText(ax)
                        lbl.show()
                        box.show()
                        if revbox:
                            revbox.show()
                            revbox.setText(f'{ax} starts at far end')
                    else:
                        lbl.hide()
                        box.hide()
                        if revbox:
                            revbox.hide()

        if not self.holder_info:
            self.showError('Cannot auto-generate sample list as no sample '
                           'changers are defined')
            return

        dlg = dialogFromUi(self, findResource(
            'nicos_ess/loki/gui/ui_files/sampleconf_gen.ui'))
        dlg.ax1Box.setValidator(DoubleValidator(self))
        dlg.ax2Box.setValidator(DoubleValidator(self))
        dlg.readBtn.clicked.connect(read_axes)
        n_rows = int(math.ceil(len(self.holder_info) / 2.0))
        row, col = 0, 0
        for name, info in self.holder_info:
            btn = QRadioButton(name, dlg)
            btn._info = info
            btn.toggled.connect(btn_toggled)
            dlg.optionFrame.layout().addWidget(btn, row, col)
            if (row, col) == (0, 0):
                btn.setChecked(True)
            row += 1
            if row == n_rows:
                row = 0
                col += 1
        if dlg.exec_() != QDialog.Accepted:
            return

        self._generate_configs(dlg)

        first_item = None
        for config in self.configs:
            new_item = QListWidgetItem(config['name'], self.list)
            first_item = first_item or new_item
        # select the first item
        self.list.setCurrentItem(first_item)
        self.on_list_itemClicked(first_item)

        self.sampleGroup.setEnabled(True)
        self.applyBtn.setEnabled(True)

    def _generate_configs(self, dlg):
        rows, levels, ax1, dax1, ax2, dax2 = dlg._info
        sax1 = float(dlg.ax1Box.text()) if ax1 else 0
        sax2 = float(dlg.ax2Box.text()) if ax2 else 0
        if dlg.ax1RevBox.isChecked():
            dax1 = -dax1

        self._clear_samples()
        n = 0
        for i in range(levels):
            for j in range(rows):
                n += 1
                position = {}
                if ax1:
                    position[ax1] = round(sax1 + j * dax1, 1)
                if ax2:
                    position[ax2] = round(sax2 + i * dax2, 1)
                config = dict(
                    name=str(n),
                    comment='',
                    detoffset=-335.0,
                    thickness=1.0,
                    aperture=(0, 0, 10, 10),
                    position=position,
                )
                self.configs.append(config)

    def _clear_samples(self):
        self.list.clear()
        self.configs.clear()

    @pyqtSlot()
    def on_retrieveBtn_clicked(self):
        sampleconf = self.client.eval('Exp.sample.samples', [])
        sampleconf = sorted(sampleconf.items())
        self.configs = [dict(c[1]) for c in sampleconf if 'thickness' in c[1]]
        # convert read-only dict to normal dict
        for config in self.configs:
            config['position'] = dict(config['position'].items())
        self.list.clear()
        last_item = None
        for config in self.configs:
            last_item = QListWidgetItem(config['name'], self.list)
        # select the last item
        if last_item:
            self.list.setCurrentItem(last_item)

        self.sampleGroup.setEnabled(True)
        self.applyBtn.setEnabled(False)

    @pyqtSlot()
    def on_openFileBtn_clicked(self):
        initial_dir = self.client.eval('session.experiment.scriptpath', '')
        filename = QFileDialog.getOpenFileName(self, 'Open sample file',
                                               initial_dir,
                                               'Sample files (*.py)')[0]
        if not filename:
            return
        try:
            self.configs = parse_sampleconf(filename)
        except Exception as err:
            self.showError(f'Could not read file: {err}\n\n'
                           'Are you sure this is a sample file?')
        else:
            self.list.clear()
            self.sampleGroup.setEnabled(True)
            new_item = None
            for config in self.configs:
                new_item = QListWidgetItem(config['name'], self.list)
            # select the last item
            if new_item:
                self.list.setCurrentItem(new_item)
            self.on_list_itemClicked(new_item)
            self.applyBtn.setEnabled(True)

    @pyqtSlot()
    def on_applyBtn_clicked(self):
        script = self._generate_script()
        self.client.run(script)
        self.showInfo('Sample info has been transferred to the daemon.')
        
        self.applyBtn.setEnabled(False)

    @pyqtSlot()
    def on_saveBtn_clicked(self):
        initial_dir = self.client.eval('session.experiment.scriptpath', '')
        filename = QFileDialog.getSaveFileName(self, 'Save sample file',
                                         initial_dir,
                                         'Sample files (*.py)')[0]
        if not filename:
            return False
        if not filename.endswith('.py'):
            filename += '.py'
        try:
            self._save_script(filename, self._generate_script())
        except Exception as err:
            self.showError(f'Could not write file: {err}')

    def _clearDisplay(self):
        item = self.frame.layout().takeAt(0)
        if item:
            item.widget().deleteLater()

    def on_list_currentItemChanged(self, item):
        self.on_list_itemClicked(item)

    def on_list_itemClicked(self, item):
        self._clearDisplay()
        if not item:
            return
        index = self.list.row(item)
        frm = QFrame(self)
        loadUi(frm, findResource(
            'nicos_ess/loki/gui/ui_files/sampleconf_summary.ui'))
        configToFrame(frm, self.configs[index])
        frm.addDevBtn.setVisible(False)
        frm.delDevBtn.setVisible(False)
        frm.readDevsBtn.setVisible(False)
        frm.posTbl.setEnabled(False)
        relevant_list = [frm.offsetBox, frm.apXBox, frm.apYBox, frm.apWBox,
                         frm.apHBox]
        for box in frm.findChildren(QLineEdit):
            if box in relevant_list:
                box.setEnabled(True)
            else:
                box.setEnabled(False)
        layout = self.frame.layout()
        layout.addWidget(frm)

        # editingFinished signal is fired when LineEdit lose focus.
        # So when Matt switches to Firefox it is fired.
        # Can use returnPressed signal but will require user to press Enter 
        # everytime they change the value. In case they forget to press
        # Enter, the value will not be registered.
        # Good solution will be to make a custom LineEdit which changes
        # color when in editing mode.
        frm.offsetBox.editingFinished.connect(lambda: self.set_offset(index,
                                              frm.offsetBox.displayText()))
        frm.apXBox.editingFinished.connect(lambda: self.set_pos_x(index,
                                           frm.apXBox.displayText()))
        frm.apYBox.editingFinished.connect(lambda: self.set_pos_y(index,
                                           frm.apYBox.displayText()))
        frm.apWBox.editingFinished.connect(lambda: self.set_width_w(index,
                                           frm.apWBox.displayText()))
        frm.apHBox.editingFinished.connect(lambda: self.set_height_h(index,
                                           frm.apHBox.displayText()))

        # Re-validate the values
        for box in [frm.offsetBox, frm.apXBox, frm.apYBox, frm.apWBox,
                    frm.apHBox]:
            box.setValidator(DoubleValidator(self))

    def set_offset(self, index, value):
        if self.configs[index]['detoffset'] == value:
            return
        self.applyBtn.setEnabled(True)
        self.configs[index]['detoffset'] = value
        self._copy_key('detoffset')

    def set_pos_x(self, index, value):
        value = float(value)
        if self.configs[index]['aperture'][0] == value:
            return
        self._set_aperture_value_at_key(index, 0, value)
        
    def set_pos_y(self, index, value):
        value = float(value)
        if self.configs[index]['aperture'][1] == value:
            return
        self._set_aperture_value_at_key(index, 1, value)
    
    def set_width_w(self, index, value):
        value = float(value)
        if self.configs[index]['aperture'][2] == value:
            return
        self._set_aperture_value_at_key(index, 2, value)
    
    def set_height_h(self, index, value):
        value = float(value)
        if self.configs[index]['aperture'][3] == value:
            return
        self._set_aperture_value_at_key(index, 3, value)
    
    def _set_aperture_value_at_key(self, index, key, value):
        self.applyBtn.setEnabled(True)
        container = self.configs[index]['aperture']
        self.configs[index]['aperture'] = \
            container[:key] + (value, ) + container[key+1:]
        self._copy_key('aperture') 

    def on_list_itemDoubleClicked(self):
        self.on_editBtn_clicked()

    @pyqtSlot()
    def on_newBtn_clicked(self):
        dlg = ConfigEditDialog(self, self.client, self.instrument,
                               self.configs)
        if not dlg.exec_():
            return
        self.applyBtn.setEnabled(True)
        config = configFromFrame(dlg.frm)
        self.configs.append(config)
        new_item = QListWidgetItem(config['name'], self.list)
        self.list.setCurrentItem(new_item)

    @pyqtSlot()
    def on_editBtn_clicked(self):
        index = self.list.currentRow()
        if index < 0:
            return
        dlg = ConfigEditDialog(self, self.client, self.instrument,
                               [config for (i, config) in
                                enumerate(self.configs) if i != index],
                               self.configs[index])
        if not dlg.exec_():
            return
        self.applyBtn.setEnabled(True)
        config = configFromFrame(dlg.frm)
        self.configs[index] = config
        list_item = self.list.item(index)
        list_item.setText(config['name'])
        self.on_list_itemClicked(list_item)

    @pyqtSlot()
    def on_delBtn_clicked(self):
        index = self.list.currentRow()
        if index < 0:
            return
        self.applyBtn.setEnabled(True)
        self.list.takeItem(index)
        del self.configs[index]
        if self.list.currentRow() != -1:
            self.on_list_itemClicked(self.list.item(self.list.currentRow()))
        else:
            self._clearDisplay()

    def _copy_key(self, key):
        index = self.list.currentRow()
        if index < 0:
            return
        template = self.configs[index][key]
        for config in self.configs:
            config[key] = template

    def _generate_script(self):
        script = [f'# LoKI sample file for NICOS\n',
                  f'# Written: {time.asctime()}\n\n' ,
                  f'ClearSamples()\n']
        for (i, config) in enumerate(self.configs, start=1):
            script.append(f"SetSample({i}, {repr(config['name'])}, ")
            for key in SAMPLE_KEYS:
                script.append(f"{key}={repr(config[key])}")
                script.append(', ')
            del script[-1]  # remove last comma
            script.append(')\n')
        return ''.join(script)

    @staticmethod
    def _save_script(filename, script):
        with open(filename, 'w') as fp:
            fp.writelines(script)


class MockSample:
    def __init__(self):
        self.reset_called = False
        self.configs = []

    def reset(self):
        self.reset_called = True
        self.configs = []

    def define(self, _num, name, **entry):
        entry['name'] = name
        for key in SAMPLE_KEYS:
            if key not in entry:
                raise ValueError(f'missing key {key} in sample entry')
        self.configs.append(entry)


def parse_sampleconf(filename):
    builtin_ns = vars(builtins).copy()
    for name in ('__import__', 'open', 'exec', 'execfile'):
        builtin_ns.pop(name, None)
    mock_sample = MockSample()
    ns = {'__builtins__': builtin_ns,
          'ClearSamples': mock_sample.reset,
          'SetSample': mock_sample.define}
    with open(filename, 'r') as fp:
        for line in fp.readlines():
            exec(line, ns)
    # The script needs to call this, if it doesn't it is not a sample file.
    if not mock_sample.reset_called:
        raise ValueError('the script never calls ClearSamples()')
    return mock_sample.configs
